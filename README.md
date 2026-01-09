# 💼 HRD 的黑匣子 (HRD's Blackbox)

> **版本**: v1.3 | **状态**: Production Ready | **核心**: 15年 HRD 经验数字化

**HRD 的黑匣子** 不是一个冷冰冰的 AI 工具，而是你职场晋升的**数字军师**。它复刻了一位拥有 15 年经验的资深 HRD（人力资源总监）的大脑，帮你揭秘招聘背后的潜规则。

## 核心价值 (The Blackbox Magic)

*   **🕵️‍♂️ 简历透视镜 (Resume Audit)**：像 HRD 一样审视你的简历，在 6 秒内找出让你被秒拒的致命伤。
*   **📝 智能 JD 生成器 (Smart JD Gen)**：[P1 战略] 输入老板的口语需求，一键生成标准岗位说明书 (JD) + 面试题库。
*   **🗣️ 面试官思维 (Interviewer Mind)**：不仅改简历，更教你如何像管理者一样思考。
*   **🚀 职场外挂 (Career Cheat)**：用信息差打破职场天花板。

### 技术栈 (Tech Stack)
*   **核心逻辑**: Python 3.9+
*   **Web 界面**: Streamlit
*   **AI 引擎**: 支持 DeepSeek / OpenAI / Anthropic
*   **文档解析**: pdfplumber, python-docx
*   **配置管理**: YAML + 环境变量

---

## 2. 安装指南 (Installation)

### 系统要求
*   Windows / macOS / Linux
*   Python 3.9 或更高版本
*   至少一个 LLM API Key (DeepSeek / OpenAI / Anthropic)

### 依赖安装
```bash
# 1. 进入项目目录
cd AI_Resume_Sniper

# 2. 创建虚拟环境 (可选)
python -m venv venv
# Windows 激活:
.\venv\Scripts\activate
# Mac/Linux 激活:
source venv/bin/activate

# 3. 安装依赖
pip install streamlit openai python-dotenv pdfplumber python-docx pyyaml

# 可选: Anthropic 支持
pip install anthropic
```

### 环境配置
1.  复制配置模板: `cp config/.env.example .env`
2.  编辑 `.env` 文件，添加 API Key:
    ```text
    DEEPSEEK_API_KEY="sk-your-key-here"
    # OPENAI_API_KEY="sk-your-key-here"  # 可选
    # ANTHROPIC_API_KEY="sk-ant-your-key-here"  # 可选
    ```

---

## 3. 使用说明 (Usage)

### 快速启动 (Web UI)
```bash
streamlit run src/web_ui.py
```
*   浏览器自动打开 `http://localhost:8501`

### 命令行使用 (Python API)
```python
from src.core.engine import create_engine

# 创建引擎
engine = create_engine()

# 单个简历分析
result = engine.analyze(
    resume_text="简历内容...",
    jd_text="职位描述...",
    persona="hrbp"  # 或 "coach"
)
print(result.report)
print(f"Score: {result.score}")

# 批量处理
results = engine.batch_analyze(
    resumes=["简历1", "简历2", "简历3"],
    jd_text="职位描述...",
    show_progress=True
)
```

### 功能模式详解

#### 1️⃣ 单人模式 (Single Mode)
*   **场景**: 深度精修一份简历。
*   **操作**: 上传/粘贴简历 + 上传/粘贴 JD -> 点击分析。
*   **输出**: 深度报告、红旗预警、STAR 重写建议。

#### 2️⃣ 批量简历匹配 (Batch Resumes)
*   **场景**: HR 筛选海量候选人。
*   **操作**:
    1.  粘贴目标 JD。
    2.  批量上传 N 份简历 (支持 PDF/DOCX)。
    3.  点击 "Analyze Batch Resumes"。
*   **输出**: 包含姓名、匹配分数的 CSV 表格，支持下载。

#### 3️⃣ 批量职位匹配 (Batch JDs)
*   **场景**: 求职者海投，寻找最匹配的职位。
*   **操作**:
    1.  粘贴个人简历。
    2.  批量上传 N 个 JD 文件。
    3.  点击 "Analyze Batch JDs"。
*   **输出**: 职位适配度排名，帮助优先投递高胜算职位。

---

## 4. 架构说明 (Architecture)

### 插件系统 (Plugin System)

```
AI_Resume_Sniper/
├── src/
│   ├── core/                    # 核心引擎
│   │   ├── engine.py            # 主引擎 (ResumeSniperEngine)
│   │   ├── config.py            # 配置管理
│   │   └── exceptions.py        # 异常定义
│   ├── interfaces/              # 抽象接口 (ABC)
│   │   ├── illm_provider.py     # LLM提供商接口
│   │   ├── idocument_parser.py  # 文档解析器接口
│   │   └── istorage.py          # 存储接口
│   ├── plugins/                 # 插件实现
│   │   ├── llm_providers/       # LLM提供商
│   │   │   ├── deepseek.py
│   │   │   ├── openai.py
│   │   │   └── anthropic.py
│   │   ├── document_parsers/    # 文档解析器
│   │   │   ├── pdf_parser.py
│   │   │   ├── docx_parser.py
│   │   │   └── text_parser.py
│   │   └── storage/             # 存储后端
│   │       ├── local_storage.py
│   │       └── memory_cache.py
│   └── web_ui.py                # Web界面
└── config/
    ├── config.yaml              # 主配置文件
    └── .env.example             # 环境变量模板
```

### 添加自定义插件

#### 1. 自定义 LLM Provider
```python
from src.interfaces.illm_provider import ILLMProvider, LLMResponse

class MyLLMProvider(ILLMProvider):
    @property
    def provider_name(self) -> str:
        return "my_provider"

    def chat(self, messages, **kwargs) -> LLMResponse:
        # 实现逻辑
        pass
```

#### 2. 自定义 Document Parser
```python
from src.interfaces.idocument_parser import IDocumentParser

class MyParser(IDocumentParser):
    @property
    def parser_name(self) -> str:
        return "my_parser"

    def parse(self, file_path) -> ParsedDocument:
        # 实现逻辑
        pass
```

#### 3. 自定义 Storage
```python
from src.interfaces.istorage import IStorage

class MyStorage(IStorage):
    @property
    def storage_name(self) -> str:
        return "my_storage"

    def save(self, key, value, ttl=None) -> bool:
        # 实现逻辑
        pass
```

---

## 5. 配置说明 (Configuration)

### 配置文件 (`config/config.yaml`)

```yaml
llm_providers:
  deepseek:
    enabled: true
    api_key_env: "DEEPSEEK_API_KEY"
    models:
      - name: "deepseek-chat"
        max_tokens: 16384
    default_model: "deepseek-chat"

  openai:
    enabled: false
    api_key_env: "OPENAI_API_KEY"
    models:
      - name: "gpt-4o"
        max_tokens: 16384
    default_model: "gpt-4o"

document_parsers:
  pdf:
    parser: "pdf"
    enabled: true
  docx:
    parser: "docx"
    enabled: true

storage:
  backend: "local"  # 或 "memory"
  cache_ttl: 3600   # 秒

analysis:
  default_persona: "hrbp"  # 或 "coach"
```

---

## 6. 开发指南 (Development)

### 添加新功能
1.  实现对应的抽象接口 (ABC)
2.  在 `plugins/` 目录下创建实现
3.  更新 `__init__.py` 注册插件
4.  (可选) 更新配置文件支持

### 测试
```bash
# 运行集成测试
python tests/integration_test.py
```

---

## 7. 许可证 (License)

MIT License

---

## 8. 更新日志 (Changelog)

### v1.3.0 (2026-01-05)
- ✨ **重大重构**: 插件化架构
- ✨ 新增多 LLM 支持 (OpenAI, Anthropic)
- ✨ 新增缓存系统 (本地/内存)
- ✨ 新增自动重试机制
- ✨ 新增 Persona 系统
- 📝 更新文档和配置

### v1.2.0 (之前版本)
- 批量处理功能
- 文档解析支持
- 基础 Web UI

---

> *Generated by AI Resume Sniper Project Team | v1.3 Plugin Architecture*
