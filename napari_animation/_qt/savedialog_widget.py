from pathlib import Path

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QWidget,
)
from superqt import QLabeledSlider


class SaveDialogWidget(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getAnimationParameters(
        self,
        parent=None,
        caption="Select a file :",
        dir=".",
        filter="All files (*.*)",
        selectedFilter="",
        options=None,
    ):

        # Set dialog parameters
        self.setWindowTitle(caption)
        self.setDirectory(dir)
        self.setNameFilter(filter)
        self.setFileMode(QFileDialog.AnyFile)
        self.setAcceptMode(QFileDialog.AcceptSave)

        if selectedFilter != "":
            self.selectNameFilter(selectedFilter)
        if options is not None:
            self.setOptions(options)

        # add OptionsWidget
        self.setOption(QFileDialog.DontUseNativeDialog, True)
        layout = self.layout()
        self.optionsWidget = OptionsWidget(self)

        layout.addWidget(self.optionsWidget, 4, 1)
        self.setLayout(layout)

        # Get info back from user
        if self.exec_():
            animation_kwargs = {}
            extension = self.selectedNameFilter().split()[-1].strip('()*')
            animation_kwargs["path"] = Path(list(self.selectedFiles())[0]).with_suffix(extension)
            animation_kwargs["fps"] = self.optionsWidget.fpsSpinBox.value()
            animation_kwargs["quality"] = int(
                self.optionsWidget.qualitySlider.value()
            )
            animation_kwargs[
                "canvas_only"
            ] = self.optionsWidget.canvasCheckBox.isChecked()
            animation_kwargs[
                "scale_factor"
            ] = self.optionsWidget.scaleSpinBox.value()

            return animation_kwargs
        else:
            return ""


class OptionsWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QHBoxLayout()

        # "Canvas only" check box
        self.canvasCheckBox = QCheckBox("Canvas only", self)
        self.canvasCheckBox.toggle()
        layout.addWidget(self.canvasCheckBox)

        # Quality list
        self.qualitySlider = QLabeledSlider(Qt.Horizontal, self)
        self.qualitySlider.setRange(1, 10)
        self.qualitySlider.setValue(5)

        self.qualitySlider._slider.setMinimumWidth(70)
        self.qualitySlider._slider.setMaximumWidth(210)

        self.qualitySlider._label.setAlignment(Qt.AlignCenter)
        self.qualitySlider._label.setStyleSheet(
            "SliderLabel {background:transparent; border: 0; min-width: 20px; max-width: 20px;}"
            "SliderLabel::up-button, SliderLabel::down-button {subcontrol-origin: margin; width: 0px; height: 0px; }"
        )

        quality_label = QLabel("Quality", self)
        quality_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(quality_label)
        layout.addWidget(self.qualitySlider)

        # fps
        self.fpsSpinBox = QSpinBox(self)
        self.fpsSpinBox.setRange(1, 100000)
        self.fpsSpinBox.setValue(20)
        fps_label = QLabel("FPS", self)
        fps_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(fps_label)
        layout.addWidget(self.fpsSpinBox)

        # scale factor
        self.scaleSpinBox = QDoubleSpinBox(self)
        self.scaleSpinBox.setRange(0.001, 1000.0)
        self.scaleSpinBox.setValue(1.0)
        scale_label = QLabel("Scale factor", self)
        scale_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(scale_label)
        layout.addWidget(self.scaleSpinBox)

        self.setLayout(layout)
        self.setMaximumWidth(700)
