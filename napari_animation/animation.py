import os
from itertools import count
from pathlib import Path
from time import sleep

import imageio
import numpy as np
from napari.utils.io import imsave
from tqdm import tqdm

from napari_animation.easing import Easing

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
    key_frames : list of KeyFrame
        List of key-frames in the animation.
    """

    def __init__(self, viewer):
        self.viewer = viewer

        self.key_frames = KeyFrameList()

        self.key_frames.events.removed.connect(self._on_keyframe_removed)

        self.key_frames.events.changed.connect(self._on_keyframe_changed)

        self.key_frames.selection.events.active.connect(
            self._on_active_keyframe_changed
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
            active_keyframe = self.key_frames.selection.active
            if active_keyframe:
                position = self.key_frames.index(active_keyframe)
            else:
                if insert:
                    position = -1
                else:
                    raise ValueError("No selected keyframe to replace !")

        new_frame = KeyFrame.from_viewer(self.viewer, steps=steps, ease=ease)
        new_frame.name = f"Key Frame {next(self._keyframe_counter)}"

        if insert:
            self.key_frames.insert(position + 1, new_frame)
        else:
            self.key_frames[position] = new_frame

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
        frame_index = self._keyframe_frame_index(index)
        self.set_movie_frame_index(frame_index)

    def set_movie_frame_index(self, index: int):
        """Set state to a specific frame in the final movie."""
        try:
            if index < 0:
                index += len(self._frames)

            key_frame = self._frames._keyframe_index[index][0]

            # to prevent active callback again
            if self.key_frames.selection.active != key_frame:
                self.key_frames.selection.active = key_frame

            self._frames.set_movie_frame_index(self.viewer, index)
            self._current_frame = index

        except KeyError:
            return

    def animate(
        self,
        filename,
        fps=20,
        quality=5,
        format=None,
        canvas_only=True,
        scale_factor=None,
    ):
        """Create a movie based on key-frames
        Parameters
        -------
        filename : str
            path to use for saving the movie (can also be a path). Extension
            should be one of .gif, .mp4, .mov, .avi, .mpg, .mpeg, .mkv, .wmv
            If no extension is provided, images are saved as a folder of PNGs
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
        file_path = Path(filename)
        folder_path = file_path.absolute().parent.joinpath(file_path.stem)

        # if path has no extension, save as fold of PNG
        save_as_folder = False
        if file_path.suffix == "":
            save_as_folder = True

        # try to create an ffmpeg writer. If not installed default to folder creation
        if save_as_folder is False:
            try:
                # create imageio writer. Handle separately imageio-ffmpeg extensions and
                # gif extension which doesn't accept the quality parameter.
                if file_path.suffix in [
                    ".mov",
                    ".avi",
                    ".mpg",
                    ".mpeg",
                    ".mp4",
                    ".mkv",
                    ".wmv",
                ]:
                    writer = imageio.get_writer(
                        filename,
                        fps=fps,
                        quality=quality,
                        format=format,
                    )
                else:
                    writer = imageio.get_writer(
                        filename, fps=fps, format=format
                    )
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
        frame_generator = self._frames.iter_frames(
            self.viewer, canvas_only, scale_factor
        )
        n_frames = len(self._frames)

        # Render frames (with a progress bar)
        print("Rendering frames...")
        sleep(0.05)
        with tqdm(total=n_frames) as pbar:
            for frame_index, image in enumerate(frame_generator):
                if save_as_folder is True:
                    frame_filename = (
                        folder_path / f"{file_path.stem}_{frame_index:06d}.png"
                    )
                    imsave(frame_filename, image)
                else:
                    writer.append_data(image)
                pbar.update(1)
        if not save_as_folder:
            writer.close()

    def _keyframe_frame_index(self, keyframe_index):
        """Gets the frame index of the keyframe corresponding to keyframe_index."""
        # Get all steps leading to keyframe.
        steps_to_keyframe = [
            kf.steps for kf in self.key_frames[1 : keyframe_index + 1]
        ]
        frame_index = np.sum(steps_to_keyframe) if steps_to_keyframe else 0
        return int(frame_index)

    def _on_keyframe_removed(self, event):
        self.key_frames.selection.active = None

    def _on_keyframe_changed(self, event):
        self.key_frames.selection.active = event.value

    def _on_active_keyframe_changed(self, event):
        active_keyframe = event.value
        if active_keyframe:
            keyframe_index = self.key_frames.index(active_keyframe)
            self.set_key_frame_index(keyframe_index)
