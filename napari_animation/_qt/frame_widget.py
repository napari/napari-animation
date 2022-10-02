from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtWidgets import QComboBox, QFormLayout, QSpinBox, QWidget

from ..easing import Easing

if TYPE_CHECKING:
    from ..animation import Animation


class FrameWidget(QWidget):
    """Widget for interatviely making animations using the napari viewer."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.animation: Animation = self.parentWidget().animation
        self.animation.key_frames.selection.events.active.connect(
            self._on_active_keyframe_changed
        )

        # init steps
        self.stepsSpinBox = QSpinBox()
        self.stepsSpinBox.setRange(1, 100000)
        self.stepsSpinBox.setValue(15)

        # init ease
        self.easeComboBox = QComboBox()
        self.easeComboBox.addItems([e.name.lower() for e in Easing])
        self.easeComboBox.setCurrentText("linear")

        # add callbacks
        self.stepsSpinBox.valueChanged.connect(self._update_animation_steps)
        self.easeComboBox.currentIndexChanged.connect(
            self._update_animation_ease
        )

        # layout
        self.setLayout(QFormLayout())
        self.layout().addRow("Steps", self.stepsSpinBox)
        self.layout().addRow("Ease", self.easeComboBox)

    def _on_active_keyframe_changed(self, event):
        """update state of self to reflect animation state at active key frame"""
        key_frame = event.value
        if key_frame:
            self.stepsSpinBox.setValue(key_frame.steps)
            active_keyframe = self.animation.key_frames.selection.active
            ease = active_keyframe.ease
            self.easeComboBox.setCurrentText(ease.name.lower())

    def _update_animation_steps(self, event):
        """update state of 'steps' at current key-frame to reflect GUI state"""
        active_keyframe = self.animation.key_frames.selection.active
        if active_keyframe is None:
            return
        active_keyframe.steps = self.stepsSpinBox.value()
        # TODO: if this changes programatically the slider will be out of sync.
        # but we don't currently have events on the keyframe.steps attribute.
        self.animation._frames._rebuild_keyframe_index()

    def _update_animation_ease(self, event):
        """update state of 'ease' at current key-frame to reflect GUI state"""
        active_keyframe = self.animation.key_frames.selection.active
        active_keyframe.ease = self.get_easing_func()

    def get_easing_func(self):
        return Easing[self.easeComboBox.currentText().upper()]
