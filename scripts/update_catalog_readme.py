"""Refresh the generated asset table after a model revision, preserving other prose."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'README.md';s=p.read_text();catalog=json.loads((ROOT/'catalog.json').read_text())
for a in catalog:
 base=f"assets/{a['category']}/{a['id']}"
 row=f"| [{a['title_ja']}]({base}) | {a['triangles']:,} | {a['glb_bytes']/1000:.1f} KB | {a['blend_bytes']/1000:.1f} KB | {' × '.join(str(x) for x in a['dimensions_m'])} |"
 s=re.sub(r'^\| \['+re.escape(a['title_ja'])+r'\].*$',lambda _:row,s,flags=re.M)
s=s.replace('単色中心のオリジナル・ローポリ小物集です。','形状の自然さと素材の違いを保った、軽量なオリジナル小物集です。')
if '## 制作基準' not in s:
 s=s.replace('## 共通仕様','''## 制作基準

丸い物は自然に丸く見えるよう、曲面に必要な面数を配分します。陶器の釉薬、木材、塗装面、金属、ゴムの反射特性を分けています。日本にある物は、日本で見られる配色・形状・仕様を参考にします。

[詳しい制作基準](docs/asset-standard.md) · [GLB内の材質検証](material-validation.json)

## 共通仕様''')
if 'detail.jpg' not in s:
 s=s.replace('## 検証','''### 信号機の接写

![信号機の曲面・レンズ・塗装](assets/street/traffic_signal/detail.jpg)

塗装筐体・金属支柱・レンズの反射を分け、支柱やレンズの円周分割数を増やしています。フード付きの汎用モデルで、特定製品の複製ではありません。国内灯器の寸法・材質の参考：[日本通信電材の製品資料](https://www.nippon-tsushin.jp/wp/wp-content/themes/nippontsushin/file/business/electric/singou.pdf)。資料の製品はフードレスで、本モデルとは構造が異なります。

## 検証''')
s=s.replace('python scripts/prepare_previews.py','blender -b --python scripts/render_signal_detail.py\npython scripts/prepare_previews.py\npython scripts/inspect_materials.py\npython scripts/update_catalog_readme.py') if 'python scripts/inspect_materials.py' not in s else s
p.write_text(s)
