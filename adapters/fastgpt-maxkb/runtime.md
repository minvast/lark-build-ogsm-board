# FastGPT / MaxKB 适配

将 `adapters/generic/system-prompt.md` 作为应用系统提示词。通过 HTTP 工具、API 节点或工作流把 `tool-contract.json` 的五个统一操作接入一个受控后端。

若平台一次只能调用简单 HTTP 接口，优先让后端提供五个粗粒度端点，不要让模型自行编排大量底层飞书 OpenAPI。后端负责分页、重试、幂等、确认状态和日志审计。

平台没有持久会话状态时，每次请求显式传递来源指纹、计划 ID、快照 ID 和确认摘要。没有完整回读或后端确认校验时，只启用预检和计划接口。
