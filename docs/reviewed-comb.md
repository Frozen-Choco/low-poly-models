# くしの公開資料

新規くしr3の独立レビュー済みパッケージです。メーカー画像は含めていません。公開移設時にモデル・画像・生成ソースは変更していません。入力パスとカタログの公開情報だけを対応づけています。

生成: Blender4.3.2で `generators/household_restart_20261017/scripts/build_comb.py`。生成先は同generatorのmodels/combです。

写真再現: リポジトリルートをSOURCE_ROOTに指定し、`blender -b -t 2 --python generators/comb_restart_20261017_preview_standard_v1/render.py -- comb VIEW`。VIEWはpreview/back/front/rear/left/side/top/underside/close_up/underside_detail/alternate_light。1200×1200、512samples、閾値0.005、denoiseなし。新しい生成GLBは公開入力hashと一致することを先に確認してください。

写真recordsと元inputsは撮影時の証跡として変更せず保存しています。records内の元のローカル出力パスは履歴であり公開リンクではありません。公開先対応はcomb-relocation.jsonにあります。新しいinputs.jsonはモデル実体の移設先のみを更新しました。renderer/spec、画像bytes、モデルbytesは変更していません。

source内の文書には承認発行前の時点を記載した説明を保持しています。現在の承認は `reviews/comb_restart_20261017/source_package_approval.json` と、それを参照する公開メタデータで確認できます。
