# napari-animation documentation

**napari-animation** is a plugin for making animations in [napari](https://napari.org).

<p align="center">
  <img width="500" src="https://user-images.githubusercontent.com/7307488/196110138-6c4663b1-67b2-4c79-97b7-57b706d1d49c.gif">
</p>

napari-animation is hosted on GitHub at [github.com/napari/napari-animation](https://github.com/napari/napari-animation).

## Overview

**napari-animation** provides a framework for the creation of animations in napari, the plugin contains:

- an easy to use GUI for creating animations interactively;
- a Python package for the programmatic creation of animations.

This plugin remains under development and contributions are very welcome, please open an issue to discuss potential improvements.

## Installation

### PyPI
`napari-animation` is available through the Python package index and can be installed using `pip`.

```sh
pip install napari-animation
```

### Local
You can clone this repository and install locally with

    pip install -e .

### Interactive use
**napari-animation** can be used interactively.

An animation is created by capturing [keyframes](https://en.wikipedia.org/wiki/Key_frame) containing the current viewer state.

<p align="center">
  <img width="600" src="https://user-images.githubusercontent.com/7307488/196113682-96ce0da3-fa5c-411e-8fb1-52dc3a8f96b6.png">
</p>

To activate the GUI, select **napari-animation: wizard** from the *plugins menu*

<p align="center">
  <img width="200" src="https://user-images.githubusercontent.com/7307488/196114466-56cb5985-0d79-4cfa-96f1-38cf3ccfbc48.png">
</p>

### Headless
**napari-animation** can also be run headless, allowing for reproducible, scripted creation of animations.

```python
from napari_animation import Animation

animation = Animation(viewer)

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
animation.animate('demo.mov', canvas_only=False)
```

## Contributing

Contributions are very welcome and a detailed contributing guide is coming soon. 

Tests are run with `pytest`.

We use [`pre-commit`](https://pre-commit.com) to sort imports with
[`isort`](https://github.com/timothycrosley/isort), format code with
[`black`](https://github.com/psf/black), and lint with
[`flake8`](https://github.com/PyCQA/flake8) automatically prior to each commit.
To minmize test errors when submitting pull requests, please install `pre-commit`
in your environment as follows:

```sh
pre-commit install
```

## Documentation

The documentation for napari-animation is built with [mkdocs](https://www.mkdocs.org). After installing the documentation dependencies with

```sh
pip install ".[doc]"
```

you can see a local version of the documentation by running

```sh
mkdocs serve
```

Open up http://127.0.0.1:8000/ in your browser, and you'll see the home page of the docs being displayed.

## License

Distributed under the terms of the [BSD-3 license](http://opensource.org/licenses/BSD-3-Clause), "napari-animation" is free and open source software.

## Issues

If you encounter any problems, please [file an issue on GitHub](https://github.com/napari/napari-animation/issues) along with a detailed description.
