from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from napari.utils.events import SelectableEventedList

from napari_animation.easing import Easing

from .utils import make_thumbnail
from .viewer_state import ViewerState

if TYPE_CHECKING:
    import napari


@dataclass
class KeyFrame:
    """A single keyframe in the animation.

    Parameters
    ----------
    viewer_state : napari_animation.ViewerState
        The state of the viewer at this keyframe.
    thumbnail : np.ndarray
        A thumbnail representing this keyframe.
    steps : int
        Number of interpolation steps between last keyframe and captured one.
    ease : callable, optional
        If provided this method should make from `[0, 1]` to `[0, 1]` and will
        be used as an easing function for the transition between the last state
        and captured one.
    name : str
        A name for the keyframe.
    """

    viewer_state: ViewerState
    thumbnail: np.ndarray
    steps: int = 15
    ease: Easing = Easing.LINEAR
    name: str = "KeyFrame"

    def __str__(self):
        return self.name

    @classmethod
    def from_viewer(
        cls, viewer: napari.viewer.Viewer, steps=15, ease=Easing.LINEAR
    ):
        """Create a KeyFrame from a viewer instance."""
        return cls(
            viewer_state=ViewerState.from_viewer(viewer),
            thumbnail=make_thumbnail(
                viewer.screenshot(canvas_only=True, flash=False)
            ),
            steps=steps,
            ease=ease,
        )

    def __repr__(self) -> str:
        return f"<KeyFrame: {self.name}>"

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other):
        if isinstance(other, KeyFrame):
            return (
                self.__hash__() == other.__hash__()
                and self.viewer_state == other.viewer_state
                and (self.thumbnail == other.thumbnail).all()
                and self.steps == other.steps
                and self.ease == other.ease
            )
        else:
            return False


class KeyFrameList(SelectableEventedList[KeyFrame]):
    def __init__(self) -> None:
        super().__init__(basetype=KeyFrame)
