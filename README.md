# Ollama File Organizer

Ollamaを「判断役」、FastAPIバックエンドを「安全な実行役」として分離した、ローカルAIファイル整理システムです。NAS、SMB共有、Windows共有フォルダなど、OSから参照可能なパスを対象にします。

> [!WARNING]
> 初回は必ず `DRY_RUN=true`、`AUTO_PROCESSING=false` のまま確認してください。MVPではファイル削除機能を実装しません。

## 特徴

- Ollamaによる構造化JSON分類
- PDF / DOCX / XLSX / TXT / Markdown / CSV / JSONの本文抽出
- 複数監視フォルダ
- SHA-256による変更・重複検知
- 許可ルート外への移動拒否
- パストラバーサル対策
- シンボリックリンク脱出対策
- Dry Run
- 同名上書き禁止
- 操作履歴と安全なUndo基盤
- Vue 3 + Vuetify 3 管理画面

## アーキテクチャ

```text
Network Share / NAS / SMB
        |
        v
File Scanner
        |
        v
Content Extractor
        |
        v
Ollama Structured Classification
        |
        v
Validated Decision
        |
        v
Destination Resolver
        |
        v
Path Safety Validator
        |
        +--> Dry Run
        +--> Approval / Hold
        +--> Future Auto Processing
        |
        v
File Operation / Audit / Undo
```

Ollamaはファイル操作を行いません。分類結果には `category_id` などの論理値だけを返し、実際の保存先はバックエンド側のカテゴリテンプレートから決定します。

## 必要環境

- Docker / Docker Compose
- または Python 3.12+ / Node.js 22+
- Ollama
- 使用するOllamaモデル

## Ollama準備

例:

```bash
ollama pull qwen3:8b
ollama serve
```

`.env` の設定例:

```dotenv
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen3:8b
```

Ollamaが別サーバーの場合:

```dotenv
OLLAMA_BASE_URL=http://192.168.1.50:11434
```

## Docker起動

```bash
cp .env.example .env
docker compose up -d --build
```

ブラウザ:

```text
http://localhost:8080
```

API:

```text
http://localhost:8080/api/health
```

## 共有フォルダの渡し方

### Linux

OS側でSMBをマウントしてからコンテナへ渡します。

```yaml
services:
  backend:
    volumes:
      - /mnt/nas/share:/data/share
```

アプリ側では例として次を登録します。

```text
root_path: /data/share
inbox_path: /data/share/未整理
```

### Windows

Docker Desktopで共有可能なホストパスをbind mountしてください。UNCパスを直接アプリへ渡すより、Dockerから安定して見えるパスへマウントする運用を推奨します。

ネイティブ実行の場合は以下のようなパスも想定しています。

```text
\\NAS\share
Z:\share
```

## ローカル開発

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Windows PowerShellでは仮想環境有効化コマンドを環境に合わせて変更してください。

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 初回運用

1. `.env` を作成する。
2. `DRY_RUN=true` を確認する。
3. `AUTO_PROCESSING=false` を確認する。
4. 監視フォルダを登録する。
5. 手動スキャンする。
6. AI分類結果と移動先候補を確認する。
7. 十分な検証後に自動化範囲を拡張する。

## Dry Run

Dry Runでは操作履歴候補を記録できますが、実ファイルは移動しません。初期設定は常にDry Runです。

## Undo

実移動済み操作では次を確認してから元へ戻します。

- 移動後ファイルが存在すること
- SHA-256が移動時と一致すること
- 元位置に同名ファイルが存在しないこと

危険な場合はUndoを拒否します。

## セキュリティ

- ファイル削除なし
- Ollamaへ直接ファイル操作権限を与えない
- Ollamaへ絶対パスを生成させない
- JSON Schemaで分類応答を検証
- 文書本文中のPrompt Injectionを命令として扱わない
- ルート外パスを拒否
- シンボリックリンク経由の脱出を拒否
- 同名上書きなし
- 操作直前のSHA-256再検証

詳細は `documents/security.md` を参照してください。

## 制限事項

- OCRは未実装です。スキャンPDFはテキスト抽出不能になる場合があります。
- リアルタイム監視は設計項目のみで、MVPでは手動スキャン中心です。
- 自動整理実行フローは安全性検証を優先し、段階的に実装します。
- Mattermost / Obsidian / RAG連携は拡張ポイントです。
- 認証・ユーザー権限管理はMVP未実装です。インターネットへ直接公開しないでください。

## テスト

```bash
cd backend
pytest
```

## ロードマップ

- 承認キューUI
- カテゴリ変更とファイル名候補編集
- 高信頼度の自動処理
- Watchdogによるリアルタイム監視
- Mattermost通知
- Obsidian Markdown生成
- Ollama Embeddings / pgvector / Qdrant連携
- PostgreSQL対応とAlembic移行
- 認証・ロール管理

## ライセンス

未設定です。公開・配布方針に合わせて追加してください。
