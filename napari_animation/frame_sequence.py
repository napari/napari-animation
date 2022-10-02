from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterator, Sequence, Tuple

import numpy as np
from napari.utils.events import EmitterGroup

from .interpolation import (
    Interpolation,
    InterpolationMap,
    interpolate_viewer_state,
)
from .utils import pairwise
from .viewer_state import ViewerState

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
        key_frames.events.inserted.connect(self._rebuild_keyframe_index)
        key_frames.events.removed.connect(self._rebuild_keyframe_index)
        key_frames.events.changed.connect(self._rebuild_keyframe_index)
        key_frames.events.reordered.connect(self._rebuild_keyframe_index)

        self.__current_index = 0
        self.events = EmitterGroup(
            source=self, n_frames=None, _current_index=None
        )

        self.state_interpolation_map: InterpolationMap = {
            "camera.angles": Interpolation.SLERP,
            "camera.zoom": Interpolation.LOG,
        }

        # cache of interpolated viewer states
        self._cache: Dict[int, ViewerState] = {}

        # map of frame number -> (kf0, kf1, fraction)
        self._keyframe_index: Dict[int, Tuple[KeyFrame, KeyFrame, float]] = {}
        self._rebuild_keyframe_index()

    def _rebuild_keyframe_index(self, event=None):
        """Create a map of frame number -> (kf0, kf1, fraction)"""
        self._keyframe_index.clear()
        self._cache.clear()

        n_keyframes = len(self._key_frames)

        if n_keyframes == 0:
            self.events.n_frames(value=len(self))
            return
        elif n_keyframes == 1:
            f = 0
            kf1 = self._key_frames[0]
        else:
            f = 0
            for kf0, kf1 in pairwise(self._key_frames):
                for s in range(kf1.steps):
                    fraction = kf1.ease(s / kf1.steps)
                    self._keyframe_index[f] = (kf0, kf1, fraction)
                    f += 1

        self._keyframe_index[f] = (kf1, kf1, 0)
        self.events.n_frames(value=len(self))

    def __len__(self) -> int:
        """The total frame count of the animation"""
        return len(self._keyframe_index)

    def __getitem__(self, key: int) -> ViewerState:
        """Get the interpolated state at frame `key` in the animation."""
        if key < 0:
            key += len(self)
        if key not in self._cache:
            try:
                kf0, kf1, frac = self._keyframe_index[key]
            except KeyError:
                raise IndexError(
                    f"Frame index ({key}) out of range ({len(self)} frames)"
                )
            if frac == 0:
                self._cache[key] = kf0.viewer_state
            else:
                self._cache[key] = interpolate_viewer_state(
                    kf0.viewer_state,
                    kf1.viewer_state,
                    frac,
                    self.state_interpolation_map,
                )

        return self._cache[key]

    def iter_frames(
        self,
        viewer: napari.viewer.Viewer,
        canvas_only: bool = True,
        scale_factor: float = None,
    ) -> Iterator[np.ndarray]:
        """Iterate over interpolated viewer states, and yield rendered frames."""
        for i, state in enumerate(self):
            frame = state.render(viewer, canvas_only=canvas_only)
            if scale_factor not in (None, 1):
                from scipy import ndimage as ndi

                frame = ndi.zoom(frame, (scale_factor, scale_factor, 1))
                frame = frame.astype(np.uint8)
            yield frame

    def set_movie_frame_index(self, viewer: napari.viewer.Viewer, index: int):
        self[index].apply(viewer)
        self._current_index = index

    @property
    def _current_index(self):
        return self.__current_index

    @_current_index.setter
    def _current_index(self, frame_index):
        if frame_index != self._keyframe_index:
            self.__current_index = frame_index
            self.events._current_index(value=frame_index)
