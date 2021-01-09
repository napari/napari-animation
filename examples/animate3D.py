"""
Display a labels layer above of an image layer using the add_labels and
add_image APIs
"""

from skimage import data
from scipy import ndimage as ndi
from napari_animation import Animation
import napari


blobs = data.binary_blobs(length=128, volume_fraction=0.1, n_dim=3)
viewer = napari.view_image(blobs.astype(float), name='blobs')
labeled = ndi.label(blobs)[0]
viewer.add_labels(labeled, name='blob ID')

animation = Animation(viewer)
viewer.update_console({'animation': animation})

viewer.dims.ndisplay = 3
viewer.camera.angles = (0.0, 0.0, 90.0)
animation.capture_keyframe()
viewer.camera.zoom = 2.4
animation.capture_keyframe()
viewer.camera.angles = (-7.0, 15.7, 62.4)
animation.capture_keyframe(steps=60)
viewer.camera.angles = (2.0, -24.4, -36.7)
animation.capture_keyframe(steps=60)
viewer.reset_view()
viewer.camera.angles = (0.0, 0.0, 90.0)
animation.capture_keyframe()
animation.animate('demo3D.mov', canvas_only=False)
