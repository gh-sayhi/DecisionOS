# DecisionOS

**AI Decision Operating System** — 面向重大业务决策的企业级 AI 顾问。

梳理问题、推演取舍，输出可给管理层使用的结构化决策报告。

---

## 核心功能

| 功能 | 说明 |
|---|---|
| **追问机制** | 提交决策后 AI 追问 3-5 个关键问题，收集深度上下文后再生成报告 |
| **Pack 差异化评分** | 7 个行业 Pack（Product/Startup/Marketing/Content/Hiring/Investment/Custom），各有独立评分模型 |
| **案例对标** | 内置 26 个经典商业案例，AI 自动匹配相似案例佐证推荐 |
| **行动清单** | 报告末尾输出具体可执行的"明天做什么" |
| **用户反驳** | 对报告结论有异议可反馈，AI 重新评估局部更新 |
| **导出** | 支持 PDF / Markdown / 一键复制 |
| **中英文** | 一键切换 |

---

## License & Pricing

DecisionOS 采用 **Open Core** 模式：

| 功能 | 开源免费版 | 企业付费版 |
|---|---|---|
| 7 个行业 Pack | ✅ | ✅ |
| 追问机制 | ✅ | ✅ |
| 基础评分引擎（关键词匹配） | ✅ | ✅ |
| 26 个内置商业案例 | ✅ | ✅ |
| 报告导出（Markdown） | ✅ | ✅ |
| 中英文切换 | ✅ | ✅ |
| **LLM 真实评分** | ❌ | ✅ |
| **自定义 Pack** | ❌ | ✅ |
| **私人案例库** | ❌ | ✅ |
| **团队协作 / SSO** | ❌ | ✅ |
| **飞书 / 企微 / 钉钉集成** | ❌ | ✅ |
| **PDF 增强排版** | ❌ | ✅ |

开源版：AGPL v3 — 可自由使用、修改、分发。
企业版：付费，闭源。如需试用请联系。

---

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8001
```

### 前端

```bash
cd frontend
pnpm install
pnpm dev
```

打开 http://127.0.0.1:3000

---

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Next.js 16 + TypeScript |
| 后端 | Python FastAPI |
| 评分引擎 | RICE / 自定义决策框架 |
| 案例库 | 26 个商业案例，向量匹配 |
| 导出 | ReportLab (PDF) |

---

## License

Private — © 2026 gh-sayhi. All rights reserved.
