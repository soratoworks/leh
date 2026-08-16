# Leh サイト 運用・デプロイ仕様

このリポジトリ（`soratoworks/leh`）の更新とデプロイの手順書。

- **ソース本体（ローカルrepo）**: `/Users/sorato/_works/_leh`（`.git` + `htdocs/`）
- **リモートrepo**: GitHub `soratoworks/leh`（master 運用）
- **公開ドキュメントルート**: `htdocs/`（この中身がサーバーに配られる）
- 構成: PHP + 静的HTML の従来型サイト
- ⚠️ repo は**サイトの不完全ミラー**。共通アセット（`lib/` `common/` 一部 `css/` `js/` `img/mail.jpg` `movie.php` 等）は過去に手動FTPで直接上げられ、**repoには入っていない**（サーバーにのみ存在）。

---

## 毎回更新するファイル / ディレクトリ

シーズンや情報の更新のたびに触る対象。**新規シーズン追加時は以下をセットで更新する。**

| 対象 | 種別 | 内容 |
|---|---|---|
| `htdocs/collection/<季>/` | ディレクトリ（新規） | コレクションの LOOK(`index.html`) ＋ ITEM(`item.html`) ＋ `img/`。既存シーズンを流用して作る |
| `htdocs/collection.php` | ファイル | コレクション一覧の導線。最新シーズンをトップ枠へ昇格＋旧トップを過去一覧へ降格 |
| `htdocs/silence/<季>/` | ディレクトリ（新規） | SILENCE の `index.html` ＋ `img/` |
| `htdocs/silence.php` | ファイル | SILENCE 一覧の導線（昇格/降格） |
| `htdocs/stockist.php` | ファイル | 取扱店舗リスト。支給Excelの一番右の列（削除/追加/更新）に従って反映 |
| `htdocs/aboutus_en.php` / `htdocs/aboutus_jp.php` | ファイル | 展示会・イベント履歴を時系列で末尾に追記（日英ペア） |
| `htdocs/index.html` ＋ `htdocs/lib/img/top/<季>/` | ファイル＋ディレクトリ | トップの写真スライダー(`.wideslider`)。新シーズンの写真(600×600)を `lib/img/top/<季>/` に置き、`index.html` のスライダー**先頭**に `<li><img ...></li>` を追加。古いシーズンは適宜整理（例: 追加分と同数を最古シーズンから削除して総数維持）。`lib/img/top/` は repo 追跡対象なので**画像も git add** する |

命名の注意:
- コレクション画像は大文字（`leh_26AW_look1.jpg` / `leh_26AW_item1157.jpg`）だが **title 画像だけ小文字**（`leh_26aw_title.png`）のことがある。
- 連番画像の**修正版は `_1` や `-1` を付けて追加**することがある（例 `leh_26SS_item1152_1.jpg` / `leh_25AW_item1079-1.jpg`）＝欠番ではない。
- Mac の `.DS_Store` / `._*` はコミット・アップロードしない（`.gitignore` 済み）。

---

## プレビュー反映（XServer）— ✅ 稼働中・自動

**フロー**: ローカルで編集 → `git commit` → `git push`（master） → GitHub Actions が自動でFTPデプロイ。

- ワークフロー: `.github/workflows/deploy-preview.yml`（push で自動起動 ＋ 手動 `Run workflow` も可）
- 反映先: `http://soratoworks.xsrv.jp/preview_leh/`（**HTTP**。httpsは初期ドメインの証明書不一致で別vhostに飛ぶ／Basic認証あり・ユーザー `leh`）
- 差分ファイルのみアップ（初回のみ全ファイルで数十分、以降は数十秒）
- デプロイの前後に**検証チェック**が走る（下記）
- 手順は Claude が commit→push まで実行してよい（この Mac は git 認証キャッシュ済み）。ターミナルで叩く場合 **先頭に `!` を付けない**（zshで `!` は直前の成否を反転し `&&` 以降がスキップされる）。

---

## 本番反映（lolipop `www.leh.jp`）— 🚧 未構築・方針のみ

preview とは**別サーバー（lolipop）**。まだワークフロー未作成。決めた方針:

1. **手動のみ**。push では動かさず、GitHub Actions の `Run workflow`（`workflow_dispatch`）で押した時だけ実行する（別ワークフロー）。
2. 手段は **FTP**（lolipop 宛て）。認証情報は GitHub Secrets に（preview の `FTP_*` と分けて **`PROD_` 接頭辞**）:
   - `PROD_FTP_SERVER` … lolipop の FTP サーバー
   - `PROD_FTP_USERNAME` … FTP ユーザー名
   - `PROD_FTP_PASSWORD` … FTP パスワード
   - 取得元: ロリポップ！ユーザー専用ページ →「サーバーの管理・設定」→「FTP・WebDAVアカウント設定」
   - 本番の server-dir（docロート配下パス）はワークフロー作成時に確定する。
3. **htaccess の出し分け必須** 🔑
   - 現行 `htdocs/.htaccess` は **preview 用（Basic認証つき）** → 本番へ上げると本番にロックがかかるので**絶対に上げない**。
   - 本番は `htdocs/prd.htaccess.txt`（ドメイン直下用・リダイレクト設定）が正。
4. **アップ範囲は限定推奨**。repo が不完全ミラーのため「htdocs 全体同期」は repo の古い版で本番を上書きする恐れ → **今回変更したフォルダ/ファイルだけ**を上げる方式が安全。

---

## 検証チェック（デプロイに組込み・CI）

`tools/` のスクリプトが GitHub Actions 内で自動実行される。

- **`tools/check_assets.py`（デプロイ前・静的）**: 変更ファイルのシーズン画像のリンク切れがあれば**デプロイを止める**（ERROR）。連番の欠番は WARNING。`_N`/`-N` の修正版は在るものとして扱う。共通テンプレは対象外。`--all` で全体監査。
- **`tools/check_live.py`（デプロイ後・ライブ）**: preview 実物の主要ページを取得し `<img>` が全て HTTP 200 で表示できるか確認（サーバー側の画像抜け・403 等を捕捉）。Secrets `PREVIEW_USER`/`PREVIEW_PASS` 必要。

## サーバー権限（403対策）

FTP新規アップは通常Webから読める権限になるが、手動 rsync 等で `-rwx------`(700) が残ると **403** になる。修正:
```
ssh soratoworks@sv14112.xserver.jp -p 10022 \
 'cd ~/soratoworks.xsrv.jp/public_html/preview_leh/<対象> && \
  find . -type d -exec chmod 705 {} \; && find . -type f -exec chmod 604 {} \;'
```
（XServer は鍵認証設定済みで、ルーティンなサーバー修正は Claude が直接 SSH 実行してよい。破壊的操作は事前確認。）
