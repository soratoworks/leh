#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leh サイト ライブチェック（デプロイ後 / preview 実物）
  指定ページを実際に取得し、<img> の画像が全て HTTP 200 で表示できるか確認する。
  → repo は正しいのにサーバー側で画像が抜けている、を捕まえる（今日のバグ型）。

環境変数:
  PREVIEW_BASE  例 https://soratoworks.xsrv.jp/preview_leh/ （末尾スラッシュ必須）
  PREVIEW_USER / PREVIEW_PASS  Basic認証（preview はBasic認証あり）

使い方:
  python3 tools/check_live.py                 # 既定の主要ページを検査
  python3 tools/check_live.py collection.php silence/26aw/index.html   # ページ指定
終了コード: 表示できない画像が1件でもあれば 1
"""
import os, sys, re, base64, ssl
import urllib.request, urllib.error
from urllib.parse import urljoin, urldefrag, urlparse

# preview は自分の環境（Basic認証付き）。XServer初期ドメイン(*.xsrv.jp)は共有証明書で
# ホスト名不一致になるため、この自己監視チェックでは証明書検証をスキップする。
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

BASE = os.environ.get("PREVIEW_BASE", "http://soratoworks.xsrv.jp/preview_leh/")
if not BASE.endswith("/"):
    BASE += "/"
USER = os.environ.get("PREVIEW_USER", "")
PASS = os.environ.get("PREVIEW_PASS", "")
HOST = urlparse(BASE).netloc

DEFAULT_PAGES = [
    "collection.php", "silence.php", "stockist.php",
    "aboutus_en.php", "aboutus_jp.php", "index.html",
    "collection/26aw/index.html", "collection/26aw/item.html",
    "silence/26aw/index.html",
]

IMG_RE = re.compile(r'<img[^>]+src\s*=\s*["\']([^"\']+)["\']', re.I)
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)  # コメントアウトされた<img>は対象外
AUTH = "Basic " + base64.b64encode(f"{USER}:{PASS}".encode()).decode() if USER else None


def fetch(url, method="GET"):
    req = urllib.request.Request(url, method=method)
    if AUTH:
        req.add_header("Authorization", AUTH)
    req.add_header("User-Agent", "leh-live-check/1.0")
    return urllib.request.urlopen(req, timeout=30, context=SSL_CTX)


def main():
    if not USER or not PASS:
        print("⏭  PREVIEW_USER / PREVIEW_PASS 未設定のためライブチェックをスキップ（Basic認証が必要）")
        sys.exit(0)

    pages = sys.argv[1:] or DEFAULT_PAGES
    errors, checked = [], 0

    for page in pages:
        page_url = urljoin(BASE, page)
        try:
            html = fetch(page_url).read().decode("utf-8", "replace")
        except Exception as e:
            errors.append(f"[ページ取得失敗] {page} -> {e}")
            continue

        seen = set()
        for m in IMG_RE.finditer(COMMENT_RE.sub("", html)):
            raw = m.group(1).strip()
            if not raw or raw.lower().startswith(("data:",)):
                continue
            img_url = urljoin(page_url, urldefrag(raw)[0])
            if urlparse(img_url).netloc != HOST:  # 外部ホストの画像は対象外
                continue
            if img_url in seen:
                continue
            seen.add(img_url)
            checked += 1
            try:
                r = fetch(img_url, method="HEAD")
                if r.status != 200:
                    errors.append(f"[{page}] HTTP {r.status} -> {raw}")
            except urllib.error.HTTPError as e:
                errors.append(f"[{page}] HTTP {e.code} -> {raw}")
            except Exception as e:
                errors.append(f"[{page}] 取得失敗({e}) -> {raw}")

    print(f"=== ライブチェック（{BASE}）===")
    print(f"検査ページ {len(pages)} / 画像 {checked}枚")
    if errors:
        print(f"\n❌ 表示できない画像 {len(errors)}件:")
        for e in errors:
            print("  -", e)
    else:
        print("✅ 全画像 表示OK")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
