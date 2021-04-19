import os
from copy import deepcopy
from pathlib import Path

import imageio
import numpy as np
from scipy import ndimage as ndi

from napari.layers.utils.layer_utils import convert_to_uint8
from napari.utils.events import EventedList
from napari.utils.io import imsave
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

        self.key_frames = EventedList()
        self.frame = -1

    def capture_keyframe(self, steps=30, ease=None, insert=True, frame=None):
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
        frame : int, optional
            If provided use this value for frame rather than current frame number.
        """
        if frame is not None:
            self.frame = frame

        new_state = {
            'viewer': self._get_viewer_state(),
            'thumbnail': self._generate_thumbnail(),
            'steps': steps,
            'ease': ease,
        }

        if insert or self.frame == -1:
            self.key_frames.insert(self.frame + 1, new_state)
            self.frame += 1
        else:
            self.key_frames[self.frame] = new_state

    @property
    def n_frames(self):
        """The total frame count of the animation
        """
        if len(self.key_frames) >= 2:
            return np.sum([f["steps"] for f in self.key_frames[1:]]) + 1
        else:
            return 0

    def set_to_keyframe(self, frame):
        """Set the viewer to a given key-frame

        Parameters
        -------
        frame : int
            Key-frame to visualize
        """
        self.frame = frame
        if len(self.key_frames) > 0 and self.frame > -1:
            self._set_viewer_state(self.key_frames[frame]['viewer'])

    def set_to_current_keyframe(self):
        """Set the viewer to the current key-frame
        """
        self._set_viewer_state(self.key_frames[self.frame]['viewer'])

    def _get_viewer_state(self):
        """Capture current viewer state

        Returns
        -------
        new_state : dict
            Description of viewer state.
        """

        new_state = {
            'camera': self.viewer.camera.dict(),
            'dims': self.viewer.dims.dict(),
            'layers': self._get_layer_state(),
        }

        # Log transform zoom for linear interpolation
        new_state['camera']['zoom'] = np.log10(new_state['camera']['zoom'])
        return new_state

    def _set_viewer_state(self, state):
        """Sets the current viewer state

        Parameters
        ----------
        state : dict
            Description of viewer state.
        """
        # Undo log transform zoom for linear interpolation
        camera_state = deepcopy(state['camera'])
        camera_state['zoom'] = np.power(10, camera_state['zoom'])

        self.viewer.camera.update(camera_state)
        self.viewer.dims.update(state['dims'])
        self._set_layer_state(state['layers'])

    def _get_layer_state(self):
        """Store layer state in a dict of dicts {layer.name: state}
        """
        layer_state = {
            layer.name: layer._get_base_state() for layer in self.viewer.layers
        }
        # remove metadata from layer_state dicts
        for state in layer_state.values():
            state.pop('metadata')
        return layer_state

    def _set_layer_state(self, layer_state):
        for layer_name, layer_state in layer_state.items():
            layer = self.viewer.layers[layer_name]
            for key, value in layer_state.items():
                setattr(layer, key, value)

    def _state_generator(self):
        self._validate_animation()
        # iterate over and interpolate between pairs of key-frames
        for current_frame, next_frame in zip(self.key_frames, self.key_frames[1:]):
            # capture necessary info for interpolation
            initial_state = current_frame["viewer"]
            final_state = next_frame["viewer"]
            interpolation_steps = next_frame["steps"]
            ease = next_frame["ease"]

            # generate intermediate states between key-frames
            for interp in range(interpolation_steps):
                fraction = interp / interpolation_steps
                if ease is not None:
                    fraction = ease(fraction)
                state = interpolate_state(initial_state, final_state, fraction)
                yield state

        # be sure to include the final state
        yield final_state

    def _validate_animation(self):
        if len(self.key_frames) < 2:
            raise ValueError(f'Must have at least 2 key frames, received {len(self.key_frames)}')

    def _frame_generator(self, canvas_only=True):
        for i, state in enumerate(self._state_generator()):
            print('Rendering frame ', i + 1, 'of', self.n_frames)
            self._set_viewer_state(state)
            frame = self.viewer.screenshot(canvas_only=canvas_only)
            yield frame

    def _generate_thumbnail(self):
        """generate a thumbnail from viewer
        """
        screenshot = self.viewer.screenshot(canvas_only=True)
        thumbnail = self._coerce_image_into_thumbnail_shape(screenshot)
        return thumbnail

    def _coerce_image_into_thumbnail_shape(self, image):
        """Resizes an image to self._thumbnail_shape with padding
        """
        scale_factor = np.min(
            np.divide(self._thumbnail_shape, image.shape)
        )
        intermediate_image = ndi.zoom(image, (scale_factor, scale_factor, 1))

        padding_needed = np.subtract(self._thumbnail_shape, intermediate_image.shape)
        pad_amounts = [(p // 2, (p + 1) // 2) for p in padding_needed]
        thumbnail = np.pad(intermediate_image, pad_amounts, mode='constant')
        thumbnail = convert_to_uint8(thumbnail)

        # blend thumbnail with opaque black background
        background = np.zeros(self._thumbnail_shape, dtype=np.uint8)
        background[..., 3] = 255

        f_dest = thumbnail[..., 3][..., None] / 255
        f_source = 1 - f_dest
        thumbnail = thumbnail * f_dest + background * f_source
        return thumbnail.astype(np.uint8)

    @property
    def _thumbnail_shape(self):
        return (32, 32, 4)

    @property
    def current_key_frame(self):
        return self.key_frames[self.frame]

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
            The format to use to write the file. By default imageio selects the appropriate for you based on the filename.
        canvas_only : bool
            If True include just includes the canvas, otherwise include the full napari viewer.
        scale_factor : float
            Rescaling factor for the image size. Only used without
            viewer (with_viewer = False).
        """
        self._validate_animation()

        # create a frame generator
        frame_gen = self._frame_generator(canvas_only=canvas_only)

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
                if path_obj.suffix in ['mov', 'avi', 'mpg', 'mpeg', 'mp4', 'mkv', 'wmv']:
                    writer = imageio.get_writer(
                        path, fps=fps, quality=quality, format=format,
                    )
                else:
                    writer = imageio.get_writer(path, fps=fps, format=format)
            except ValueError as err:
                print(err)
                print('Your file will be saved as a series of PNG files')
                save_as_folder = True

        if save_as_folder:
            # if movie is saved as series of PNG, create a folder
            if folder_path.is_dir():
                for f in folder_path.glob('*.png'):
                    os.remove(f)
            else:
                folder_path.mkdir(exist_ok=True)

        # save frames
        for ind, frame in enumerate(frame_gen):
            if scale_factor is not None:
                frame = ndi.zoom(frame, (scale_factor, scale_factor, 1))
                frame = frame.astype(np.uint8)
            if not save_as_folder:
                writer.append_data(frame)
            else:
                fname = folder_path / (path_obj.stem + '_' + str(ind) + '.png')
                imsave(fname, frame)

        if not save_as_folder:
            writer.close()
