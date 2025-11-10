
# md_utils

Markdownファイルの`##`見出しセクションごとの文字数を自動カウントして、`### 文字数: <N>`の行を挿入するシンプルなツールです。

## 機能
### 文字数: 147

- 指定したディレクトリ内の`.md`ファイルを再帰的に処理
- 各`##`セクションの本文文字数をカウント（スペース・改行を除く）
- `### 文字数:`行を自動挿入・更新
- `--watch`オプションでファイル変更を監視して自動更新
- `--no-recursive`オプションでサブディレクトリを除外

## 必要環境
### 文字数: 12

- Python 3.8以上

## セットアップ
### 文字数: 262

### 1. リポジトリをクローン

```bash
git clone https://github.com/sumomo/md_utils.git
cd md_utils
```

### 2. 仮想環境の作成（推奨）

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

現在は外部依存なしで動作します。

## 使い方
### 文字数: 339

### 基本的な使い方

指定ディレクトリ内の全`.md`ファイルを処理：

```bash
python md_char_counter.py ./docs
```

### 監視モード

ファイルの変更を監視して自動で文字数を更新：

```bash
python md_char_counter.py ./docs --watch
```

終了する場合は`Ctrl+C`を押してください。

### サブディレクトリを除外

指定ディレクトリ直下のファイルのみを処理：

```bash
python md_char_counter.py ./docs --no-recursive
```

### オプションの組み合わせ

```bash
python md_char_counter.py ./docs --watch --no-recursive
```

## 実行例
### 文字数: 282

```bash
$ python md_char_counter.py ./test_docs
ディレクトリ: ./test_docs
再帰処理: 有効
監視モード: 無効
==================================================
処理対象: 3個のファイル

処理中: test_docs/sample.md
  ✓ 完了

処理中: test_docs/guide.md
  ✓ 完了

処理中: test_docs/notes.md
  ✓ 完了

==================================================
処理完了: 成功 3件 / エラー 0件
```

## 処理の仕組み
### 文字数: 153

- Markdownファイル内の`##`で始まる見出しを検出
- 各セクションの本文（`##`見出しの次の行から、次の全ての見出しまで）の文字数をカウント
- `### 文字数:`の行が既にある場合は更新、ない場合は挿入
- スペース、改行、タブは文字数に含まれません

### 処理前のMarkdown

```markdown
## セクション1
### 文字数: 8

これは 本文です。

## セクション2
### 文字数: 42

もう一つのセクションです。
```

### 処理後のMarkdown

```markdown
## セクション1
### 文字数: 8

これは本文です。

## セクション2
### 文字数: 16

もう一つのセクションです。
```


## 作者
### 文字数: 6

sumomo

## ライセンス
### 文字数: 6

後で追加予定