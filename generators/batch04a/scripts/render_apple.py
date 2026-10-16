import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_assets import *
render_asset('whole_red_apple')
