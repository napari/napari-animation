"""
Camera example
==============
"""
from scipy import ndimage as ndi
from napari_animation import Animation
import napari
import skimage
import scipy

viewer = napari.Viewer(ndisplay=3)

nuclei = skimage.data.cells3d()[:,1,...]
denoised = scipy.ndimage.median_filter(nuclei, size=3)
th_nuclei = denoised > skimage.filters.threshold_li(denoised)
th_nuclei = skimage.morphology.remove_small_holes(th_nuclei, 20**3)
labels_data = skimage.measure.label(th_nuclei)

animation = Animation(viewer)

image_layer = viewer.add_image(nuclei, name="nuclei", depiction="plane",
                               blending='translucent')
labels_layer = viewer.add_labels(labels_data, name="labels", blending='translucent')

viewer.camera.angles = (-18.23797054423494, 41.97404742075617, 141.96173085742896)
viewer.camera.zoom *= 0.5


def replace_labels_data():
    z_cutoff = int(image_layer.plane.position[0])
    new_labels_data = labels_data.copy()
    new_labels_data[z_cutoff:] = 0
    labels_layer.data = new_labels_data


labels_layer.visible = False
image_layer.plane.position = (0, 0, 0)
animation.capture_keyframe(steps=30)

image_layer.plane.position = (59, 0, 0)
animation.capture_keyframe(steps=30)

image_layer.plane.position = (0, 0, 0)

animation.capture_keyframe(steps=30)

image_layer.plane.events.position.connect(replace_labels_data)
labels_layer.visible = True
labels_layer.experimental_clipping_planes = [{
    "position": (0, 0, 0),
    "normal": (-1, 0, 0),  # point up in z (i.e: show stuff above plane)
}]

image_layer.plane.position = (59, 0, 0)
# access first plane, since it's a list
labels_layer.experimental_clipping_planes[0].position = (59, 0, 0)
animation.capture_keyframe(steps=30)

image_layer.plane.position = (0, 0, 0)
animation.capture_keyframe(steps=30)

animation.animate("test.mp4", canvas_only=True)
image_layer.plane.position = (0, 0, 0)