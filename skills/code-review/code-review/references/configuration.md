# 配置說明

## 正式路徑：呼叫當下的 repo / process environment

`code-review` skill 的預設 runtime state/cache 路徑是呼叫當下 repo 內的 `.code-review/`。

建議從目標 repo 目錄執行 CLI，並以既有 process environment 或 repo-local `.env` 提供設定。不要把 runtime cache、viewer 輸出、session DB、vector DB 或 handoff 暫存檔寫到 `~/`、`/tmp`、`/temp` 或 repo 外目錄，除非使用者明確指定。

為避免和其他專案衝突，請使用 **project-unique** 的 `CODE_REVIEW_*` 命名。

### 建議的最小設定

```bash
# code-review skill runtime (authoritative global env)
CODE_REVIEW_PERSISTENCE_MODE=local-sqlite
CODE_REVIEW_SQLITE_ENABLED=true
CODE_REVIEW_SQLITE_PROJECT_STATE_DIR=.code-review

CODE_REVIEW_EMBEDDING_PROVIDER=bedrock
CODE_REVIEW_EMBEDDING_BEDROCK_REGION=us-west-2
CODE_REVIEW_EMBEDDING_BEDROCK_MODEL=amazon.titan-embed-text-v2:0
CODE_REVIEW_EMBEDDING_BEDROCK_DIMENSIONS=1024
CODE_REVIEW_EMBEDDING_BEDROCK_MAX_TOKENS=8192
```

### 如果你改用 OpenAI embeddings

```bash
CODE_REVIEW_EMBEDDING_PROVIDER=openai
CODE_REVIEW_EMBEDDING_OPENAI_API_KEY=your_openai_api_key
CODE_REVIEW_EMBEDDING_OPENAI_BASE_URL=https://api.openai.com/v1
CODE_REVIEW_EMBEDDING_OPENAI_MODEL=text-embedding-3-small
CODE_REVIEW_EMBEDDING_OPENAI_DIMENSIONS=1536
```

### 如果你改用 self-hosted embeddings

```bash
CODE_REVIEW_EMBEDDING_PROVIDER=self-hosted
CODE_REVIEW_EMBEDDING_SELF_HOSTED_BASE_URL=http://127.0.0.1:8000/v1
CODE_REVIEW_EMBEDDING_SELF_HOSTED_API_FORMAT=openai-compatible
CODE_REVIEW_EMBEDDING_SELF_HOSTED_MODEL=BAAI/bge-small-en-v1.5
CODE_REVIEW_EMBEDDING_SELF_HOSTED_DIMENSIONS=384
# Optional, only if your local endpoint requires auth.
CODE_REVIEW_EMBEDDING_SELF_HOSTED_API_KEY=local-token
```

這條路徑不以單一 local server 命名。`api_format=openai-compatible` 適合 OpenAI-compatible `/v1/embeddings`；`api_format=native-embed` 會呼叫 native `/api/embed`。如果端點不要求 auth，可以不設定 API key。

### ONNX embeddings 狀態

```bash
CODE_REVIEW_EMBEDDING_PROVIDER=onnx
CODE_REVIEW_EMBEDDING_ONNX_RUNNER_PATH=.agents/skills/code-review/scripts/embedding-runner
CODE_REVIEW_EMBEDDING_ONNX_MODEL_PATH=.agents/skills/code-review/assets/models/baai-bge-small-en-v1-5/model.onnx
CODE_REVIEW_EMBEDDING_ONNX_TOKENIZER_PATH=.agents/skills/code-review/assets/models/baai-bge-small-en-v1-5/tokenizer.json
CODE_REVIEW_EMBEDDING_ONNX_DIMENSIONS=384
CODE_REVIEW_EMBEDDING_ONNX_EXECUTION_PROVIDER=cpu
CODE_REVIEW_EMBEDDING_ONNX_NORMALIZE=true
```

`runner_path`、`model_path`、`tokenizer_path` 應優先使用相對路徑，讓同一份 repo/skill bundle 可在不同機器重用。上述三個 env var 可覆寫 config 檔中的相對路徑；packaged runner 應放在 `{the-skill}/scripts/` 或直接打包成 `{the-skill}/scripts/{executable}`，ONNX model/tokenizer artifacts 應放在 `{the-skill}/assets/`。open-source embedding model 轉 ONNX、tokenizer 匯出、manifest 與 CPU/GPU 驗證 handoff 由 repo-level `.agents/skills/opensource-embedding-onnx/` skill 處理。

目前 ONNX CPU path 已包含 bundled `embedding-runner` 與 BGE-small ONNX/tokenizer asset。Go CLI 會用 stdin/stdout JSON 呼叫 runner，避免主 Go binary 直接 link ONNX runtime；runner 會在需要時透過 isolated Python/`uvx` environment 載入 `onnxruntime`、`tokenizers`、`numpy`。CUDA path 需要依 `.agents/skills/opensource-embedding-onnx/references/gpu-validation-handoff.md` 在 GPU machine 上驗證後才能宣稱支援。它不會退回 mock 或雲端 provider。

Runner request stdin:

```json
{"text":"query","model_path":"model.onnx","tokenizer_path":"tokenizer.json","dimensions":384,"execution_provider":"cpu","normalize":true}
```

Runner response stdout:

```json
{"embedding":[0.1,0.2,0.3]}
```

### 如果你改用 Vertex embeddings

```bash
CODE_REVIEW_EMBEDDING_PROVIDER=vertex
CODE_REVIEW_EMBEDDING_VERTEX_PROJECT_ID=gcputil
CODE_REVIEW_EMBEDDING_VERTEX_LOCATION=us-central1
CODE_REVIEW_EMBEDDING_VERTEX_MODEL=gemini-embedding-2-preview
CODE_REVIEW_EMBEDDING_VERTEX_DIMENSIONS=1536
CODE_REVIEW_EMBEDDING_VERTEX_CREDENTIALS_FILE=/home/ga6653/.config/gcloud/gcputil-6ea3c7189bd4.json
```

這條路徑使用的是 Vertex 的 Gemini Embedding 2 系列，並沿用 service account / ADC 認證。

對目前這個 repo 來說，`1536` 維度是刻意選擇的相容值，因為現有 PostgreSQL pgvector schema 仍是 `vector(1536)`。

標準 ADC 相容路徑也仍可用：

```bash
GOOGLE_APPLICATION_CREDENTIALS=/home/ga6653/.config/gcloud/gcputil-6ea3c7189bd4.json
```

但對這個服務來說，preferred 的 unique env 名稱是 `CODE_REVIEW_EMBEDDING_VERTEX_CREDENTIALS_FILE`。

### 非 embedding LLM / chat model 設定

這一組設定主要影響：

- Go API server 的 generic LLM provider path
- `XPP_FALLBACK_ENABLED=true` 時的 X++ fallback model path

一般 hybrid `search-code` / embedding-backed `index` / `developer-routing` / `bounded-context` 主流程仍主要依賴 embedding provider，而不是這一組 chat model 設定。若任務明確要求 no-model / no-embedding，使用 `index --no-embeddings` 與 `search-code --graph-only`；這條路徑不需要 chat model 或 embedding provider。

要做 read-only inspection，直接用：

```bash
scripts/review-cli-<os>-<arch> llm-config
```

它只會輸出目前解析後的 non-embedding LLM config，不會碰 graph、vector、embedding 或 indexing flow。

注意：`llm-config` 檢查的是 **目前 CLI bootstrap 看到的設定**。如果你想避免 cwd / `config.yaml` 差異造成的混淆，請從目標工作目錄執行，或明確傳入 `--config <path>`。

要做真正的 active validation，直接用：

```bash
scripts/review-cli-<os>-<arch> doctor
```

`doctor` 會實際初始化目前設定的 non-embedding LLM provider，並送出一個最小 prompt 做 runtime 診斷。這和 `llm-config` 不同；前者是 active validation，後者只是 inspection。

```bash
# Preferred regular FM path in this workspace: direct AWS Bedrock
CODE_REVIEW_LLM_PROVIDER=bedrock
CODE_REVIEW_LLM_BEDROCK_REGION=us-west-2
CODE_REVIEW_LLM_BEDROCK_MODEL=minimax.minimax-m2.5
CODE_REVIEW_LLM_BEDROCK_TEMPERATURE=0.7
CODE_REVIEW_LLM_BEDROCK_MAX_TOKENS=4096

# Custom gateway example
CODE_REVIEW_LLM_PROVIDER=bedrock-gateway
CODE_REVIEW_LLM_GATEWAY_ENDPOINT=https://gateway.example.com/chat
CODE_REVIEW_LLM_GATEWAY_API_KEY=your_gateway_api_key
CODE_REVIEW_LLM_GATEWAY_USER_ID=agent-user
CODE_REVIEW_LLM_GATEWAY_MODEL=provider-model-id
CODE_REVIEW_LLM_GATEWAY_TIMEOUT_SECONDS=30
```

說明：

- **公司政策優先**：regular FM 以 AWS Bedrock 為主；這也是本 workspace 的預設偏好。
- **custom gateway current mode**：目前最需要 ready 的是這條 custom gateway 路徑。
- **custom gateway openai-compatible mode**：這可以作為未來準備方向，但在本 repo 內目前缺少明確測試情境，因此應標示為 **deferred**，不要把它寫成 generic `openai` provider 已可直接使用。

對目前已實作的 provider 路徑來說，優先設定 provider-specific 欄位：

- `bedrock` → `CODE_REVIEW_LLM_BEDROCK_*`
- `bedrock-gateway` → `CODE_REVIEW_LLM_GATEWAY_*`
- `vertex` → `CODE_REVIEW_LLM_VERTEX_*`

`CODE_REVIEW_LLM_MODEL` / `CODE_REVIEW_LLM_API_KEY` 保留作 generic contract，但不是目前 bedrock / gateway path 的主要設定欄位。

另外要注意：

- config schema 雖然宣告了 `openai` / `anthropic` 的 non-embedding LLM shape，但它們目前不是已實作的 provider path。
- **不要**因為底層 transport 可能相容 OpenAI shape，就在文件裡把 custom gateway current mode 說成 generic OpenAI provider support。

Vertex 建議設定：

```bash
CODE_REVIEW_LLM_PROVIDER=vertex
CODE_REVIEW_LLM_VERTEX_PROJECT_ID=gcputil
CODE_REVIEW_LLM_VERTEX_LOCATION=us-central1
CODE_REVIEW_LLM_VERTEX_MODEL=gemini-3.5-flash
CODE_REVIEW_LLM_VERTEX_CREDENTIALS_FILE=/home/ga6653/.config/gcloud/gcputil-6ea3c7189bd4.json
```

請依目標帳號實際可用的 Vertex model catalog 調整 `CODE_REVIEW_LLM_VERTEX_MODEL`；不要沿用舊範例 model 當作預設值。

標準 ADC 相容路徑也仍可用：

```bash
GOOGLE_APPLICATION_CREDENTIALS=/home/ga6653/.config/gcloud/gcputil-6ea3c7189bd4.json
```

但對這個服務來說，preferred 的 unique env 名稱是 `CODE_REVIEW_LLM_VERTEX_CREDENTIALS_FILE`。

Gateway path uses the project-scoped env names:

```bash
CODE_REVIEW_LLM_PROVIDER=bedrock-gateway
CODE_REVIEW_LLM_GATEWAY_ENDPOINT=...
CODE_REVIEW_LLM_GATEWAY_API_KEY=...
CODE_REVIEW_LLM_GATEWAY_USER_ID=...
CODE_REVIEW_LLM_GATEWAY_MODEL=...
CODE_REVIEW_LLM_GATEWAY_TIMEOUT_SECONDS=30
```

### 什麼情況才需要 Neo4j / PostgreSQL？

如果你現在走的是 `local-sqlite` graph/query path，**不需要**在 global env 裡設定 Neo4j 或 PostgreSQL。

### no-model / subscription-agent graph lane

Spec #62 adds a graph-only lane for situations where embedding models and pay-as-you-go provider APIs are disallowed:

```bash
CODE_REVIEW_PERSISTENCE_MODE=local-sqlite
CODE_REVIEW_SQLITE_ENABLED=true
scripts/review-cli-<os>-<arch> index <project-path> --no-embeddings
scripts/review-cli-<os>-<arch> search-code <project-path> "ProviderFallback" --graph-only
```

For richer semantic graph edges without repository-managed provider API calls, the active coding-agent session can write an `agent-graph-fragment/v1` JSON file and import it:

```bash
scripts/review-cli-<os>-<arch> graph fragment validate fragment.json --target <project-path>
scripts/review-cli-<os>-<arch> graph fragment apply fragment.json --target <project-path> --source-owned
```

This does not make vector search obsolete. Hybrid graphRAG remains the better path for natural-language semantic recall, cross-repo candidate discovery, and ranking by similarity.

### 模式選擇原則

- `local-sqlite`：單一 workspace / 本地專案工作。SQLite state 會放在 **workspace-relative** 的 `project_state_dir` 下面，預設是 `<workspace>/.code-review/`，不是單一全域 SQLite 檔案。
- `server-postgresql`：較大的 shared / multi-project runtime。這是另一個 persistence mode，不應和本地 workspace SQLite state 混在一起。

目前這個 repo 內的 project-local graph/query surfaces（例如 `search-code`、`developer-routing`、`bounded-context`）仍要求 `local-sqlite`，對 `server-postgresql` 會 fail closed；所以 `server-postgresql` 在這裡是治理上的 mode boundary，不是這些命令的直接替代路徑。

只有在你刻意切到 `server-postgresql` 或其他明確依賴外部 store 的流程時，才需要額外設定：

```bash
# Optional only
CODE_REVIEW_PERSISTENCE_MODE=server-postgresql
CODE_REVIEW_POSTGRES_DSN=postgresql://user:password@localhost:15432/code_review_db
```

如果你想自訂 local SQLite 檔名，也應該保持 **workspace-relative**：

```bash
CODE_REVIEW_SQLITE_PROJECT_STATE_DIR=.code-review
CODE_REVIEW_SQLITE_GRAPH_FILE=graph.sqlite
CODE_REVIEW_SQLITE_VECTOR_FILE=vector.sqlite
CODE_REVIEW_SQLITE_SESSION_FILE=session.sqlite
```

### local SQLite state 的版控建議

`local-sqlite` 不是「全部都 ignore」或「全部都 commit」的單一決策。Agent 應該先判斷檔案在 GraphRAG 流程中的角色；預設不要把 indexing 產物自動加入版控。

- `graph.sqlite` / `CODE_REVIEW_SQLITE_GRAPH_FILE` 指到的 graph DB（預設 `.code-review/graph.sqlite`）只有在 repo 明確要共享預建 GraphRAG graph，讓後續 agent 直接查詢或重用時，才應該用 Git LFS 版控，並在 `.gitattributes` 加上精準路徑規則。單次本機 indexing 產物仍應保持 ignored。
- `manifest.json` 如果是 graph DB 的 durable companion，描述 source corpus、schema/version、generation inputs、freshness policy 或 rebuild command，應該當一般文字檔版控；如果只是 runtime/cache manifest，應該 `.gitignore`。
- `status.json` 在本 skill 語境下預設視為 runtime/preflight/local registry 狀態，容易過期，應該 `.gitignore`；只有在 repo 明確規範它是 curated evidence，且最好放在非 runtime cache 路徑時才版控。
- `CODE_REVIEW_SQLITE_VECTOR_FILE` 指到的 vector DB 預設視為可重建的 provider/model-specific 產物，先 `.gitignore`；只有在 repo 明確需要固定 retrieval evidence，且已檢查大小、freshness、資料敏感性時，才考慮 Git LFS。
- `CODE_REVIEW_SQLITE_SESSION_FILE`、local registry、logs、tmp、cache、viewer runtime reports 預設 `.gitignore`。
- 不要把 `.env`、credential、API key、或機器特定絕對路徑 commit 進 repo。

具體判斷準則與 `.gitattributes` / `.gitignore` 範例見 `references/local-state-version-control.md`。

## native CLI 的讀取順序

published native CLI 現在會使用這個順序：

1. **既有 process environment**
2. **explicit env file**（只有在 `CODE_REVIEW_GLOBAL_ENV_FILE` 明確指定時才讀取）
3. **repo-local `.env`**：從呼叫當下的 repo root 讀取
4. **optional sibling fallback**：binary 同層 `.env`（只有在 authoritative runtime vars 皆未設定時才會使用）

也就是說，published bundle 不再依賴 retired Python wrapper / env-bridge 作為 runtime surface。

## `config.yaml` 的角色

Go CLI 仍支援 `--config <path>`，但 wrapper 不會自動指定一個 global `config.yaml`。

如果你有特殊需求，仍可手動傳入：

```bash
scripts/review-cli-<os>-<arch> search-code <artifact> <query> --config /path/to/config.yaml
```

對大多數 skill 使用情境，建議以 `CODE_REVIEW_*` env vars 為主，而不是依賴 skill 目錄裡的 `config.yaml`。

## local examples

Published native bundle 不再 shipping `.env.example*` 或 `config.yaml.example` 在 `scripts/` 內。
若需要 local sample settings，請直接參照本文件中的 env snippets，或在 repo source tree 內另行管理非 shipped 範例檔。

## Foundation model local hosts

Foundation-model settings are only needed for commands that already use LLM generation, such as LLM diagnostics or summarization paths. Do not configure FM just to use graph, vector, deterministic rerank, or local CPU rerank surfaces.

OpenAI-compatible local hosts can be selected through the existing LLM provider family:

```bash
# vLLM default base URL: http://localhost:8000/v1
export CODE_REVIEW_LLM_PROVIDER=vllm
export CODE_REVIEW_LLM_OPENAI_MODEL='<local-chat-model>'

# Ollama default base URL: http://localhost:11434/v1
export CODE_REVIEW_LLM_PROVIDER=ollama

# LM Studio default base URL: http://localhost:1234/v1
export CODE_REVIEW_LLM_PROVIDER=lm-studio
```

Override the default host when needed with `CODE_REVIEW_LLM_OPENAI_BASE_URL`.

## Model-backed rerank

Model-backed rerank is optional and separate from chat/embedding settings.

```bash
export CODE_REVIEW_RERANK_PROVIDER=bedrock
export CODE_REVIEW_RERANK_BEDROCK_REGION=us-east-1
export CODE_REVIEW_RERANK_BEDROCK_MODEL='arn:aws:bedrock:us-east-1::foundation-model/cohere.rerank-v3-5:0'
```

OpenAI-compatible local hosts use `/rerank` and share the `RERANK_OPENAI_*` config family:

```bash
# vLLM default base URL: http://localhost:8000/v1
export CODE_REVIEW_RERANK_PROVIDER=vllm
export CODE_REVIEW_RERANK_OPENAI_MODEL='bge-reranker-v2-m3'

# Ollama default base URL: http://localhost:11434/v1
export CODE_REVIEW_RERANK_PROVIDER=ollama

# LM Studio default base URL: http://localhost:1234/v1
export CODE_REVIEW_RERANK_PROVIDER=lm-studio

# Any OpenAI-compatible rerank host
export CODE_REVIEW_RERANK_PROVIDER=openai
export CODE_REVIEW_RERANK_OPENAI_BASE_URL='http://localhost:8000/v1'
export CODE_REVIEW_RERANK_OPENAI_API_KEY='local-key-if-required'
```

Small local CPU rerank is available only for bounded candidate sets:

```bash
export CODE_REVIEW_RERANK_PROVIDER=local-cpu
export CODE_REVIEW_RERANK_MAX_DOCUMENTS=32
```

Use `rerank-config` for passive inspection and `rerank-doctor` for an active provider probe. Vertex and custom gateway rerank providers remain unsupported; regular FM support for those providers does not imply rerank support.
