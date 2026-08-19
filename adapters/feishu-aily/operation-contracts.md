# 飞书 Aily 操作契约

在一个 Agent Skill 中添加以下五个粗粒度操作。操作名称必须与提示词一致。保持操作数量精简，把多步 Base 写入封装在工作流或自定义连接器后端中，避免把每个 Base API 都暴露为一个 Agent 操作。

## 1. inspect_ogsm_source

只读。输入 `source`、可选 `scope` 和 `topology_hint`。输出来源指纹、规范记录数、覆盖率、负责人和日期问题、重复项、过宽策略、阻断问题、待确认事项及规范数据引用。

## 2. resolve_people

只读。输入唯一姓名原文列表和来源指纹。每个姓名输出 `zero`、`unique` 或 `ambiguous`，唯一匹配时带可写入的人员标识；不得返回自动选择后的歧义人员。

## 3. inspect_target_base

只读。输入目标 Base 列表、表名和 upsert 键。必须完成分页，并输出 `snapshot_id`、`has_more`、总数、空键、重复键、计划外记录和字段/视图/仪表盘/工作流配置。

## 4. execute_approved_ogsm_plan

写操作。输入 `plan_id`、`source_fingerprint`、`snapshot_id`、`approval_summary` 和 `approved`。后端必须拒绝以下请求：

- `approved` 不为 `true`；
- 指纹、计划或快照已变化；
- 目标出现新的空键、重复键或计划外记录；
- 请求包含未经单独授权的删除；
- 请求启用工作流但没有明确的启用授权和接收人。

执行顺序为字段与选项、upsert 记录、视图、仪表盘、默认关闭的工作流。返回每个目标的创建/更新数、对象结果、工作流状态和操作日志 ID。

## 5. verify_ogsm_base

只读为主，但允许执行同一计划的第二次幂等 upsert。输入计划、目标和操作日志 ID。输出完整回读总数、唯一键数、第二次 upsert 的创建/更新数、对象配置、工作流状态、问题和总体验收结果。`second_upsert_created` 必须为 0。

## 错误约定

所有操作失败时返回结构化 `error_code`、`message`、`retryable` 和 `details`。超时或响应不明时不得自动补写；先回读目标状态。操作日志不得记录飞书访问令牌或用户敏感凭证。
