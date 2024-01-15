from pathlib import Path

import napari
from mkdocs_gallery.gen_gallery import DefaultResetArgv
from mkdocs_gallery import scrapers


def napari_scraper(block, script):
    """Basic napari window scraper.

    Looks for any QtMainWindow instances and takes a screenshot of them.

    `app.processEvents()` allows Qt events to propagateo and prevents hanging.

    Parameters
    ----------
    block : tuple
        A tuple containing the (label, content, line_number) of the block.

    script : GalleryScript
        Script being run

    Returns
    -------
    md : str
        The ReSTructuredText that will be rendered to HTML containing
        the images. This is often produced by :func:`figure_md_or_html`.
    """
    if app := napari.qt.get_app():
        app.processEvents()
    else:
        return ""

    imgpath_iter = script.run_vars.image_path_iterator
    img_paths = []
    for win, img_path in zip(
        reversed(napari._qt.qt_main_window._QtMainWindow._instances),
        imgpath_iter,
    ):
        img_paths.append(img_path)
        win._window.screenshot(img_path, canvas_only=False)

    napari.Viewer.close_all()
    app.processEvents()

    return scrapers.figure_md_or_html(img_paths, script)


def reset_napari(gallery_conf, fname):
    from napari.settings import get_settings
    from qtpy.QtWidgets import QApplication

    settings = get_settings()
    settings.appearance.theme = "dark"

    # Disabling `QApplication.exec_` means example scripts can call `exec_`
    # (scripts work when run normally) without blocking example execution by
    # sphinx-gallery. (from qtgallery)
    QApplication.exec_ = lambda _: None


conf = {
    "reset_argv": DefaultResetArgv(),
    "default_thumb_file": Path(__file__).parent
    / "assets"
    / "images"
    / "logo.png",
    "image_scrapers": (
        scrapers.matplotlib_scraper,
        napari_scraper,
    ),
    "reset_modules": (reset_napari,),
    "remove_config_comments": True,
    "run_stale_examples": True,
}
