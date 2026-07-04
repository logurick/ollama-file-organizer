# Ollama File Organizer

Ollamaを「判断役」、FastAPIバックエンドを「安全な実行役」として分離した、ローカルAIファイル整理システムです。NAS、SMB共有、Windows共有フォルダなど、OSから参照可能なパスを対象にします。

> [!WARNING]
> 初回は必ず `DRY_RUN=true`、`AUTO_PROCESSING=false` のまま確認してください。

## 現在の実装

- FastAPI + SQLAlchemy + SQLite
- Ollama `/api/chat` 連携
- JSON Schemaによる構造化分類
- PDF / DOCX / XLSX / TXT / Markdown / CSV / JSONの本文抽出
- ファイル名ルールを先に使うハイブリッド分類
- SHA-256計算
- パストラバーサル対策
- 許可ルート外アクセス拒否
- シンボリックリンク脱出対策
- カテゴリ別保存先テンプレート
- Dry Run対応のファイル移動サービス
- 同名上書き回避
- SHA-256検証付きUndoサービス
- Vue 3 + Vite + Vuetify 3 管理画面
- Docker Compose

## 安全設計

Ollamaにはファイル操作権限を与えません。AIは `category_id`、信頼度、要約、タグ、ファイル名候補などを返し、実際の保存先はバックエンド側の許可済みテンプレートから決定します。

```text
Network Share / NAS / SMB
        |
        v
File Scanner / Metadata
        |
        +--> Rule Engine
        |
        v
Content Extractor
        |
        v
Ollama Structured Classification
        |
        v
Pydantic Validation
        |
        v
Destination Resolver
        |
        v
Path Safety Validator
        |
        +--> Dry Run
        +--> File Operation
        +--> History / Undo
```

## 必要環境

- Docker / Docker Compose
- または Python 3.12+ / Node.js 22+
- Ollama
- 利用するOllamaモデル

## Ollama準備

例:

```bash
ollama pull qwen3:8b
ollama serve
```

`.env`:

```dotenv
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen3:8b
DRY_RUN=true
AUTO_PROCESSING=false
```

別サーバー上のOllamaも指定できます。

```dotenv
OLLAMA_BASE_URL=http://192.168.1.50:11434
```

## Docker起動

```bash
cp .env.example .env
docker compose up -d --build
```

管理画面:

```text
http://localhost:8080
```

API:

```text
http://localhost:8080/api/health
```

## ネットワーク共有

アプリ自身がSMB認証やマウントを担当するのではなく、OSまたはDockerホスト側で利用可能にしたパスを渡します。

Linux例:

```yaml
services:
  backend:
    volumes:
      - /mnt/nas/share:/data/share
```

Windowsネイティブ実行では次のようなパスを想定しています。

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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 初回運用

1. `.env.example` を `.env` へコピーする。
2. `DRY_RUN=true` を確認する。
3. `AUTO_PROCESSING=false` を確認する。
4. 小規模なテストフォルダから検証する。
5. AI分類と保存先候補を確認する。
6. 十分な検証後に自動化範囲を拡張する。

## API

現在のMVP基盤では以下を提供します。

- `GET /api/health`
- `GET /api/ollama/status`
- `POST /api/ollama/test`
- `GET /api/files`
- `GET /api/categories`
- `GET /api/dashboard`

監視フォルダのスキャン、承認キュー、高信頼度自動処理はサービス層を基盤として段階的にAPIへ公開します。

## 制限事項

- OCR未実装です。
- 認証・権限管理はMVP未実装です。インターネットへ直接公開しないでください。
- リアルタイム監視は未実装です。
- Mattermost / Obsidian / RAG連携は今後の拡張ポイントです。

## テスト

```bash
cd backend
pytest
```

## 開発ルール

`AGENTS.md` を参照してください。README、ドキュメント、Issue、PR、コミットメッセージは原則日本語で運用します。
