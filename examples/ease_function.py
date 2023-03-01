import napari
from skimage import data
from napari_animation import Animation
from napari_animation.easing import Easing

cat = data.cat()
viewer = napari.view_image(cat, rgb=True)


animation = Animation(viewer)
viewer.camera.zoom = 1
animation.capture_keyframe(steps=0)
animation.capture_keyframe(steps=60)
viewer.camera.zoom = 1.5
animation.capture_keyframe(steps=30, ease=Easing.QUADRATIC)

animation.capture_keyframe(steps=60)

animation.animate("hello.mp4", canvas_only=True, fps=60)
