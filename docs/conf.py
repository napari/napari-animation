# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import os
import shutil
from pathlib import Path

import imageio.v2 as iio
import napari
from sphinx_gallery import scrapers
from sphinx_gallery.sorting import ExampleTitleSortKey

from napari_animation._version import version as napari_animation_version

release = napari_animation_version
if "dev" in release:  # noqa: SIM108
    version = "dev"
else:
    version = release

# -- Project information -----------------------------------------------------

project = "napari-animation"
copyright = "2024, The napari team"  # noqa: A001
author = "The napari team"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx_external_toc",
    "myst_nb",
    "sphinx.ext.viewcode",
    "sphinx_favicon",
    "sphinx_copybutton",
    "sphinx_gallery.gen_gallery",
    "sphinxcontrib.video",
]

external_toc_path = "_toc.yml"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "napari_sphinx_theme"

# # Define the json_url for our version switcher.
# json_url = "https://napari.org/dev/_static/version_switcher.json"

# if version == "dev":
#     version_match = "latest"
# else:
#     version_match = release

html_theme_options = {
    "external_links": [{"name": "napari", "url": "https://napari.org"}],
    "github_url": "https://github.com/napari/napari-animation",
    "navbar_start": ["navbar-logo", "navbar-project"],
    "navbar_end": ["navbar-icon-links"],
    # "switcher": {
    #     "json_url": json_url,
    #     "version_match": version_match,
    # },
    "navbar_persistent": [],
    "header_links_before_dropdown": 6,
    "secondary_sidebar_items": ["page-toc"],
    "pygment_light_style": "napari",
    "pygment_dark_style": "napari",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_logo = "images/logo.png"
html_sourcelink_suffix = ""
html_title = "napari animation"

favicons = [
    {
        # the SVG is the "best" and contains code to detect OS light/dark mode
        "static-file": "favicon/logo-silhouette-dark-light.svg",
        "type": "image/svg+xml",
    },
    {
        # Safari in Oct. 2022 does not support SVG
        # an ICO would work as well, but PNG should be just as good
        # setting sizes="any" is needed for Chrome to prefer the SVG
        "sizes": "any",
        "static-file": "favicon/logo-silhouette-192.png",
    },
    {
        # this is used on iPad/iPhone for "Save to Home Screen"
        # apparently some other apps use it as well
        "rel": "apple-touch-icon",
        "sizes": "180x180",
        "static-file": "favicon/logo-noborder-180.png",
    },
]

html_css_files = [
    "custom.css",
]

intersphinx_mapping = {
    "python": ["https://docs.python.org/3", None],
    "numpy": ["https://numpy.org/doc/stable/", None],
    "napari_plugin_engine": [
        "https://napari-plugin-engine.readthedocs.io/en/latest/",
        "https://napari-plugin-engine.readthedocs.io/en/latest/objects.inv",
    ],
    "napari": [
        "https://napari.org/dev",
        "https://napari.org/dev/objects.inv",
    ],
}

myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
    "substitution",
    "tasklist",
]

myst_heading_anchors = 4
suppress_warnings = ["etoc.toctree"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".jupyter_cache",
    "jupyter_execute",
]

# -- Examples gallery scrapers -------------------------------------------------


class VideoScraper:
    """Video file scraper class.
    Scrapes video files that were saved to disk by the example scripts.
    Based on the sphinx example scraper "Example 2: detecting image files on disk"
    https://sphinx-gallery.github.io/stable/advanced.html#example-2-detecting-image-files-on-disk
    """

    def __init__(self):
        self.seen = set()

    def __repr__(self):
        return "VideoScraper"

    def __call__(self, block, block_vars, gallery_conf):
        """Video file scraper.
        Scrapes video files that were saved to disk by the example scripts.
        Based on the sphinx example scraper "Example 2: detecting image files on disk"
        https://sphinx-gallery.github.io/stable/advanced.html#example-2-detecting-image-files-on-disk
        """
        # Find all video files in the directory of this example.
        video_file_extensions = [".mp4", ".mov"]
        path_current_example = os.path.dirname(block_vars["src_file"])
        video_paths = sorted(
            str(p.resolve())
            for p in Path(path_current_example).glob("**/*")
            if p.suffix in video_file_extensions
        )

        # Iterate through the videos, copy them to the sphinx-gallery output directory
        video_names = []
        image_path_iterator = block_vars["image_path_iterator"]
        rst = ""
        for video in video_paths:
            if video not in self.seen:
                self.seen |= set(video)
                this_video_path = image_path_iterator.next()
                this_video_path = (
                    os.path.splitext(this_video_path)[0]
                    + os.path.splitext(video)[1]
                )
                video_names.append(this_video_path)
                shutil.move(video, this_video_path)
                assert os.path.exists(this_video_path)
                self.video_thumbnail(this_video_path)
                relative_path = (
                    ".."
                    + os.sep
                    + ".."
                    + os.sep
                    + gallery_conf.get("gallery_dirs").strip()
                    + this_video_path.split(gallery_conf.get("gallery_dirs"))[
                        -1
                    ].strip()
                )
                rst += self.rst_video_template(relative_path)

        # We want to display either a video OR a napari screenshot, not both!
        # If any video files are found, VideoScraper() closes any open napari windows
        # so that the static screenshot napari_scraper will not find anything
        # For this to work, VideoScraper() must come BEFORE napari_scraper in sphinx_gallery_conf
        if len(video_paths) > 0:
            napari.Viewer.close_all()

        return rst

    def video_thumbnail(self, video_filename):
        """Save PNG screenshot of the first video frame."""
        reader = iio.get_reader(video_filename)
        first_frame = reader.get_data(0)
        first_frame_filename = os.path.splitext(video_filename)[0] + ".png"
        iio.imwrite(first_frame_filename, first_frame)
        return first_frame

    def rst_video_template(self, video_filepath):
        """Template HTML for embedding video into webpage."""
        rst = f""".. video:: {video_filepath}
        :autoplay:
        :loop:
        :width: 600
        :poster: {os.path.splitext(video_filepath)[0] + ".png"}
    """
        return rst


def napari_scraper(block, block_vars, gallery_conf):
    """Basic napari window scraper.

    Looks for any QtMainWindow instances and takes a screenshot of them.

    `app.processEvents()` allows Qt events to propagateo and prevents hanging.
    """
    imgpath_iter = block_vars["image_path_iterator"]

    if app := napari.qt.get_app():
        app.processEvents()
    else:
        return ""

    img_paths = []
    for win, img_path in zip(
        reversed(napari._qt.qt_main_window._QtMainWindow._instances),
        imgpath_iter,
    ):
        img_paths.append(img_path)
        win._window.screenshot(img_path, canvas_only=False)

    napari.Viewer.close_all()
    app.processEvents()

    return scrapers.figure_rst(img_paths, gallery_conf["src_dir"])


def reset_napari(gallery_conf, fname):
    from napari.settings import get_settings
    from qtpy.QtWidgets import QApplication

    settings = get_settings()
    settings.appearance.theme = "dark"

    # Disabling `QApplication.exec_` means example scripts can call `exec_`
    # (scripts work when run normally) without blocking example execution by
    # sphinx-gallery. (from qtgallery)
    QApplication.exec_ = lambda _: None


sphinx_gallery_conf = {
    # path to your example scripts
    "examples_dirs": "../examples",
    "gallery_dirs": "gallery",  # path to where to save gallery generated output
    "filename_pattern": "/*.py",
    "ignore_pattern": "README.rst|/*_.py",
    "default_thumb_file": Path(__file__).parent / "images" / "logo.png",
    "plot_gallery": "'True'",  # https://github.com/sphinx-gallery/sphinx-gallery/pull/304/files
    "download_all_examples": False,
    "only_warn_on_example_error": False,
    "abort_on_example_error": True,
    "image_scrapers": (
        "matplotlib",
        VideoScraper(),
        # We want to display either a video OR a napari screenshot, not both!
        # If any video files are found, VideoScraper() closes any open napari windows
        # so that the static screenshot napari_scraper will not find anything
        # For this to work, VideoScraper() must come BEFORE napari_scraper in sphinx_gallery_conf
        napari_scraper,
    ),
    "reset_modules": (reset_napari,),
    "reference_url": {"napari": None},
    "within_subsection_order": ExampleTitleSortKey,
}


def setup(app):
    """Set up docs build.

    * Ignores .ipynb files to prevent sphinx from complaining about multiple
      files found for document when generating the gallery
    """
    app.registry.source_suffix.pop(".ipynb", None)
