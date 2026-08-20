# Dify 适配

将 `adapters/generic/system-prompt.md` 用作 Agent 指令。把 `tool-contract.json` 的五个操作实现为 Tool 插件，或在 Workflow 中封装为五个可调用工具。

建议让 Agent 负责解释和确认，把标准化、Base 完整分页、upsert、对象回读和第二次幂等验证放入确定性的 Workflow 节点。写工具必须把 `approved`、来源指纹、计划 ID 和快照 ID 作为必填参数并在后端复核。

Dify 不能仅靠导入本仓库就获得飞书权限；还需配置飞书应用凭据、最小权限和可访问的 Base 范围。凭据使用平台密钥管理，不写入提示词或知识库。
