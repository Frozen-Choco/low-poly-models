# Low-poly diorama models

現実世界のジオラマに配置するための、形状の自然さと素材の違いを保った、軽量なオリジナル小物集です。現在10モデル。目標は合計1,000モデルです。

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
| [横型信号機](assets/street/traffic_signal) | 7,078 | 295.0 KB | 143.6 KB | 1.415 × 0.57 × 4.9505 |
| [踏切警報機・遮断機（下降）](assets/street/railway_crossing_lowered) | 40,296 | 1431.3 KB | 316.0 KB | 5.181 × 0.715 × 3.789 |
| [公共用分別回収ボックス](assets/street/public_recycling_bin) | 14,708 | 773.2 KB | 197.3 KB | 0.480 × 0.489 × 1.018 |

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

明るさを抑えたライトグレーの塗装筐体・高粗さの金属支柱・暗い光学ベース・個別のLED配列・黒い保持リングを分けています。支柱はクロームのような強い鏡面反射を抑え、ライトは赤点灯／青・黄消灯を区別しています。フード付きの汎用モデルで、特定製品の複製ではありません。国内灯器の白い外装・LED配列の参考：[日本信号の製品写真](https://sales.signal.co.jp/traffic_signal/)。寸法・材質の参考：[日本通信電材の製品資料](https://www.nippon-tsushin.jp/wp/wp-content/themes/nippontsushin/file/business/electric/singou.pdf)。資料の製品はフードレスで、本モデルとは構造が異なります。

## 独立レビュー済みの追加モデル

次の2点は、形状・接続部・素材・別方向の照明・保存ファイル・生成コードを独立レビュー済みです。既存5点を、この新基準で一括承認したという意味ではありません。

### 踏切警報機・遮断機（下降）

![踏切警報機・遮断機（下降）](assets/street/railway_crossing_lowered/preview.jpg)

[GLB](assets/street/railway_crossing_lowered/railway_crossing_lowered.glb) · [Blend](assets/street/railway_crossing_lowered/railway_crossing_lowered.blend) · [背面](assets/street/railway_crossing_lowered/back.jpg) · [接写](assets/street/railway_crossing_lowered/close_up.jpg)

### 公共用分別回収ボックス

![公共用分別回収ボックス](assets/street/public_recycling_bin/preview.jpg)

[GLB](assets/street/public_recycling_bin/public_recycling_bin.glb) · [Blend](assets/street/public_recycling_bin/public_recycling_bin.blend) · [背面](assets/street/public_recycling_bin/back.jpg) · [接写](assets/street/public_recycling_bin/close_up.jpg)

[昼光での配置確認](generators/batch02b/previews/context_daylight.jpg) · [別方向の照明](generators/batch02b/previews/context_alternate_light.jpg) · [再生成方法・制約](generators/batch02b/README.md)

踏切は遮断棒を下げた片側ユニット、回収ボックスは屋根のある公共空間向けの静的モデルです。文脈画像は縮尺と材質を確認するための配置で、完成した写真風ジオラマではありません。

## 検証

Blender 4.3.2で制作。保存した全 `.blend` を再度開き、各GLBを空のシーンへ読み込み直しました。三角形数と外接範囲の一致、頂点の数値異常、面積ゼロの三角形、ファイル容量を検証しています。初期5点の結果は [validation.json](validation.json)、追加2点の結果は [batch02bの検証結果](generators/batch02b/validation.json) を参照してください。

- GLBには照明・背景床・カメラを含みません。
- Blendの `PREVIEW STUDIO` コレクションは通常のビューポートでは非表示です。モデルを別シーンへ移す際は `ASSET` コレクションを使ってください。
- パーツ同士の接触・重なりを許すジオラマ／描画用モデルです。水密の一体形状や3Dプリント適性は保証していません。
- 信号機はライトグレー筐体・艶を抑えた亜鉛めっき調支柱の横型汎用デザインです。赤LEDを点灯、青・黄は消灯した状態にしています。動的な点灯制御やアニメーションは含みません。
- マグカップは内部の空洞と底・壁の厚みを持たせています。

## 再生成

Blender 4.3.2 と、プレビュー変換用の Python / Pillow を使用します。以下は初期5点用の手順です。追加2点は [batch02bの再生成手順](generators/batch02b/README.md) を使用してください。

```sh
blender -b --python scripts/build_assets.py
ONLY_ASSETS=oak_table,dining_chair,open_shelf,mug,traffic_signal blender -b --python scripts/validate_assets.py
blender -b --python scripts/render_signal_detail.py
python scripts/prepare_previews.py
python scripts/inspect_materials.py
python scripts/update_catalog_readme.py
```

再生成は既存のモデルファイルを書き換えます。手作業で編集したモデルは別名で保存してください。

## ライセンス

配布ライセンスは未設定です。公開リポジトリであることだけを、無制限の再利用許可とは扱わないでください。


### 信号機の配色再調整

筐体・ひさしと支柱の明度差を抑えました。形状と赤点灯状態は変更していません。保存したBLENDの再読込とGLBの再インポート、別照明での比較を独立レビューで確認済みです。色は写真からの推定で、測色値や特定製品の保証色ではありません。確認画像の支柱には若干のレンダーノイズがあります。参考：[大阪府警の信号機資料](https://www.police.pref.osaka.lg.jp/kotsu/kisei/shingouki/12111.html)。

## 追加モデル：街灯・ベンチ・コーン

以下の3点は制作担当とは独立したレビュー、保存ファイルの再読込、実配置・別照明の確認を経て公開しています。

- [公園ベンチ](assets/street/park_bench)：5,800三角形、GLB 458,368 bytes
- [街路灯](assets/street/streetlight)：8,428三角形、GLB 269,884 bytes
- [三角コーン](assets/street/traffic_cone)：4,620三角形、GLB 122,564 bytes

街灯は消灯状態です。コーンは底部の重りが一体の積み重ね不可モデルで、白帯は通常のPBR材質による表現です。専用の再帰反射シェーダーは使用していません。

[生成・検証手順](generators/batch02a/README.md) · [検証結果](generators/batch02a/validation.json)
