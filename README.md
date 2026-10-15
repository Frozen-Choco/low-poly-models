# Low-poly diorama models

現実世界のジオラマに配置するための、形状の自然さと素材の違いを保った、軽量なオリジナル小物集です。第1セットは5モデル。

## 制作基準

丸い物は自然に丸く見えるよう、曲面に必要な面数を配分します。陶器の釉薬、木材、塗装面、金属、ゴムの反射特性を分けています。日本にある物は、日本で見られる配色・形状・仕様を参考にします。

[詳しい制作基準](docs/asset-standard.md) · [GLB内の材質検証](material-validation.json)

## 共通仕様

- GLB、編集用 `.blend`、正面寄り／背面寄りの確認画像を各モデルに同梱。
- メートルスケール。BlenderはZ-up、正面は-Y。GLBは標準のY-upに変換して書き出しています。
- 原点は床面付近。信号機は支柱の基部、他は設置面の中央付近です。
- 実在の特定製品の複製ではありません。寸法はジオラマ向けに設定した目安で、製造・施工用の図面ではありません。
- 外部テクスチャ・外部モデルは使用せず、マテリアルを同梱。外部ファイル参照なしでGLBを開けます。
- すべてのファイルは100,000,000バイト未満。上限に近づけず小さく保っています。
- ポリゴン数は三角形換算で記載しています。

## 一覧

| モデル | 三角形 | GLB | 編集用Blend | 寸法 X × Y × Z（m、Blender座標） |
|---|---:|---:|---:|---|
| [ダイニングチェア](assets/furniture/dining_chair) | 640 | 57.6 KB | 100.1 KB | 0.43 × 0.45073 × 0.88121 |
| [木製テーブル](assets/furniture/oak_table) | 616 | 56.3 KB | 99.2 KB | 1.2 × 0.7 × 0.75 |
| [オープンシェルフ](assets/furniture/open_shelf) | 968 | 86.1 KB | 99.8 KB | 0.905 × 0.35 × 1.51 |
| [マグカップ](assets/household/mug) | 1,684 | 40.1 KB | 109.9 KB | 0.123 × 0.086 × 0.108 |
| [横型信号機](assets/street/traffic_signal) | 5,528 | 188.0 KB | 146.3 KB | 1.415 × 0.57 × 4.9505 |

## プレビューとファイル

### ダイニングチェア

![ダイニングチェア](assets/furniture/dining_chair/preview.jpg)

[GLB](assets/furniture/dining_chair/dining_chair.glb) · [Blend](assets/furniture/dining_chair/dining_chair.blend) · [背面画像](assets/furniture/dining_chair/back.jpg) · [メタデータ](assets/furniture/dining_chair/metadata.json)

### 木製テーブル

![木製テーブル](assets/furniture/oak_table/preview.jpg)

[GLB](assets/furniture/oak_table/oak_table.glb) · [Blend](assets/furniture/oak_table/oak_table.blend) · [背面画像](assets/furniture/oak_table/back.jpg) · [メタデータ](assets/furniture/oak_table/metadata.json)

### オープンシェルフ

![オープンシェルフ](assets/furniture/open_shelf/preview.jpg)

[GLB](assets/furniture/open_shelf/open_shelf.glb) · [Blend](assets/furniture/open_shelf/open_shelf.blend) · [背面画像](assets/furniture/open_shelf/back.jpg) · [メタデータ](assets/furniture/open_shelf/metadata.json)

### マグカップ

![マグカップ](assets/household/mug/preview.jpg)

[GLB](assets/household/mug/mug.glb) · [Blend](assets/household/mug/mug.blend) · [背面画像](assets/household/mug/back.jpg) · [メタデータ](assets/household/mug/metadata.json)

### 横型信号機

![横型信号機](assets/street/traffic_signal/preview.jpg)

[GLB](assets/street/traffic_signal/traffic_signal.glb) · [Blend](assets/street/traffic_signal/traffic_signal.blend) · [背面画像](assets/street/traffic_signal/back.jpg) · [メタデータ](assets/street/traffic_signal/metadata.json)

### 信号機の接写

![信号機の曲面・レンズ・塗装](assets/street/traffic_signal/detail.jpg)

塗装筐体・金属支柱・レンズの反射を分け、支柱やレンズの円周分割数を増やしています。フード付きの汎用モデルで、特定製品の複製ではありません。国内灯器の寸法・材質の参考：[日本通信電材の製品資料](https://www.nippon-tsushin.jp/wp/wp-content/themes/nippontsushin/file/business/electric/singou.pdf)。資料の製品はフードレスで、本モデルとは構造が異なります。

## 検証

Blender 4.3.2で制作。保存した全 `.blend` を再度開き、各GLBを空のシーンへ読み込み直しました。三角形数と外接範囲の一致、頂点の数値異常、面積ゼロの三角形、ファイル容量を検証しています。結果は [validation.json](validation.json) を参照してください。

- GLBには照明・背景床・カメラを含みません。
- Blendの `PREVIEW STUDIO` コレクションは通常のビューポートでは非表示です。モデルを別シーンへ移す際は `ASSET` コレクションを使ってください。
- パーツ同士の接触・重なりを許すジオラマ／描画用モデルです。水密の一体形状や3Dプリント適性は保証していません。
- 信号機は横型の汎用デザインで、レンズ3色を着色しています。点灯制御やアニメーションは含みません。
- マグカップは内部の空洞と底・壁の厚みを持たせています。

## 再生成

Blender 4.3.2 と、プレビュー変換用の Python / Pillow を使用します。

```sh
blender -b --python scripts/build_assets.py
blender -b --python scripts/validate_assets.py
blender -b --python scripts/render_signal_detail.py
python scripts/prepare_previews.py
python scripts/inspect_materials.py
python scripts/update_catalog_readme.py
```

再生成は既存のモデルファイルを書き換えます。手作業で編集したモデルは別名で保存してください。

## ライセンス

配布ライセンスは未設定です。公開リポジトリであることだけを、無制限の再利用許可とは扱わないでください。
