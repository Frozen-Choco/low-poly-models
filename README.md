# Low-poly diorama models

現実世界のジオラマに配置するための、単色中心のオリジナル・ローポリ小物集です。第1セットは5モデル。

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
| [ダイニングチェア](assets/furniture/dining_chair) | 640 | 59.4 KB | 100.5 KB | 0.43 × 0.45073 × 0.88121 |
| [木製テーブル](assets/furniture/oak_table) | 616 | 56.3 KB | 98.7 KB | 1.2 × 0.7 × 0.75 |
| [オープンシェルフ](assets/furniture/open_shelf) | 968 | 86.1 KB | 99.7 KB | 0.905 × 0.35 × 1.51 |
| [マグカップ](assets/household/mug) | 360 | 19.9 KB | 96.9 KB | 0.123 × 0.086 × 0.108 |
| [横型信号機](assets/street/traffic_signal) | 1,132 | 81.0 KB | 108.6 KB | 1.415 × 0.57 × 4.9505 |

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
python scripts/prepare_previews.py
```

再生成は既存のモデルファイルを書き換えます。手作業で編集したモデルは別名で保存してください。

## ライセンス

配布ライセンスは未設定です。公開リポジトリであることだけを、無制限の再利用許可とは扱わないでください。
