# napari-animation

[![License](https://img.shields.io/pypi/l/napari-animation.svg?color=green)](https://github.com/napari/napari-animation/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-animation.svg?color=green)](https://pypi.org/project/napari-animation)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-animation.svg?color=green)](https://python.org)
[![tests](https://github.com/napari/napari-animation/actions/workflows/test_and_deploy.yml/badge.svg)](https://github.com/napari/napari-animation/actions)
[![codecov](https://codecov.io/gh/napari/napari-animation/branch/main/graph/badge.svg)](https://codecov.io/gh/napari/napari-animation)

**napari-animation** is a plugin for making animations in [napari](https://napari.org).

<p align="center">
  <img width="500" src="https://user-images.githubusercontent.com/7307488/196110138-6c4663b1-67b2-4c79-97b7-57b706d1d49c.gif">
</p>

----------------------------------

[Merlin Lange](https://twitter.com/Merlin_Lange) used *napari-animation* to create one of [Nature's best science images for September 2022](https://www.nature.com/immersive/d41586-022-03051-6/index.html)

----------------------------------

This plugin is built on [`naparimovie`](https://github.com/guiwitz/naparimovie) from [@guiwitz](https://github.com/guiwitz). `naparimovie` was submitted to napari in [PR#851](https://github.com/napari/napari/pull/780) before napari plugin infrastructure existed.

----------------------------------

## Overview

**napari-animation** provides a framework for the creation of animations in napari. The plugin contains:

- an easy to use GUI for creating animations interactively;
- a Python package for the programmatic creation of animations.

This plugin remains under development and contributions are very welcome, please open an issue to discuss potential improvements.

You can read the documentation at [https://napari.org/napari-animation](https://napari.org/napari-animation)

## Installation

### PyPI
`napari-animation` is available through the Python package index and can be installed using `pip`.

```sh
pip install napari-animation
```

```{warning}
`napari-animation` uses `ffmpeg` to export animations. If you are using a macOS arm64 computer (Apple Silicon e.g. M1, M2 processor)
the PyPI package does not include the needed binary for your platform. You will need to install `ffmpeg` using
`conda` from the [conda-forge channel](https://conda-forge.org/docs/#what-is-conda-forge) (`conda install -c conda-forge ffmpeg`)
or using [`homebrew`](https://brew.sh) (`brew install ffmpeg`).
```

### Conda
`napari-animation` is also available for install using `conda` through the [conda-forge channel](https://conda-forge.org/docs/#what-is-conda-forge).

```sh
conda install -c conda-forge napari-animation
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

### Scripting

**napari-animation** can also be run programatically, allowing for reproducible, scripted creation of animations.

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

## Examples

Examples can be found in our [Examples gallery](https://napari.org/napari-animation/gallery), generated from [our example scripts](https://github.com/napari/napari-animation/tree/main/examples). Simple examples for both interactive and headless
use of the plugin follow.

## Contributing

Contributions are very welcome and a detailed contributing guide is coming soon.
In the meantime, clone this repository and install it in editable mode using `pip`:

```
pip install -e .
```
We recommend using a virtual environment, for example `conda`.


```{important}
Ensure you have a suitable Qt backend for napari! We recommend `PyQt5`.
For more information, see the napari [Qt backend installation guide](https://napari.org/stable/tutorials/fundamentals/installation.html#choosing-a-different-qt-backend)
```

To set up your development installation, clone this repository, navigate to the clone folder, and install napari-animation in editable mode using `pip`.

```sh
conda create -n nap-anim python=3.10
conda activate nap-anim
pip install -e ".[dev]" PyQt5

```

Tests are run with `pytest`.
You can make sure your `[dev]` installation is working properly by running
`pytest .` from within the repository.

```{note}
We use [`pre-commit`](https://pre-commit.com) to sort imports and lint with
[`ruff`](https://github.com/astral-sh/ruff) and format code with
[`black`](https://github.com/psf/black) automatically prior to each commit.
To minmize test errors when submitting pull requests, please install `pre-commit`
in your environment as follows:

`pre-commit install`
```

## Documentation

The documentation is available at [https://napari.org/napari-animation](https://napari.org/napari-animation)

The documentation for napari-animation is built with [Sphinx](https://www.spinx-doc.org) and the [napari Sphinx Theme](https://github.com/napari/napari-sphinx-theme).

### Building docs locally

After installing the documentation dependencies with

```sh
pip install ".[doc]"
```

you can see a local version of the documentation by running

```sh
make docs
```

Open up the `docs/_build/index.html` file in your browser, and you'll see the home page of the docs being displayed.

### Deploying docs

The napari-animation documentation is automatically built and deployed to the website
whenever the main branch is updated, or a new release is tagged.
This is controlled by the [deploy_docs.yml](https://github.com/napari/napari-animation/blob/main/.github/workflows/deploy_docs.yml) github actions script.

You can also manually trigger a documenation re-build and deployment [from the github actions tab](https://github.com/napari/napari-animation/actions/workflows/deploy_docs.yml).

## License

Distributed under the terms of the [BSD-3 license](http://opensource.org/licenses/BSD-3-Clause),
`napari-animation` is free and open source software.

## Issues

If you encounter any problems, please [file an issue](https://github.com/napari/napari-animation/issues) along with a detailed description.

[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[file an issue]: https://github.com/napari/napari-animation/issues
[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
