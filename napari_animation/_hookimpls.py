from napari_plugin_engine import napari_hook_implementation

from ._qt import AnimationWidget


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    widget_options = {
        "name": "Wizard",
        "add_vertical_stretch": False,
    }
    return AnimationWidget, widget_options


@napari_hook_implementation
def napari_register_actions():
    return [
        (AnimationWidget, "Alt-f", AnimationWidget._capture_keyframe_callback)
        (AnimationWidget, "Alt-r", AnimationWidget._replace_keyframe_callback)
        (AnimationWidget, "Alt-d", AnimationWidget._capture_keyframe_callback)
        (AnimationWidget, "Alt-a", lambda w: w.animation.key_frames.select_next())
        (AnimationWidget, "Alt-b", lambda w: w.animation.key_frames.select_previous())
        # ('napari.Viewer', 'alt-f', viewer_function) # To register action to viewer (not used, but illustrative)
        # ('napari.layers.Points', 'alt-p', points_function) # To register action to points layer (not used, but illustrative)
    ]
