# mcp-bsc

조직성과 관리표를 기반으로 개인성과 관리표를 자동 작성하는 **MCP(Model Context Protocol) 서버**입니다.

로컬 Obsidian 볼트의 업무기록(.md)과 조직성과관리표(.xlsx)를 읽어 로컬 LLM(Ollama)으로 분석한 뒤, 개인성과관리표 xlsx를 자동으로 생성합니다.

---

## 주요 기능

| MCP 도구 | 설명 |
|---|---|
| `list_work_records` | 허용 경로 내 `.md` 파일 목록 반환 |
| `read_work_record` | 특정 `.md` 파일 내용 반환 (경로 보안 검증 포함) |
| `read_org_performance_sheet` | 조직성과관리표 xlsx 파싱 |
| `generate_personal_performance_sheet` | 업무기록 + 조직성과관리표 → 개인성과관리표 xlsx 생성 |
| `analyze_work_records_with_llm` | Ollama LLM으로 업무기록을 성과 항목에 매핑 |

---

## 설치 방법

### 요구사항

- Python 3.11 이상
- [Ollama](https://ollama.ai) 설치 및 실행 중

### pip로 설치

```bash
git clone https://github.com/ellen310/mcp-bsc.git
cd mcp-bsc
pip install -e .
```

### uv로 설치 (권장)

```bash
git clone https://github.com/ellen310/mcp-bsc.git
cd mcp-bsc
uv sync
```

---

## 환경변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성하고 값을 수정합니다.

```bash
cp .env.example .env
```

`.env` 파일 내용:

```dotenv
# 업무기록 .md 파일이 있는 기본 경로 (이 경로 하위에만 접근 허용)
ALLOWED_BASE_PATH=/Users/ellen/Library/Mobile Documents/iCloud~md~obsidian/Documents/유비온

# Ollama 서버 주소
OLLAMA_BASE_URL=http://localhost:11434

# 사용할 Ollama 모델명
OLLAMA_MODEL=llama3

# 생성된 개인성과관리표가 저장될 디렉토리
OUTPUT_DIR=./output
```

---

## Ollama 설치 및 모델 준비

1. [ollama.ai](https://ollama.ai)에서 Ollama를 다운로드하여 설치합니다.
2. `llama3` 모델을 받습니다:

```bash
ollama pull llama3
```

3. Ollama가 실행 중인지 확인합니다:

```bash
ollama serve
```

---

## 템플릿 xlsx 생성

조직성과관리표 및 개인성과관리표 샘플 템플릿을 생성합니다:

```bash
python scripts/create_templates.py
```

실행 후 `templates/` 디렉토리에 아래 파일이 생성됩니다:

- `templates/org_performance_template.xlsx` — 조직성과관리표 샘플 (헤더 + 예시 데이터)
- `templates/personal_performance_template.xlsx` — 개인성과관리표 빈 양식

---

## Claude Desktop 연동 설정

`~/Library/Application Support/Claude/claude_desktop_config.json` 파일에 아래 내용을 추가합니다:

```json
{
  "mcpServers": {
    "mcp-bsc": {
      "command": "mcp-bsc",
      "env": {
        "ALLOWED_BASE_PATH": "/Users/ellen/Library/Mobile Documents/iCloud~md~obsidian/Documents/유비온",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3",
        "OUTPUT_DIR": "./output"
      }
    }
  }
}
```

> `uv`를 사용하는 경우 `"command"` 를 `"uv"` 로, `"args"` 를 `["run", "mcp-bsc"]` 로 설정합니다.

---

## MCP 도구 사용 방법

### 1. 업무기록 목록 조회

```
list_work_records
```

허용 경로 하위의 모든 `.md` 파일 경로를 JSON 배열로 반환합니다.

### 2. 특정 업무기록 읽기

```
read_work_record(file_path="/path/to/record.md")
```

### 3. 조직성과관리표 읽기

```
read_org_performance_sheet(xlsx_path="/path/to/org_performance.xlsx")
```

### 4. 개인성과관리표 자동 생성

```
generate_personal_performance_sheet(
    org_xlsx_path="/path/to/org_performance.xlsx",
    output_path="/path/to/output/personal.xlsx"
)
```

- 허용 경로 내 모든 `.md` 업무기록을 읽어 조직성과 항목과 매핑합니다.
- Ollama LLM을 사용해 달성내용과 근거자료를 자동 작성합니다.
- `output_path`를 생략하면 `OUTPUT_DIR`에 타임스탬프 이름으로 저장됩니다.

### 5. LLM 직접 분석

```
analyze_work_records_with_llm(
    work_records_text="업무기록 텍스트...",
    org_items_json='[{"category":"...", "item":"...", ...}]'
)
```

---

## xlsx 양식 설명

### 조직성과관리표 (`org_performance_template.xlsx`)

| 열 | 항목 |
|---|---|
| A | 카테고리 |
| B | 성과항목 |
| C | 지표 |
| D | 목표치 |
| E | 가중치 |

### 개인성과관리표 (`personal_performance_template.xlsx`)

| 열 | 항목 |
|---|---|
| A | 카테고리 |
| B | 성과항목 |
| C | 지표 |
| D | 목표치 |
| E | 달성내용 |
| F | 근거자료 |
| G | 점수 |

---

## 프로젝트 구조

```
mcp-bsc/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── pyproject.toml
├── src/
│   └── mcp_bsc/
│       ├── __init__.py
│       ├── server.py           # MCP 서버 진입점 및 tool 등록
│       ├── config.py           # 환경변수 로드 및 경로 보안 검증
│       ├── file_reader.py      # .md 파일 읽기 (경로 제한 적용)
│       ├── xlsx_handler.py     # xlsx 읽기/쓰기
│       ├── llm_client.py       # Ollama LLM 클라이언트
│       └── performance_mapper.py  # 성과 매핑 로직
├── scripts/
│   └── create_templates.py     # 샘플 xlsx 템플릿 생성
├── templates/
│   ├── org_performance_template.xlsx       # (scripts/create_templates.py 실행 후 생성)
│   └── personal_performance_template.xlsx  # (scripts/create_templates.py 실행 후 생성)
└── tests/
    ├── __init__.py
    ├── test_config.py
    ├── test_file_reader.py
    ├── test_xlsx_handler.py
    └── test_llm_client.py
```

---

## 라이선스

MIT
