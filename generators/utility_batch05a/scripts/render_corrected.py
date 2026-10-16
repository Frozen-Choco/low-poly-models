import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
for slug in ['plastic_bail_bucket','wall_clock']:render_asset(slug)
