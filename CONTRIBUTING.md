# 贡献指南

感谢你考虑为 DecisionOS 贡献代码！

## 如何开始

1. Fork 本仓库
2. 克隆到本地
3. 按照 README 的快速启动步骤运行
4. 创建新分支：`git checkout -b feature/你的功能名`

## 开发流程

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8001

# 前端
cd frontend
pnpm install
pnpm dev
```

## 提交 Pull Request

- 确保代码通过 TypeScript 编译：`npx tsc --noEmit`
- 在 PR 描述中说明改动内容和原因
- 如果是新功能，请附上使用场景说明

## 问题反馈

遇到 Bug 或有功能建议，请提交 Issue。
