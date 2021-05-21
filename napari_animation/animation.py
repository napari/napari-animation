import os
from dataclasses import asdict
from itertools import count
from pathlib import Path
from typing import Iterator

import imageio
import numpy as np
from napari.utils.events import SelectableEventedList
from napari.utils.io import imsave
from scipy import ndimage as ndi

from .easing import Easing
from .interpolation import Interpolation, interpolate_state
from .key_frame import KeyFrame, ViewerState


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

        self.state_interpolation_map = {
            "camera.angles": Interpolation.SLERP,
            "camera.zoom": Interpolation.LOG,
        }
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

    @property
    def n_frames(self):
        """The total frame count of the animation"""
        if len(self.key_frames) >= 2:
            return np.sum([f.steps for f in self.key_frames[1:]]) + 1
        else:
            return 0

    def set_to_keyframe(self, frame: int):
        """Set the viewer to a given key-frame

        Parameters
        ----------
        frame : int
            Key-frame index to visualize
        """
        self.key_frames.selection.active = self.key_frames[frame]

    def _set_viewer_state(self, state: ViewerState):
        """Sets the current viewer state
        Parameters
        ----------
        state : dict
            Description of viewer state.
        """
        self.viewer.camera.update(state.camera)
        self.viewer.dims.update(state.dims)
        self._set_layer_state(state.layers)

    def _set_layer_state(self, layer_state: dict):
        for layer_name, layer_state in layer_state.items():
            layer = self.viewer.layers[layer_name]
            for key, value in layer_state.items():
                original_value = getattr(layer, key)
                # Only set if value differs to avoid expensive redraws
                if not np.array_equal(original_value, value):
                    setattr(layer, key, value)

    def _state_generator(self) -> Iterator[ViewerState]:
        self._validate_animation()
        # iterate over and interpolate between pairs of key-frames
        for current_frame, next_frame in zip(
            self.key_frames, self.key_frames[1:]
        ):
            # capture necessary info for interpolation
            initial_state = current_frame.viewer_state
            final_state = next_frame.viewer_state
            interpolation_steps = next_frame.steps
            ease = next_frame.ease

            # generate intermediate states between key-frames
            for interp in range(interpolation_steps):
                fraction = interp / interpolation_steps
                fraction = ease(fraction)
                state = interpolate_state(
                    asdict(initial_state),
                    asdict(final_state),
                    fraction,
                    self.state_interpolation_map,
                )
                yield ViewerState(**state)

        # be sure to include the final state
        yield final_state

    def _validate_animation(self):
        if len(self.key_frames) < 2:
            raise ValueError(
                f"Must have at least 2 key frames, received {len(self.key_frames)}"
            )

    def _frame_generator(self, canvas_only=True) -> Iterator[np.ndarray]:
        for i, state in enumerate(self._state_generator()):
            print("Rendering frame ", i + 1, "of", self.n_frames)
            self._set_viewer_state(state)
            frame = self.viewer.screenshot(canvas_only=canvas_only)
            yield frame

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
        frames = self._frame_generator(canvas_only=canvas_only)
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
            self._set_viewer_state(event.value.viewer_state)
