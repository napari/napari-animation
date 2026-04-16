from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from qt_animation_timeline import (
    AnimationTimelineWidget as _AnimationTimelineWidget,
)
from qt_animation_timeline import PlayMode
from qtpy.QtWidgets import QGridLayout, QLabel, QPushButton, QSpinBox, QWidget

if TYPE_CHECKING:
    import napari

# centralized whitelisted set of track options.
# Each key: value pair is in the form:
#     TrackName: 'attribute_path_from_source_model
_VIEWER_TRACK_OPTIONS = {
    'ndisplay': 'dims.ndisplay',
    'dims slider': 'dims.point',
    'dims margins': 'dims.thickness',
    'dims ': 'dims.current_step',
    'view direction': 'camera.angles',
    'zoom': 'camera.zoom',
    'dims': 'dims',
    'camera': 'camera',
}

# {layer_name} will be replaced by the actual name
_LAYER_TRACK_OPTIONS = {
    '{layer_name} - visibility': 'visible',
    '{layer_name} - opacity': 'opacity',
    '{layer_name} - blending': 'blending',
    '{layer_name} - transform': '_transforms',
    '{layer_name} - clipping planes': 'experimental_clipping_planes',
}


def _resolve_attr_path(source: Any, path: str) -> tuple[Any, str]:
    while True:
        attr, _, path = path.partition('.')
        if not path:
            return source, attr
        source = getattr(source, attr)


class AnimationTimelineWidget(QWidget):
    def __init__(self, viewer: napari.viewer.ViewerModel):
        self.viewer = viewer

        self.viewer_track_options = {
            name: _resolve_attr_path(viewer, attr_path)
            for (name, attr_path) in _VIEWER_TRACK_OPTIONS.items()
        }
        # add viewer itself as a whole
        self.viewer_track_options['viewer'] = (viewer, '')

        self.layer_track_options = {}
        self.custom_track_options = {}

        super().__init__()

        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 600)
        self.duration_label = QLabel()
        self.save_btn = QPushButton('Save animation...')
        self.timeline = _AnimationTimelineWidget(
            track_options=self.viewer_track_options
        )

        layout = QGridLayout()
        self.setLayout(layout)

        # row, col, rowspan, colspan
        layout.addWidget(QLabel('FPS:'), 0, 0, 1, 1)
        layout.addWidget(self.fps_spinbox, 0, 1, 1, 1)
        layout.addWidget(self.duration_label, 1, 0, 1, 2)
        layout.addWidget(self.save_btn, 2, 0, 1, 2)
        layout.addWidget(self.timeline, 0, 2, -1, -1)
        layout.setColumnStretch(
            2, 1000
        )  # timeline should take as much as possible

        self.viewer.layers.events.inserted.connect(self._update_layer_options)
        self.viewer.layers.events.removed.connect(self._update_layer_options)

        self.timeline.animation.track_removed.connect(self._update_duration)
        self.timeline.animation.keyframes_added.connect(self._update_duration)
        self.timeline.animation.keyframes_removed.connect(
            self._update_duration
        )
        self.timeline.animation.keyframes_moved.connect(self._update_duration)
        self.timeline.animation.track_removed.connect(self._update_duration)

        self.save_btn.pressed.connect(self._save_dialogue)
        self.fps_spinbox.valueChanged.connect(self._update_fps)

        self.fps_spinbox.setValue(30)

    def _update_layer_options(self):
        for layer in self.viewer.layers:
            if layer in self.layer_track_options:
                continue
            self.layer_track_options[layer] = {
                name.format(layer_name=layer.name): _resolve_attr_path(
                    layer, attr_path
                )
                for (name, attr_path) in _LAYER_TRACK_OPTIONS.items()
            }
            layer.events.name.connect(self._update_layer_track_names)

        for layer in list(self.layer_track_options):
            if layer not in self.viewer.layers:
                self.layer_track_options.pop(layer)
                layer.events.name.disconnect(self._update_layer_track_names)

        self._update_track_options()

    def _update_track_options(self):
        self.timeline.animation.track_options = (
            self.viewer_track_options
            | self.custom_track_options
            | {
                k: v
                for dct in self.layer_track_options.values()
                for k, v in dct.items()
            }
        )
        for track in list(self.timeline.animation.tracks):
            if track not in self.timeline.animation.track_options:
                self.timeline.animation.remove_track(track)

    def _update_layer_track_names(self, event):
        layer = event.source
        new_opts = {}
        for (old_name, old_val), name_template in zip(
            self.layer_track_options[layer].items(),
            _LAYER_TRACK_OPTIONS,
            strict=True,
        ):
            new_name = name_template.format(layer_name=layer.name)
            self.timeline.animation.rename_track(old_name, new_name)
            new_opts[new_name] = old_val

        self.layer_track_options[layer] = new_opts

    def add_custom_track(self, name: str, model: Any, attr: str):
        """Add a custom animation track to the timeline.

        A custom track can be added to control any model attribute.
        For example, to control `my_model.color.hue`, you may pass:
        `timeline.add_custom_track('MyModel hue', MyModel.color, 'hue')`
        """
        self.custom_track_options[name] = (model, attr)
        self._update_track_options()

    def remove_custom_track(self, name: str):
        """Remove a previously added custom track."""
        self.custom_track_options.pop(name)
        self._update_track_options()

    def _update_fps(self):
        self.timeline.animation.play_fps = self.fps_spinbox.value()
        self._update_duration()

    def _update_duration(self):
        self.duration_label.setText(
            f'Total duration:\n{self.timeline.animation.duration:.2f}s ({self.timeline.animation.n_frames} frames)'
        )

    def _save_dialogue(self):
        print('Not implemented')

    def save(
        self,
        filename,
        quality=5,
        canvas_only=True,
        scale_factor=None,
    ):
        import imageio
        from napari.utils.progress import cancelable_progress

        anim = self.timeline.animation
        fps = anim.play_fps

        file_path = Path(filename)
        folder_path = file_path.absolute().parent.joinpath(file_path.stem)
        self._filename = file_path

        save_as_folder = False
        if file_path.suffix == '':
            save_as_folder = True

        # try to create an ffmpeg writer. If not installed default to folder creation
        if save_as_folder is False:
            try:
                duration = 1000 / fps
                # create imageio writer. Handle separately imageio-ffmpeg extensions and
                # gif extension which doesn't accept the quality parameter.
                if file_path.suffix in [
                    '.mov',
                    '.avi',
                    '.mpg',
                    '.mpeg',
                    '.mp4',
                    '.mkv',
                    '.wmv',
                ]:
                    writer = imageio.get_writer(
                        filename,
                        fps=fps,
                        quality=quality,
                    )
                else:
                    writer = imageio.get_writer(
                        filename,
                        duration=duration,
                    )
            except ValueError as err:
                print(err)
                print('Your file will be saved as a series of PNG files')
                save_as_folder = True

        if save_as_folder:
            folder_path.mkdir(exist_ok=True)

        if self.timeline.is_playing():
            self.timeline.toggle_playback()

        mode = anim.play_mode

        anim.play_mode = PlayMode.NORMAL
        frame_iterator = self.timeline.animation.iter_frames()
        frames = []

        for _ in cancelable_progress(
            frame_iterator, desc='Rendering animation...', total=anim.n_frames
        ):
            image = self.viewer.screenshot(
                canvas_only=canvas_only, scale=scale_factor, flash=False
            )
            frames.append(image)
        if mode == PlayMode.PINGPONG:
            frames = frames + frames[::-1]

        for frame in frames:
            writer.append_data(frame)

        anim.play_mode = mode
