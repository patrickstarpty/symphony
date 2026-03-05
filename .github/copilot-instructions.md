# Symphony 项目开发规则

## 强制规则（必须遵守）

1. **及时更新 README** — 任何功能、CLI 参数、配置项、环境变量、依赖或使用方式的变更，必须同步更新 README.md。文档过时视为 bug。

2. **不破坏现有测试** — 每次修改后运行 `uv run pytest tests/ -v` 确认全部通过。

3. **新代码必须有测试** — 新增的函数、模块、行为至少要有一个测试覆盖。

4. **禁止硬编码密钥** — API key、token、密码等只能通过环境变量和 `.env` 管理，绝不写入代码。

5. **类型注解** — 所有新函数必须有参数和返回值的类型标注。

6. **使用 uv 管理依赖** — 添加依赖用 `uv add`，运行命令用 `uv run`，不使用 pip。

7. **错误处理** — 不静默吞异常，日志必须包含上下文（什么失败了、为什么、怎么修）。

8. **清理调试代码** — 不留 `print()`、`breakpoint()`、临时 workaround。

9. **遵守 .gitignore** — 不提交 `.env`、`.venv/`、`__pycache__/`、构建产物。

10. **向后兼容** — 修改公开接口（函数签名、CLI 参数、配置 key）必须更新所有调用方和文档。

## 代码风格

- Python 3.11+，使用 `from __future__ import annotations`
- 用 `structlog` 记录日志，不用 `print()`
- 异步优先，I/O 操作用 `async/await`
- 遵循现有代码风格和目录结构
- 注释写在意图不明显的地方
- 每个模块顶部有 docstring 说明用途

## 项目结构

- 源码在 `src/symphony/`
- 测试在 `tests/`
- 配置在 `pyproject.toml`
- 环境变量在 `.env`（不提交）
- 工作流定义在 `WORKFLOW.md`

## 常用命令

```bash
uv sync                              # 同步依赖
uv run pytest tests/ -v              # 运行测试
uv run python -m symphony ./WORKFLOW.md  # 启动 daemon
uv add <package>                     # 添加依赖
```
