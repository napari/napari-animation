from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from .easing import Easing
from .utils import make_thumbnail

if TYPE_CHECKING:
    from napari import Viewer


@dataclass(frozen=True)
class ViewerState:
    """The state of the viewer camera, dims, and layers.

    Parameters
    ----------
    camera : dict
        The state of the `napari.components.Camera` in the viewer.
    dims : dict
        The state of the `napari.components.Dims` in the viewer.
    layers : dict
        A map of layer.name -> _base_state for each layer in the viewer
        (excluding metadata).
    """

    camera: dict
    dims: dict
    layers: dict

    @classmethod
    def from_viewer(cls, viewer: Viewer):
        """Create a ViewerState from a viewer instance."""
        layers = {
            layer.name: layer._get_base_state() for layer in viewer.layers
        }
        for d in layers.values():
            d.pop("metadata")
        return cls(
            camera=viewer.camera.dict(), dims=viewer.dims.dict(), layers=layers
        )


    def __eq__(self, other):
        if isinstance(other, ViewerState):
            return (
                self.camera == other.camera and
                self.dims == other.dims and
                self.layers == other.layers
            )
        else:
            return False


@dataclass(frozen=True)
class KeyFrame:
    """A single keyframe in the animation.

    Parameters
    ----------
    viewer_state : ViewerState
        The state of the viewer at this keyframe.
    thumbnail : np.ndarray
        A thumbnail representing this keyframe.
    steps : int
        Number of interpolation steps between last keyframe and captured one.
    ease : callable, optional
        If provided this method should make from `[0, 1]` to `[0, 1]` and will
        be used as an easing function for the transition between the last state
        and captured one.
    """

    viewer_state: ViewerState
    thumbnail: np.ndarray
    steps: int = 15
    ease: Easing = Easing.LINEAR

    @classmethod
    def from_viewer(cls, viewer: Viewer, steps=15, ease=Easing.LINEAR):
        """Create a KeyFrame from a viewer instance."""
        return cls(
            viewer_state=ViewerState.from_viewer(viewer),
            thumbnail=make_thumbnail(viewer.screenshot(canvas_only=True)),
            steps=steps,
            ease=ease,
        )

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other):
        if isinstance(other, KeyFrame):
            return (
                self.__hash__() == other.__hash__() and
                self.viewer_state == other.viewer_state and
                (self.thumbnail == other.thumbnail).all() and
                self.steps == other.steps and
                self.ease == other.ease
            )
        else:
            return False

            
