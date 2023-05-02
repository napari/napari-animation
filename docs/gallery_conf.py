from pathlib import Path

import qtgallery
from mkdocs_gallery.gen_gallery import DefaultResetArgv

conf = {
    "reset_argv": DefaultResetArgv(),
    "default_thumb_file": Path(__file__).parent
    / "assets"
    / "images"
    / "logo.png",
    "image_scrapers": (
        "matplotlib",
        qtgallery.qtscraper,
    ),
    "reset_modules": (qtgallery.reset_qapp,),
    "remove_config_comments": True,
    "run_stale_examples": True,
}
