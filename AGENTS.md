# AGENTS.md

## プロジェクト概要

Ollama File Organizerは、NAS・SMB・Windows共有などOSから参照可能なフォルダ内のファイルを、Ollamaで分類し、安全なバックエンド処理を通じて整理するシステムです。

## 最重要原則

1. 初期状態は `DRY_RUN=true`、`AUTO_PROCESSING=false` とする。
2. OllamaにOSコマンドや直接ファイル操作権限を与えない。
3. Ollamaに絶対パスを生成させない。
4. 実際の移動先は許可済みカテゴリテンプレートからバックエンドが解決する。
5. ルート外アクセス、パストラバーサル、シンボリックリンク脱出を拒否する。
6. 同名ファイルを上書きしない。
7. ファイル操作直前に状態とSHA-256を再確認する。
8. 変更時は関連テストを追加・更新する。
9. UTF-8をエンドツーエンドで使用し、日本語の文字化けを防ぐ。

## アーキテクチャ

- `backend/`: FastAPI / SQLAlchemy / Pydantic
- `frontend/`: Vue 3 / TypeScript / Vite / Vuetify 3
- `documents/`: 設計・運用ドキュメント
- `backend/app/ollama/`: Ollama向けシステムプロンプト

## コーディング規約

- Python 3.12+
- Pydantic v2
- SQLAlchemy 2.x
- 型ヒントを付与する。
- 例外はAPI境界で適切なHTTPエラーへ変換する。
- 秘密情報、文書全文、認証情報、個人情報を不用意にログへ出力しない。
- README、ドキュメント、Issue、PR、コミットメッセージは原則日本語を使用する。

## 変更前チェック

- `root_path` 外へ到達可能な経路がないか。
- Ollama出力を無検証で利用していないか。
- Dry Runを意図せず迂回していないか。
- Undo時にハッシュ検証を行っているか。
- 日本語パスとUTF-8を壊していないか。
