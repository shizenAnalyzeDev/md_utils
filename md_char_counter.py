#!/usr/bin/env python3
"""
Markdownファイルの##セクション配下の文字数を自動計算し、
###文字数: として出力するスクリプト

各##セクションの本文（##見出しの次の行から、次の全ての見出しまで）の
文字数をカウントして、### 文字数: の行を自動挿入・更新します。
"""

import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime


def count_section_chars(section_content):
    """
    セクション内の文字数をカウント（スペースと改行を除く）
    ### 文字数: の行は除外してカウント
    """
    # ### 文字数: の行を除外
    lines = section_content.split('\n')
    filtered_lines = [line for line in lines if not line.startswith('### 文字数:')]
    text = '\n'.join(filtered_lines)
    
    # スペースと改行を除いた文字数
    char_count = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))
    return char_count


def process_markdown_file(file_path):
    """
    Markdownファイルを処理して文字数を更新
    各##セクションの本文（##見出しの次の行から、次の全ての見出しまで）の文字数をカウント
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        content = original_content
        # ## で始まる行でセクションを分割
        # (?=\n##) で改行後の##をマッチ（半角・全角スペース両対応）
        # ファイルの先頭に改行を追加して統一的に処理
        if not content.startswith('\n'):
            content = '\n' + content
        sections = re.split(r'(?=\n##[ 　])', content)

        updated_content = ""

        for i, section in enumerate(sections):
            # ##で始まるかチェック（半角・全角スペース両対応）
            if i == 0 and not (section.strip().startswith('## ') or section.strip().startswith('##　')):
                # 最初のセクション（##より前の部分）
                updated_content += section
            else:
                # ## セクションの処理
                # セクションの最初の改行を保持
                if section.startswith('\n'):
                    updated_content += '\n'
                    section = section[1:]

                # ## タイトル行と本文を分離
                lines = section.split('\n')
                title_line = lines[0]  # ## タイトル

                # 本文部分を抽出（次の見出しまで、または最後まで）
                # ### 文字数: の行と、それ以降の見出し（#で始まる行）は除外
                body_lines = []
                for line in lines[1:]:
                    # ### 文字数: の行はスキップ
                    if line.startswith('### 文字数:'):
                        continue
                    # 次の見出し（#で始まる行）が来たら終了
                    if line.startswith('#'):
                        break
                    body_lines.append(line)

                body_text = '\n'.join(body_lines)
                char_count = count_section_chars(body_text)

                # セクションを再構築（次の見出し以降も含める）
                # 次の見出し以降の内容を保持
                remaining_lines = []
                found_next_heading = False
                for line in lines[1:]:
                    if line.startswith('### 文字数:'):
                        continue
                    if line.startswith('#') and not found_next_heading:
                        found_next_heading = True
                    if found_next_heading:
                        remaining_lines.append(line)

                remaining_text = '\n'.join(remaining_lines)
                if remaining_text:
                    updated_content += f"{title_line}\n### 文字数: {char_count}\n{body_text}\n{remaining_text}"
                else:
                    updated_content += f"{title_line}\n### 文字数: {char_count}\n{body_text}"

        # 内容が変更された場合のみ書き込み
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

        return True, None
    
    except Exception as e:
        return False, str(e)


def process_directory(directory_path, recursive=True):
    """
    指定ディレクトリ以下の全.mdファイルを処理
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"エラー: ディレクトリが見つかりません: {directory_path}")
        return
    
    # .mdファイルを検索
    if recursive:
        md_files = list(directory.rglob('*.md'))
    else:
        md_files = list(directory.glob('*.md'))
    
    if not md_files:
        print(f"警告: {directory_path} に.mdファイルが見つかりませんでした")
        return
    
    print(f"処理対象: {len(md_files)}個のファイル\n")
    
    success_count = 0
    error_count = 0
    
    for md_file in md_files:
        print(f"処理中: {md_file}")
        success, error = process_markdown_file(md_file)
        
        if success:
            print(f"  ✓ 完了\n")
            success_count += 1
        else:
            print(f"  ✗ エラー: {error}\n")
            error_count += 1
    
    print("=" * 50)
    print(f"処理完了: 成功 {success_count}件 / エラー {error_count}件")


def watch_directory(directory_path, recursive=True):
    """
    ディレクトリを監視して、.mdファイルが変更されたら自動的に文字数を更新
    """
    directory = Path(directory_path)

    if not directory.exists():
        print(f"エラー: ディレクトリが見つかりません: {directory_path}")
        return

    # .mdファイルを検索
    if recursive:
        md_files = list(directory.rglob('*.md'))
    else:
        md_files = list(directory.glob('*.md'))

    if not md_files:
        print(f"警告: {directory_path} に.mdファイルが見つかりませんでした")
        return

    # 各ファイルの最終更新時刻を記録
    file_mtimes = {}
    for md_file in md_files:
        file_mtimes[md_file] = md_file.stat().st_mtime

    print(f"監視開始: {len(md_files)}個のファイル")
    print("Ctrl+Cで終了")
    print("=" * 50)

    try:
        while True:
            time.sleep(1.5)  # 0.5秒ごとにチェック

            # 新しいファイルをチェック
            if recursive:
                current_files = set(directory.rglob('*.md'))
            else:
                current_files = set(directory.glob('*.md'))

            # 新しいファイルが追加された場合
            new_files = current_files - set(file_mtimes.keys())
            for new_file in new_files:
                file_mtimes[new_file] = new_file.stat().st_mtime
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 新規ファイル検出: {new_file}")
                success, error = process_markdown_file(new_file)
                if success:
                    print("  ✓ 処理完了")
                else:
                    print(f"  ✗ エラー: {error}")

            # 既存ファイルの変更をチェック
            for md_file in list(file_mtimes.keys()):
                if not md_file.exists():
                    # ファイルが削除された
                    del file_mtimes[md_file]
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ファイル削除: {md_file}")
                    continue

                current_mtime = md_file.stat().st_mtime
                if current_mtime > file_mtimes[md_file]:
                    # ファイルが更新された
                    file_mtimes[md_file] = current_mtime
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 更新検出: {md_file}")
                    success, error = process_markdown_file(md_file)
                    if success:
                        print("  ✓ 文字数更新完了")
                    else:
                        print(f"  ✗ エラー: {error}")

    except KeyboardInterrupt:
        print("\n\n監視を終了しました")


def main():
    """
    メイン処理
    """
    # 引数の解析
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]

    # ディレクトリパスの決定（指定なしの場合はカレントディレクトリ）
    if len(args) == 0:
        directory_path = '.'
        print("使用方法: python md_char_counter.py [ディレクトリパス] [--watch] [--no-recursive]")
        print("\n例:")
        print("  python md_char_counter.py          # カレントディレクトリを処理")
        print("  python md_char_counter.py ./docs   # 指定ディレクトリを処理")
        print("  python md_char_counter.py --watch  # カレントディレクトリを監視")
        print("  python md_char_counter.py ./docs --watch  # ファイル変更を監視")
        print("  python md_char_counter.py ./docs --no-recursive  # サブディレクトリを除外")
        print("  python md_char_counter.py ./docs --watch --no-recursive")
        print("\nディレクトリ指定なしでカレントディレクトリを処理します...\n")
    else:
        directory_path = args[0]

    recursive = '--no-recursive' not in sys.argv
    watch_mode = '--watch' in sys.argv

    print(f"ディレクトリ: {directory_path}")
    print(f"再帰処理: {'有効' if recursive else '無効'}")
    print(f"監視モード: {'有効' if watch_mode else '無効'}")
    print("=" * 50)

    if watch_mode:
        watch_directory(directory_path, recursive)
    else:
        process_directory(directory_path, recursive)


if __name__ == "__main__":
    main()