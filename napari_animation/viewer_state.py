from dataclasses import dataclass

import napari
import numpy as np


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
    def from_viewer(cls, viewer: napari.viewer.Viewer):
        """Create a ViewerState from a viewer instance."""
        layers = {
            layer.name: layer._get_base_state() for layer in viewer.layers
        }
        for d in layers.values():
            d.pop("metadata")
        return cls(
            camera=viewer.camera.dict(), dims=viewer.dims.dict(), layers=layers
        )

    def apply(self, viewer: napari.viewer.Viewer):
        """Update `viewer` to match this ViewerState.

        Parameters
        ----------
        viewer : napari.viewer.Viewer
            A napari viewer. (viewer state will be directly modified)
        """

        viewer.camera.update(self.camera)
        viewer.dims.update(self.dims)

        for layer_name, layer_state in self.layers.items():
            layer = viewer.layers[layer_name]
            for key, value in layer_state.items():
                original_value = getattr(layer, key)
                # Only set if value differs to avoid expensive redraws
                if not np.array_equal(original_value, value):
                    setattr(layer, key, value)

    def render(
        self, viewer: napari.viewer.Viewer, canvas_only: bool = True
    ) -> np.ndarray:
        """Render this ViewerState to an image.

        Parameters
        ----------
        viewer : napari.viewer.Viewer
            A napari viewer to render screenshots from.
        canvas_only : bool, optional
            Whether to include only the canvas (and exclude the napari
            gui), by default True

        Returns
        -------
        np.ndarray
            An RGBA image of shape (h, w, 4).
        """
        self.apply(viewer)
        return viewer.screenshot(canvas_only=canvas_only, flash=False)

    def __eq__(self, other):
        if isinstance(other, ViewerState):
            return (
                self.camera == other.camera
                and self.dims == other.dims
                and self.layers == other.layers
            )
        else:
            return False
