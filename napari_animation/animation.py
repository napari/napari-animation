import os
from itertools import count
from pathlib import Path

import imageio
from napari.utils.io import imsave

from .easing import Easing
from .frame_sequence import FrameSequence
from .key_frame import KeyFrame, KeyFrameList


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
    """

    def __init__(self, viewer):
        self.viewer = viewer

        self.key_frames = KeyFrameList()
        self.key_frames.selection.events._current.connect(
            self._on_current_keyframe_changed
        )
        self._keyframe_counter = count()  # track number of frames created

        self._frames = FrameSequence(self.key_frames)

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

    def set_movie_frame_index(self, frame: int):
        """Set state to a specific frame in the final movie."""
        try:
            self._frames[frame].apply(self.viewer)
        except KeyError:
            return

        with self.key_frames.selection.events._current.blocker():
            frame = self._frames._frame_index[frame][0]
            self.key_frames.selection.active = frame

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
        frames = self._frames.iter_frames(
            self.viewer, canvas_only, scale_factor
        )
        n_frames = len(self._frames)
        # save frames
        for ind, frame in enumerate(frames):
            print("Rendering frame ", ind + 1, "of", n_frames)
            if not save_as_folder:
                writer.append_data(frame)
            else:
                fname = folder_path / (path_obj.stem + "_" + str(ind) + ".png")
                imsave(fname, frame)

        if not save_as_folder:
            writer.close()

    def _on_current_keyframe_changed(self, event):
        if event.value:
            event.value.viewer_state.apply(self.viewer)
