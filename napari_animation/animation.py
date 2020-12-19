import imageio
import copy
import skimage.transform
import skimage.io
import numpy as np
from pathlib import Path

from .utils import interpolate_state


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
    """
    def __init__(self, viewer):
        self.viewer = viewer

        self.key_frames = []
        self.frame = -1

        # establish key bindings
        self._add_callback()

    def finish_movie(self):
        self.release_callbacks()

    def _add_callback(self):
        """Bind keys"""

        self.viewer.bind_key("Alt-f", self._capture_keyframe_callback)
        self.viewer.bind_key("Alt-r", self._replace_keyframe_callback)
        self.viewer.bind_key("Alt-d", self._delete_keyframe_callback)

        self.viewer.bind_key("Alt-a", self._key_adv_frame)
        self.viewer.bind_key("Alt-b", self._key_back_frame)

    def _release_callbacks(self):
        """Release keys"""

        self.viewer.bind_key("Alt-f", None)
        self.viewer.bind_key("Alt-r", None)
        self.viewer.bind_key("Alt-d", None)

        self.viewer.bind_key("Alt-a", None)
        self.viewer.bind_key("Alt-b", None)

    def get_state(self):
        """Capture current viewer state

        Returns
        -------
        new_state : dict
            Description of viewer state.
        """

        new_state = {
            "camera": self.viewer.camera.asdict(),
            "dims": self.viewer.dims.asdict(),
        }

        return new_state

    def set_state(self, state):
        """Sets the current viewer state

        Parameters
        ----------
        state : dict
            Description of viewer state.
        """        
        self.viewer.camera.update(state['camera'])
        self.viewer.dims.update(state['dims'])

    def _capture_keyframe_callback(self, viewer):
        """Record current key-frame"""

        print('capture', self.frame, ' of ', len(self.key_frames) + 1)
        new_state = self.get_state()
        self.key_frames.insert(self.frame + 1, new_state)
        self.frame += 1
        print('current frame', self.frame)

    def _replace_keyframe_callback(self, viewer):
        """Replace current key-frame with new view"""

        new_state = self.get_state()
        self.key_frames[self.frame] = new_state
        print('current frame', self.frame)

    def _delete_keyframe_callback(self, viewer):
        """Delete current key-frame"""

        self.key_frames.pop(self.frame)
        self.frame = (self.frame - 1) % len(self.key_frames)
        self._set_to_keyframe(self.frame)
        print('current frame', self.frame)

    def _set_to_keyframe(self, frame):
        """Set the viewer to a given key-frame

        Parameters
        -------
        frame : int
            key-frame to visualize
        """
        self.frame = frame
        if len(self.key_frames) > 0 and self.frame > -1:
            self.set_state(self.key_frames[frame])

    def _key_adv_frame(self, viewer):
        """Go forwards in key-frame list"""

        new_frame = (self.frame + 1) % len(self.key_frames)
        self._set_to_keyframe(new_frame)
        print('current frame', self.frame)

    def _key_back_frame(self, viewer):
        """Go backwards in key-frame list"""

        new_frame = (self.frame - 1) % len(self.key_frames)
        self._set_to_keyframe(new_frame)
        print('current frame', self.frame)

    def _state_generator(self, interpolation_steps=15):
        if len(self.key_frames) < 2:
            raise ValueError(f'Must have at least 2 key frames, recieved {len(self.key_frames)}')

        for frame in range(len(self.key_frames) - 1):
            for interp in range(interpolation_steps):
                fraction = interp / interpolation_steps
                state = interpolate_state(self.key_frames[frame], self.key_frames[frame + 1], fraction)
                print('qq', frame, interp, fraction, state['camera'])
                yield state

    def _frame_generator(self, interpolation_steps=15, canvas_only=True):
        for state in self._state_generator(interpolation_steps=interpolation_steps):
            self.set_state(state)
            frame = self.viewer.screenshot(canvas_only=canvas_only)            
            yield frame

    def animate(
        self,
        name="movie.mp4",
        interpolation_steps=15,
        fps=20,
        quality=5,
        format=None,
        canvas_only=True,
        scale_factor=None,
    ):
        """Create a movie based on key-frames

        Parameters
        -------
        name : str
            name to use for saving the movie (can also be a path)
            should be either .mp4 or .gif. If no extension is provided,
            images are saved as a folder of PNGs
        interpolation_steps : int
            Number of steps for interpolation.
        fps : int
            frames per second
        quality: float
            number from 1 (lowest quality) to 9
            only applies to mp4
        format: str
            The format to use to write the file. By default imageio selects the appropriate for you based on the filename.
        canvas_only : bool
            If True include just includes the canvas, otherwise include the full napari viewer.
        scale_factor : float
            Rescaling factor for the image size. Only used without
            viewer (with_viewer = False).
        """

        # create a frame generator
        frame_gen = self._frame_generator(interpolation_steps=interpolation_steps, canvas_only=canvas_only)

        # create path object
        path = Path(name)

        # if path has no extension, save as fold of PNG
        save_as_folder = False
        if path.suffix == "":
            save_as_folder = True

        # try to create an ffmpeg writer. If not installed default to folder creation
        if not save_as_folder:
            try:
                # create imageio writer and add all frames
                if quality is not None:
                    writer = imageio.get_writer(
                        name, fps=fps, quality=quality, format=format,
                    )
                else:
                    writer = imageio.get_writer(name, fps=fps, format=format)
            except ImportError as err:
                print(err)
                print('Your movie will be saved as a series of PNG files.')
                save_as_folder = True

        # if movie is saved as series of PNG, create a folder
        if save_as_folder:
            folder_path = path.absolute()
            folder_path = path.parent.joinpath(path.stem)
            folder_path.mkdir(exist_ok=True)

        # save frames
        for ind, frame in enumerate(frame_gen):
            if scale_factor is not None:
                frame = skimage.transform.rescale(
                    frame, scale_factor, multichannel=True, preserve_range=True
                )
                frame = frame.astype(np.uint8)
            if not save_as_folder:
                writer.append_data(frame)
            else:
                skimage.io.imsave(
                    folder_path.joinpath(path.stem + '_' + str(ind) + '.png'),
                    frame,
                )

        if not save_as_folder:
            writer.close()