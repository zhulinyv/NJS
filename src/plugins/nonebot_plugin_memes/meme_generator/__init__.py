from pathlib import Path

from .config import meme_config as config
from .manager import add_meme as add_meme
from .manager import get_meme as get_meme
from .manager import get_meme_keys as get_meme_keys
from .manager import get_memes as get_memes
from .manager import load_meme as load_meme
from .manager import load_memes as load_memes
from .meme import Meme as Meme
from .meme import MemeArgsModel as MemeArgsModel
from .meme import MemeArgsParser as MemeArgsParser
from .meme import MemeArgsType as MemeArgsType
from .meme import MemeParamsType as MemeParamsType
from .version import __version__ as __version__

if config.meme.load_builtin_memes:
    for path in (Path(__file__).parent / "memes").iterdir():
        load_meme(f"meme_generator.memes.{path.name}")
for meme_dir in config.meme.meme_dirs:
    load_memes(meme_dir)
