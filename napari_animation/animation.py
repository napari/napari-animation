import os
from dataclasses import asdict
from itertools import count
from pathlib import Path
from typing import Dict, Iterator, Sequence, Tuple

import imageio
import numpy as np
from napari.utils.events import EmitterGroup, SelectableEventedList
from napari.utils.io import imsave
from scipy import ndimage as ndi

from .easing import Easing
from .interpolation import Interpolation
from .key_frame import KeyFrame, ViewerState
from .utils import pairwise


class AnimationGenerator(Sequence[ViewerState]):
    def __init__(self, key_frames: SelectableEventedList[KeyFrame]) -> None:
        super().__init__()
        self.key_frames = key_frames
        key_frames.events.inserted.connect(self._update_keyframe_map)
        key_frames.events.removed.connect(self._update_keyframe_map)
        key_frames.events.changed.connect(self._update_keyframe_map)
        key_frames.events.reordered.connect(self._update_keyframe_map)

        self.events = EmitterGroup(source=self, n_frames=None)

        self.state_interpolation_map = {
            "camera.angles": Interpolation.SLERP,
            "camera.zoom": Interpolation.LOG,
        }

        # cache of interpolated viewer states
        self._cache: Dict[int, ViewerState] = {}
        # map of frame number -> (kf0, kf1, fraction)
        self._keyframe_map: Dict[int, Tuple[KeyFrame, KeyFrame, float]] = {}
        self._update_keyframe_map()

    def _update_keyframe_map(self, event=None):
        """Create a map of frame number -> (kf0, kf1, fraction)"""
        self._keyframe_map.clear()
        self._cache.clear()
        if len(self.key_frames) < 2:
            self.events.n_frames(value=len(self))
            return

        f = 0
        for kf0, kf1 in pairwise(self.key_frames):
            for s in range(kf1.steps):
                fraction = s / kf1.steps
                self._keyframe_map[f] = (kf0, kf1, fraction)
                f += 1
        self._keyframe_map[f] = (kf1, kf1, 0)
        self.events.n_frames(value=len(self))

    def __len__(self) -> int:
        """The total frame count of the animation"""
        return len(self._keyframe_map)

    def __getitem__(self, key: int) -> ViewerState:
        """Get the interpolated state at frame `key` in the animation."""
        if key not in self._cache:
            kf0, kf1, frac = self._keyframe_map[key]
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
        fraction,
        state_interpolation_map=None,
    ):
        """Interpolate a state between two states

        Parameters
        ----------
        initial_state : dict
            Description of initial viewer state.
        final_state : dict
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

        if state_interpolation_map is None:
            state_interpolation_map = self.state_interpolation_map

        state = {}
        separator = "."

        from_state = asdict(from_state)
        to_state = asdict(to_state)

        for keys in keys_to_list(from_state):
            v0 = nested_get(from_state, keys)
            v1 = nested_get(to_state, keys)

            property_string = separator.join(keys)

            if property_string in state_interpolation_map.keys():
                interpolation_func = state_interpolation_map[property_string]
            else:
                interpolation_func = Interpolation.DEFAULT

            nested_set(state, keys, interpolation_func(v0, v1, fraction))

        return ViewerState(**state)

    def iter_frames(self, viewer, canvas_only=True) -> Iterator[np.ndarray]:
        n_frames = len(self)
        for i, state in enumerate(self):
            print("Rendering frame ", i + 1, "of", n_frames)
            state.apply_to_viewer(viewer)
            yield viewer.screenshot(canvas_only=canvas_only)


class Animation:
    """Make animations using the napari viewer.

    Parameters
    ----------
    viewer : napari.Viewer
        napari viewer.

    Attributes
    ----------
    key_frames : list of dict
        List of viewer state dictionaries.
    frame : int
        Currently shown key frame.
    state_interpolation_map : dict
        Dictionary relating state attributes to interpolation functions.
    """

    def __init__(self, viewer):
        self.viewer = viewer

        self.key_frames: SelectableEventedList[
            KeyFrame
        ] = SelectableEventedList(basetype=KeyFrame)
        self.key_frames.selection.events._current.connect(
            self._on_current_keyframe_changed
        )
        self._generator = AnimationGenerator(self.key_frames)
        self._keyframe_counter = count()  # track number of frames created

    def capture_keyframe(
        self, steps=15, ease=Easing.LINEAR, insert=True, position: int = None
    ):
        """Record current key-frame

        Parameters
        ----------
        steps : int
            Number of interpolation steps between last keyframe and captured one.
        ease : callable, optional
            If provided this method should make from `[0, 1]` to `[0, 1]` and will
            be used as an easing function for the transition between the last state
            and captured one.
        insert : bool
            If captured key-frame should insert into current list or replace the current
            keyframe.
        position : int, optional
            If provided, place new frame at this index. By default, inserts at current
            active frame.
        """
        if position is None:
            position = (
                self.key_frames.index(self.current_key_frame)
                if self.current_key_frame
                else -1
            )

        new_frame = KeyFrame.from_viewer(self.viewer, steps=steps, ease=ease)
        new_frame.name = f"Key Frame {next(self._keyframe_counter)}"

        if insert:
            self.key_frames.insert(position + 1, new_frame)
        else:
            del self.key_frames[position]  # needed to trigger the remove event
            self.key_frames.insert(position, new_frame)

    def set_to_keyframe(self, frame: int):
        """Set the viewer to a given key-frame

        Parameters
        ----------
        frame : int
            Key-frame index to visualize
        """
        self.key_frames.selection.active = self.key_frames[frame]

    def _validate_animation(self):
        if len(self.key_frames) < 2:
            raise ValueError(
                f"Must have at least 2 key frames, received {len(self.key_frames)}"
            )

    def set_key_frame_index(self, index: int):
        self.key_frames.selection.active = self.key_frames[index]

    @property
    def current_key_frame(self):
        return self.key_frames.selection._current

    def animate(
        self,
        path,
        fps=20,
        quality=5,
        format=None,
        canvas_only=True,
        scale_factor=None,
    ):
        """Create a movie based on key-frames
        Parameters
        -------
        path : str
            path to use for saving the movie (can also be a path). Extension
            should be one of .gif, .mp4, .mov, .avi, .mpg, .mpeg, .mkv, .wmv
            If no extension is provided, images are saved as a folder of PNGs
        interpolation_steps : int
            Number of steps for interpolation.
        fps : int
            frames per second
        quality: float
            number from 1 (lowest quality) to 9
            only applies to non-gif extensions
        format: str
            The format to use to write the file. By default imageio selects the appropriate
            for you based on the filename.
        canvas_only : bool
            If True include just includes the canvas, otherwise include the full napari
            viewer.
        scale_factor : float
            Rescaling factor for the image size. Only used without
            viewer (with_viewer = False).
        """
        self._validate_animation()

        # create path object
        path_obj = Path(path)
        folder_path = path_obj.absolute().parent.joinpath(path_obj.stem)

        # if path has no extension, save as fold of PNG
        save_as_folder = False
        if path_obj.suffix == "":
            save_as_folder = True

        # try to create an ffmpeg writer. If not installed default to folder creation
        if not save_as_folder:
            try:
                # create imageio writer. Handle separately imageio-ffmpeg extensions and
                # gif extension which doesn't accept the quality parameter.
                if path_obj.suffix in [
                    ".mov",
                    ".avi",
                    ".mpg",
                    ".mpeg",
                    ".mp4",
                    ".mkv",
                    ".wmv",
                ]:
                    writer = imageio.get_writer(
                        path,
                        fps=fps,
                        quality=quality,
                        format=format,
                    )
                else:
                    writer = imageio.get_writer(path, fps=fps, format=format)
            except ValueError as err:
                print(err)
                print("Your file will be saved as a series of PNG files")
                save_as_folder = True

        if save_as_folder:
            # if movie is saved as series of PNG, create a folder
            if folder_path.is_dir():
                for f in folder_path.glob("*.png"):
                    os.remove(f)
            else:
                folder_path.mkdir(exist_ok=True)

        # create a frame generator
        frames = self._generator.iter_frames(self.viewer, canvas_only)
        # save frames
        for ind, frame in enumerate(frames):
            if scale_factor is not None:
                frame = ndi.zoom(frame, (scale_factor, scale_factor, 1))
                frame = frame.astype(np.uint8)
            if not save_as_folder:
                writer.append_data(frame)
            else:
                fname = folder_path / (path_obj.stem + "_" + str(ind) + ".png")
                imsave(fname, frame)

        if not save_as_folder:
            writer.close()

    def _on_current_keyframe_changed(self, event):
        if event.value:
            event.value.viewer_state.apply_to_viewer(self.viewer)

    def set_movie_frame(self, frame: int):
        """Set state to a specific frame in the final movie."""
        try:
            self._generator[frame].apply_to_viewer(self.viewer)
        except KeyError:
            return

        with self.key_frames.selection.events._current.blocker():
            frame = self._generator._keyframe_map[frame][0]
            self.key_frames.selection.active = frame
