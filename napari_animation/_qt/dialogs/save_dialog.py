from pathlib import Path
from typing import Any, Callable

from PyQt5.QtWidgets import QFileDialog, QMessageBox


class SaveAnimationDialog(QFileDialog):
    """
    Dialog to choose the save location of animation

    Parameters
    ----------
    animate_function : Callable[[str], Any]
        Function to be called on successful selection of save location
    parent : QWidget, optional
        Optional parent widget for this one
    directory : str, optional
    """

    def __init__(
            self,
            animate_function: Callable[[str], Any],
            parent=None,
            directory=str(Path.home())
    ):
        super().__init__(parent=parent)
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setFileMode(QFileDialog.AnyFile)
        self.setNameFilter('Video files (*.mp4)')
        self.setDirectory(directory)

        self.animate_function = animate_function

    def accept(self):
        save_path = Path(self.selectedFiles()[0])
        if save_path.suffix == '':
            save_path = save_path.parent / (save_path.stem + '.png')
            if save_path.exists():
                res = QMessageBox().warning(
                    self,
                    'Confirm overwrite',
                    f'{save_path} already exists. Do you want to replace it?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if res != QMessageBox.Yes:
                    super().accept()
                    self.exec_()
        self.animate_function(save_path)
        return super().accept()
