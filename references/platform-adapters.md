# 运行时适配与选择

## 核心原则

业务规则、人工决策门和验收标准位于根 `SKILL.md` 与 `references/` 中；适配器只负责把平台工具映射到统一能力，不得弱化安全规则。

统一能力分为五个粗粒度操作：

1. `inspect_ogsm_source`：读取、标准化和预检来源。
2. `resolve_people`：解析负责人候选，不自动猜测歧义人员。
3. `inspect_target_base`：完整读取目标 Base 和配置。
4. `execute_approved_ogsm_plan`：只执行已确认、带来源指纹的固定计划。
5. `verify_ogsm_base`：回读并进行第二次 upsert 验收。

## 适配矩阵

| 运行时 | 使用入口 | 工具接入方式 | 可直接导入本目录 |
| --- | --- | --- | --- |
| 支持 Agent Skills 的运行时 | 根 `SKILL.md` | 平台原生工具或 MCP | 视平台规范而定 |
| WorkBuddy | `adapters/workbuddy/runtime.md` | GitHub 自主安装或通用 Skill ZIP + 连接器、MCP 或 CLI | 是，与其他兼容平台共用同一 ZIP |
| 飞书 Aily | `adapters/feishu-aily/deployment.md` | Agent Skill 负责对话调度；工作流或自定义连接器后端负责稳定执行 | 否，需粘贴提示词、配置字段并绑定 5 个粗粒度操作 |
| Codex | `adapters/codex/runtime.md` | lark 系列技能和 CLI | 是 |
| Dify | `adapters/dify/runtime.md` | Tool 插件 + Workflow | 否 |
| 扣子 | `adapters/coze/runtime.md` | 插件或工作流 | 否 |
| FastGPT / MaxKB | `adapters/fastgpt-maxkb/runtime.md` | HTTP 工具或工作流 | 否 |
| 其他函数调用 Agent | `adapters/generic/` | JSON 契约对应的函数或 API | 否 |

## 安装方式优先级

1. 把 `https://github.com/minvast/lark-build-ogsm-board` 交给 Agent，让它从仓库根目录安装并验证。
2. Agent 不能联网下载或没有安装权限时，上传通用包 `lark-build-ogsm-board.zip`。
3. 平台不支持 Agent Skills 文件结构时，不强行导入 ZIP，改用对应的提示词、工具契约或工作流适配器。

WorkBuddy 与 Codex 共用同一份 Skill 内容，不维护 WorkBuddy 专用包。平台界面是否支持直接粘贴仓库 URL 由平台版本决定；Agent 也可以通过下载或克隆仓库完成安装。

## 能力降级

- 只有文件读取和大模型：输出预检与待确认事项，禁止写入。
- 能读 Base 但不能写：输出差异和搭建计划，禁止声称完成。
- 能写但不能完整回读：禁止执行写入，因为无法完成幂等验收。
- 无人员目录：保留负责人原文，人员字段留空并列为未解决事项。
- 无持久会话状态：每次操作都显式携带 `source_fingerprint`、`plan_id` 和确认摘要。

## 后端边界

对话 Agent 负责收集输入、解释预检、提出决策问题和展示验收结果。真正的 Base 写入由可审计的工具、连接器或工作流完成。写入后端必须自行校验：

- `approved=true` 且 `approval_summary` 与计划一致；
- `source_fingerprint` 和 `plan_id` 未改变；
- 当前 Base 状态仍与写前检查一致；
- 删除操作携带用户批准的固定 record ID 清单。

提示词中的“已确认”不能替代后端校验。

飞书 Aily 适配时还应把模型可推断字段与原样传递字段分开：用户来源、范围和选择可由模型理解；指纹、计划 ID、快照 ID 和操作日志 ID 只能来自前序操作。模型上下文只保留摘要和引用，不载入完整规范数据或原始 API 响应。
