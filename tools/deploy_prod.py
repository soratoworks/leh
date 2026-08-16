#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本番(lolipop www.leh.jp)へ「今回の変更分だけ」をFTPで上げる surgical デプロイ。
repo は不完全ミラーのため全体同期はせず、下記の成果物だけをピンポイントで上書き/新規アップする。
htaccess・共通ファイル等は一切触らない。

環境変数:
  PROD_FTP_SERVER / PROD_FTP_USERNAME / PROD_FTP_PASSWORD  … lolipop FTP
  DRY  … "false" のときだけ実アップ。それ以外(既定)は dry-run（一覧表示のみ・無変更）
"""
import os, sys, ftplib, ssl

LOCAL_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "htdocs")
LOCAL_ROOT = os.path.normpath(LOCAL_ROOT)

# --- アップ対象（本番ドキュメントルート = FTPログイン直後 / からの相対パス）---
FILES = [
    "index.html",
    "collection.php", "silence.php", "stockist.php",
    "aboutus_en.php", "aboutus_jp.php",
]
DIRS = [
    "collection/26aw",
    "silence/26aw",
    "lib/img/top/26aw",
]
SKIP = (".DS_Store",)

DRY = os.environ.get("DRY", "true").strip().lower() != "false"


def connect():
    host = os.environ["PROD_FTP_SERVER"]; user = os.environ["PROD_FTP_USERNAME"]; pw = os.environ["PROD_FTP_PASSWORD"]
    try:
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        f = ftplib.FTP_TLS(context=ctx); f.connect(host, 21, timeout=60); f.login(user, pw); f.prot_p()
        print("[接続] FTPS OK"); return f
    except Exception as e:
        print("[FTPS失敗]", e, "-> 平FTP"); f = ftplib.FTP(); f.connect(host, 21, timeout=60); f.login(user, pw)
        print("[接続] FTP OK"); return f


def collect():
    """(local_path, remote_path) のリストを作る。"""
    targets = []
    for rel in FILES:
        lp = os.path.join(LOCAL_ROOT, rel)
        if not os.path.isfile(lp):
            print("⚠ ローカルに無い(スキップ):", rel); continue
        targets.append((lp, rel))
    for d in DIRS:
        base = os.path.join(LOCAL_ROOT, d)
        if not os.path.isdir(base):
            print("⚠ ローカルに無い(スキップ):", d); continue
        for dp, _, files in os.walk(base):
            for fn in sorted(files):
                if fn in SKIP or fn.startswith("._"):
                    continue
                lp = os.path.join(dp, fn)
                rel = os.path.relpath(lp, LOCAL_ROOT).replace(os.sep, "/")
                targets.append((lp, rel))
    return targets


def ensure_dirs(f, remote_path):
    parts = remote_path.split("/")[:-1]
    cur = ""
    for p in parts:
        cur = (cur + "/" + p) if cur else p
        try:
            f.mkd(cur)
        except ftplib.error_perm:
            pass  # 既に在る


def main():
    targets = collect()
    total_bytes = sum(os.path.getsize(lp) for lp, _ in targets)
    print(f"\n=== 本番デプロイ対象: {len(targets)}ファイル / {total_bytes/1024/1024:.1f}MB ===")
    print(f"モード: {'DRY-RUN（無変更・一覧のみ）' if DRY else '★実アップ★'}\n")
    for lp, rp in targets:
        print(f"  {'[予定]' if DRY else '[上げる]'} {rp}  ({os.path.getsize(lp)//1024}KB)")

    if DRY:
        # 接続だけ確認（書き込みはしない）
        try:
            f = connect(); print("ログイン直後:", f.pwd()); f.quit()
            print("→ 接続OK。")
        except Exception as e:
            print("→ 接続テスト失敗:", e); sys.exit(1)
        print("\nDRY-RUN のため本番には何も書き込んでいません。")
        return

    f = connect()
    print("ログイン直後:", f.pwd())
    ok = 0
    for lp, rp in targets:
        ensure_dirs(f, rp)
        with open(lp, "rb") as fp:
            f.storbinary("STOR " + rp, fp)
        ok += 1
        if ok % 10 == 0:
            print(f"  ...{ok}/{len(targets)}")
    print(f"\n✅ アップ完了: {ok}/{len(targets)} ファイル")
    try: f.quit()
    except Exception: pass


if __name__ == "__main__":
    main()
