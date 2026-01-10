# TalentOS 部署指南

本指南将帮助你将项目部署为微信小程序后端，并发布小程序。

## 架构概览
*   **服务端**: Python FastAPI (运行在你的云服务器上)，提供 `/analyze` 接口。
*   **客户端**: 微信小程序 (运行在用户手机微信里)，调用服务端接口。

---

## 第一部分 (Windows 本地版): 使用 Cloudflare Tunnel 部署 (推荐)

这是最简单的方式，无需购买云服务器，无需配置 Nginx，无需公网 IP。

### 1. 准备工作
确保你已经在本地安装了 `cloudflared`。

### 2. 一键配置 Tunnel
运行项目根目录下的自动化脚本：
```powershell
.\setup_tunnel.ps1
```
按照脚本提示操作：
1.  如果没有登录，会自动打开浏览器让你登录 Cloudflare。
2.  自动创建名为 `talentos-tunnel` 的 Tunnel。
3.  自动配置路由：
    *   `bmwuv.com/` -> 本地 React Frontend (8501)
    *   `bmwuv.com/analyze` -> 本地 FastAPI (8000)

### 3. 启动服务
你需要同时启动三个进程 (建议在三个不同的终端窗口中运行)：

**终端 1 (Frontend):**
```powershell
cd frontend-web
pnpm dev
```

**终端 2 (FastAPI 后端):**
```powershell
python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8000
```

**终端 3 (Cloudflare Tunnel):**
```powershell
cloudflared tunnel run talentos-tunnel
```

### 4. 验证
*   访问 `https://bmwuv.com` -> 应该看到 TalentOS 网页版。
*   小程序调用 `https://bmwuv.com/analyze` -> 应该能正常分析。

---

## 第二部分 (云服务器版): 常规 Nginx 部署

假设你已经购买了云服务器并解析了域名 `bmwuv.com`。

### 1. 准备环境
确保服务器上安装了 Python 3.9+。将本项目代码上传到服务器。

### 2. 安装依赖
在服务器项目根目录下运行：
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
确保服务器上有 `.env` 文件，并包含有效的 API Key：
```env
DEEPSEEK_API_KEY="你的key"
# 或
OPENAI_API_KEY="你的key"
```

### 4. 启动 API 服务
使用 `uvicorn` 启动服务。建议使用 `nohup` (Linux) 或后台运行，确保断开 SSH 后服务不停止。

**测试运行 (前台):**
```bash
python -m uvicorn src.api_server:app --host 0.0.0.0 --port 8000
```

**生产运行 (Linux 示例):**
```bash
nohup python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8000 > api.log 2>&1 &
```

### 5. 配置域名与 HTTPS (Nginx) - 进阶版 (同时支持小程序和网页)
为了让 `bmwuv.com` 既能服务小程序 (API)，又能让普通用户直接访问网页版 (Streamlit)，建议如下配置 Nginx：

1.  **启动 Streamlit (网页版):**
    ```bash
    nohup streamlit run src/web_app.py --server.port 8501 --server.address 127.0.0.1 > web.log 2>&1 &
    ```

2.  **启动 FastAPI (API 服务):**
    ```bash
    nohup python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8000 > api.log 2>&1 &
    ```

3.  **Nginx 配置示例:**
    ```nginx
    server {
        listen 443 ssl;
        server_name bmwuv.com;

        ssl_certificate /path/to/your/cert.pem;
        ssl_certificate_key /path/to/your/key.pem;

        # 1. 网页版 (Streamlit) - 默认访问路径
        location / {
            proxy_pass http://127.0.0.1:8501;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Streamlit WebSocket 支持 (必须配置)
        location /_stcore/stream {
            proxy_pass http://127.0.0.1:8501/_stcore/stream;
            proxy_http_version 1.1;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        # 2. API 接口 (供小程序和网页调用)
        # 注意: 如果网页版直接调用 Python 内部函数，其实不需要暴露 /analyze 给网页，
        # 但小程序必须用这个。
        location /analyze {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /health {
            proxy_pass http://127.0.0.1:8000;
        }
    }
    ```

---

## 第二部分：微信小程序发布

### 1. 下载微信开发者工具
前往 [微信官方文档](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html) 下载并安装。

### 2. 导入项目
1.  打开微信开发者工具。
2.  点击“导入项目”。
3.  目录选择本项目下的 `wx_mini_program` 文件夹。
4.  AppID 填写你注册的小程序 AppID。

### 3. 配置服务器域名
在代码 `pages/index/index.js` 中，找到 `API_URL`：
```javascript
// 生产环境
const API_URL = 'https://bmwuv.com/analyze';
```
确保你的小程序后台 (mp.weixin.qq.com) -> 开发 -> 开发管理 -> 服务器域名中，`uploadFile` 和 `request` 合法域名已添加 `https://bmwuv.com`。

### 4. 调试与上传
*   **本地调试**: 如果还没配置好 HTTPS，可以在开发者工具详情里勾选“不校验合法域名”，并将 URL 改为 `http://localhost:8000/analyze` (如果是在本机运行服务端)。
*   **上传**: 测试无误后，点击开发者工具右上角的“上传”，然后在小程序后台提交审核。

---

## 常见问题
1.  **上传文件失败**: 检查 Nginx 配置中 `client_max_body_size` 是否足够大 (建议 10M+)。
2.  **API 报错 500**: 检查服务器 `api.log`，通常是 API Key 无效或文件解析失败。
