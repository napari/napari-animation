from mkdocs_gallery.gen_gallery import DefaultResetArgv
import qtgallery
from pathlib import Path

conf = {
    'reset_argv': DefaultResetArgv(),
    'default_thumb_file': Path(__file__).parent / 'assets' / 'images' / 'logo.png',
    #'image_scrapers': ("matplotlib", qtgallery.qtscraper,),
    'remove_config_comments': True,
    #'run_stale_examples': True,
}
