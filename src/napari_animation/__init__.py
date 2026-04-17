try:
    from ._version import version as __version__
except ImportError:
    __version__ = 'unknown'

from ._qt import AnimationWidget
from .animation import Animation
from .key_frame import KeyFrame
from .viewer_state import ViewerState

__all__ = ('AnimationWidget', 'Animation', 'KeyFrame', 'ViewerState')
