from pathlib import Path

SCHALE_URL = "https://lonqie.github.io/SchaleDB/"
MIRROR_SCHALE_URL = "http://schale.lgc2333.top/"

BAWIKI_DB_URL = "https://bawiki.lgc2333.top/"

RES_PATH = Path(__file__).parent / "res"
# RES_FONT = RES_PATH / "SourceHanSansSC-Bold-2.otf"
RES_CALENDER_BANNER = RES_PATH / "calender_banner.png"
RES_SCHALE_BG = RES_PATH / "schale_bg.jpg"

DATA_PATH = Path.cwd() / "data" / "BAWiki"
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)
