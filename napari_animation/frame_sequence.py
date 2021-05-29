from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Dict, Iterator, Optional, Sequence, Tuple

import numpy as np
from napari.utils.events import EmitterGroup

from .interpolation import Interpolation, InterpolationMap
from .key_frame import ViewerState
from .utils import pairwise

if TYPE_CHECKING:
    import napari

    from .key_frame import KeyFrame, KeyFrameList


class FrameSequence(Sequence[ViewerState]):
    """Final sequence of of rendered animation frames, based on keyframes.

    This object acts like an immutable sequence of frames, interpolated from
    a sequence of (mutable) KeyFrames.  It can be indexed at any (valid) frame
    in the animation, and will inteprolate (and cache) viewer state on demand.

    If the KeyFrameList changes in any way, the cache is cleared.

    Parameters
    ----------
    key_frames : KeyFrameList
        A KeyFrameList from which to render the final frame sequence.
    """

    def __init__(self, key_frames: KeyFrameList) -> None:
        super().__init__()
        self._key_frames = key_frames
        key_frames.events.inserted.connect(self._rebuild_frame_index)
        key_frames.events.removed.connect(self._rebuild_frame_index)
        key_frames.events.changed.connect(self._rebuild_frame_index)
        key_frames.events.reordered.connect(self._rebuild_frame_index)

        self.events = EmitterGroup(source=self, n_frames=None)

        self.state_interpolation_map: InterpolationMap = {
            "camera.angles": Interpolation.SLERP,
            "camera.zoom": Interpolation.LOG,
        }

        # cache of interpolated viewer states
        self._cache: Dict[int, ViewerState] = {}

        # map of frame number -> (kf0, kf1, fraction)
        self._frame_index: Dict[int, Tuple[KeyFrame, KeyFrame, float]] = {}
        self._rebuild_frame_index()

    def _rebuild_frame_index(self, event=None):
        """Create a map of frame number -> (kf0, kf1, fraction)"""
        self._frame_index.clear()
        self._cache.clear()
        if len(self._key_frames) < 2:
            self.events.n_frames(value=len(self))
            return

        f = 0
        for kf0, kf1 in pairwise(self._key_frames):
            for s in range(kf1.steps):
                fraction = s / kf1.steps
                self._frame_index[f] = (kf0, kf1, fraction)
                f += 1
        self._frame_index[f] = (kf1, kf1, 0)
        self.events.n_frames(value=len(self))

    def __len__(self) -> int:
        """The total frame count of the animation"""
        return len(self._frame_index)

    def __getitem__(self, key: int) -> ViewerState:
        """Get the interpolated state at frame `key` in the animation."""
        if key < 0:
            key += len(self)
        if key not in self._cache:
            try:
                kf0, kf1, frac = self._frame_index[key]
            except KeyError:
                raise IndexError(
                    f"Frame index ({key}) out of range ({len(self)} frames)"
                )
            if frac == 0:
                self._cache[key] = kf0.viewer_state
            else:
                self._cache[key] = self._interpolate_state(
                    kf0.viewer_state,
                    kf1.viewer_state,
                    frac,
                    self.state_interpolation_map,
                )

        return self._cache[key]

    def _interpolate_state(
        self,
        from_state: ViewerState,
        to_state: ViewerState,
        fraction: float,
        state_interpolation_map: Optional[InterpolationMap] = None,
    ):
        """Interpolate a state between two states

        Parameters
        ----------
        from_state : ViewerState
            Description of initial viewer state.
        to_state : ViewerState
            Description of final viewer state.
        fraction : float
            Interpolation fraction, must be between `0` and `1`.
            A value of `0` will return the initial state. A
            value of `1` will return the final state.
        state_interpolation_map : dict
            Dictionary relating state attributes to interpolation functions.

        Returns
        -------
        state : dict
            Description of viewer state.
        """
        from .utils import keys_to_list, nested_get, nested_set

        interp_map = state_interpolation_map or self.state_interpolation_map

        state = {}
        sep = "."

        from_state = asdict(from_state)
        to_state = asdict(to_state)

        for keys in keys_to_list(from_state):
            v0 = nested_get(from_state, keys)
            v1 = nested_get(to_state, keys)

            interp_func = interp_map.get(sep.join(keys), Interpolation.DEFAULT)

            nested_set(state, keys, interp_func(v0, v1, fraction))

        return ViewerState(**state)

    def iter_frames(
        self,
        viewer: napari.viewer.Viewer,
        canvas_only: bool = True,
        scale_factor: float = None,
    ) -> Iterator[np.ndarray]:
        """Iterate over interpolated viewer states, and yield rendered frames."""
        for i, state in enumerate(self):
            frame = state.render(viewer, canvas_only=canvas_only)

            if scale_factor is not None:
                from scipy import ndimage as ndi

                frame = ndi.zoom(frame, (scale_factor, scale_factor, 1))
                frame = frame.astype(np.uint8)
            yield frame
