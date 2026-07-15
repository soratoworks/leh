#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leh サイト 静的アセットチェック（デプロイ前）

既定では「変更のあったファイルだけ」を対象にする（15年物の古い遺産まで拾わないため）。
  ① リンク切れ: 変更した php/html 内の src/href が指すローカルファイルが実在するか → ERROR（デプロイを止める）
  ② 連番の抜け: 変更が関係する img フォルダの連番画像に欠番が無いか            → WARNING（止めない・通知のみ）

使い方:
  python3 tools/check_assets.py                # 変更ファイル（CHECK_BASE..HEAD ＋ 作業ツリー）を対象
  python3 tools/check_assets.py --all          # htdocs 全体（フル監査・ノイズ多い）
  python3 tools/check_assets.py <path> ...      # 指定ファイルのみ
環境変数 CHECK_BASE で比較元を指定（既定 origin/master。CI では push 前の SHA を渡す）。
終了コード: ERROR が1件でもあれば 1、無ければ 0
"""
import os, re, sys, subprocess
from urllib.parse import urldefrag, unquote

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROOT = os.path.join(REPO, "htdocs")

IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico", ".bmp"}
# repo が実際に管理している「コンテンツ」領域。ここ配下の画像参照だけ存在チェックする。
# （共通テンプレの css/js/favicon 等はサーバーにだけ在り repo に無いので対象外＝誤検出防止）
MANAGED_ROOTS = ("collection", "silence")

REF_RE = re.compile(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', re.I)
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)  # コメントアウトされた参照は対象外
# 末尾の _N / -N は「修正版（例 item1152_1, item1079-1）」として base番号に畳み込む
NUM_RE = re.compile(r'^(.*?)(\d+)((?:[_-]\d+)*)(\D*)$')


def is_local(u):
    u = u.strip()
    if not u:
        return False
    low = u.lower()
    return not any(low.startswith(p) for p in
                   ("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:", "#"))


def git_lines(*args):
    try:
        out = subprocess.run(["git", "-C", REPO, *args],
                             capture_output=True, text=True, check=True).stdout
        return [l for l in out.splitlines() if l.strip()]
    except Exception:
        return []


def changed_files():
    """変更のあった htdocs 配下ファイルの絶対パス集合。"""
    base = os.environ.get("CHECK_BASE", "origin/master")
    paths = set()
    # ベースとの差分（解決できなければ HEAD~1 にフォールバック）
    for ref in (base, "HEAD~1"):
        diff = git_lines("diff", "--name-only", f"{ref}...HEAD")
        if diff:
            paths.update(diff)
            break
    # 作業ツリーの変更（staged / unstaged / 未追跡）も対象に
    paths.update(git_lines("diff", "--name-only"))
    paths.update(git_lines("diff", "--name-only", "--cached"))
    paths.update(git_lines("ls-files", "--others", "--exclude-standard"))
    result = set()
    for p in paths:
        ap = os.path.normpath(os.path.join(REPO, p))
        if ap.startswith(ROOT + os.sep) and os.path.exists(ap):
            result.add(ap)
    return result


def all_files():
    res = set()
    for dp, _, files in os.walk(ROOT):
        for f in files:
            res.add(os.path.join(dp, f))
    return res


def check_links(pages):
    errors = []
    for path in sorted(pages):
        if not path.lower().endswith((".php", ".html", ".htm")):
            continue
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        base = os.path.dirname(path)
        for m in REF_RE.finditer(COMMENT_RE.sub("", text)):
            raw = m.group(1)
            if not is_local(raw):
                continue
            ref = unquote(urldefrag(raw)[0].split("?")[0]).strip()
            # 画像のみ・repo管理コンテンツ（collection/ silence/）配下の参照だけを対象にする
            if not ref or os.path.splitext(ref)[1].lower() not in IMG_EXT:
                continue
            target = os.path.normpath(os.path.join(base, ref))
            rel = os.path.relpath(target, ROOT)
            parts = rel.split(os.sep)
            # collection/<season>/... と silence/<season>/... のシーズン画像だけ対象。
            # 除外: repo外(..)、管理外ルート、共通UI(collection/img 直下)、共通favicon(common/)
            if rel.startswith("..") or len(parts) < 3 or parts[0] not in MANAGED_ROOTS:
                continue
            if parts[1] == "img" or "common" in parts:
                continue
            if not os.path.exists(target):
                errors.append(f"{os.path.relpath(path, ROOT)}: 参照画像が無い -> {raw}")
    return errors


def check_sequences(img_dirs):
    warnings = []
    for dp in sorted(img_dirs):
        if not os.path.isdir(dp):
            continue
        groups = {}
        for f in os.listdir(dp):
            stem, ext = os.path.splitext(f)
            if ext.lower() not in IMG_EXT:
                continue
            m = NUM_RE.match(stem)
            if not m:
                continue
            prefix, num, suffix = m.group(1), m.group(2), m.group(4)  # group(3)=修正版サフィックスは無視
            groups.setdefault((prefix, suffix, ext.lower()), []).append((int(num), len(num)))
        for (prefix, suffix, ext), items in groups.items():
            if len(items) < 3:
                continue
            nums = sorted(n for n, _ in items)
            width = max(w for _, w in items)
            present = set(nums)
            missing = [n for n in range(nums[0], nums[-1] + 1) if n not in present]
            if missing:
                rel = os.path.relpath(dp, ROOT)
                names = ", ".join(f"{prefix}{str(n).zfill(width)}{suffix}{ext}" for n in missing)
                warnings.append(f"{rel}: 連番に抜け（{nums[0]}〜{nums[-1]} のうち {len(missing)}個）-> {names}")
    return warnings


def img_dirs_for(pages, changed):
    """連番チェック対象の img ディレクトリ:
       変更画像の所在ディレクトリ ＋ 変更ページが参照する img ディレクトリ。"""
    dirs = set()
    for p in changed:
        if os.path.splitext(p)[1].lower() in IMG_EXT:
            dirs.add(os.path.dirname(p))
    for path in pages:
        if not path.lower().endswith((".php", ".html", ".htm")):
            continue
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        base = os.path.dirname(path)
        for m in REF_RE.finditer(COMMENT_RE.sub("", text)):
            raw = m.group(1)
            if not is_local(raw):
                continue
            ref = unquote(urldefrag(raw)[0].split("?")[0]).strip()
            if os.path.splitext(ref)[1].lower() in IMG_EXT:
                d = os.path.normpath(os.path.join(base, os.path.dirname(ref)))
                if d.startswith(ROOT):
                    dirs.add(d)
    return dirs


def main():
    args = sys.argv[1:]
    if "--all" in args:
        targets = all_files()
        scope = "htdocs 全体"
    elif args:
        targets = {os.path.normpath(os.path.abspath(a)) for a in args}
        scope = f"指定 {len(args)}件"
    else:
        targets = changed_files()
        scope = "変更ファイル"

    pages = {p for p in targets if p.lower().endswith((".php", ".html", ".htm"))}
    errors = check_links(pages)
    warnings = check_sequences(img_dirs_for(pages, targets))

    print(f"=== 静的アセットチェック（対象: {scope}）===")
    if not targets:
        print("（対象ファイルなし）")
    if errors:
        print(f"\n❌ リンク切れ {len(errors)}件:")
        for e in errors:
            print("  -", e)
    if warnings:
        print(f"\n⚠️  連番の抜け {len(warnings)}件:")
        for w in warnings:
            print("  -", w)
    if not errors and not warnings:
        print("✅ 問題なし")
    print(f"\n結果: エラー {len(errors)} / 警告 {len(warnings)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
