# 飞书 Aily 操作契约

在一个 Agent Skill 中只暴露以下五个粗粒度操作。名称必须与提示词完全一致；每个操作支持批量目标。复杂的 Base API 编排放在工作流或后端，不要继续拆成大量 Agent 操作。

## 通用返回结构

五个操作统一返回以下顶层字段，便于 Aily 稳定判断下一步：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ok` | boolean | 操作是否得到可信结果；未知或部分响应必须为 `false` |
| `status` | string | `ready`、`needs_confirmation`、`blocked`、`completed`、`unknown` 之一 |
| `summary` | string | 给业务用户看的短结论，不含技术日志 |
| `requires_user_confirmation` | boolean | 是否必须停止并询问用户 |
| `confirmation_questions` | string[] | 已按优先级排列；Agent 每次只问第一条 |
| `data` | object | 下列操作定义的结构化结果 |
| `error` | object/null | 失败时含 `code`、`message`、`retryable`、`details` |

Aily 中只让模型处理上述摘要、问题、数量、链接和不透明 ID。完整规范记录、原始 API 响应与详细日志不返回给模型，改用 `normalized_ref` 或 `operation_log_id` 引用。所有 ID 字段说明都写明“只可原样传递，不可由 AI 生成或改写”。

## 1. `inspect_ogsm_source`

用途描述：当用户提供 OGSM 文件、飞书电子表格链接、Base 链接或要求重新预检时调用。只读，不创建或修改 Base。

输入：

- `source`（首次调用必填，AI 推断）：包含 `query`、`files`、`urls`，示例“附件中的 2026 OGSM.xlsx，按部门处理”。
- `scope`（可选，AI 推断）：`department` 或 `personal`。
- `topology_hint`（可选，AI 推断）：`separate_bases`、`merged_base` 或空。
- `normalized_ref`、`source_fingerprint`（复检时原样传递）：用于复用第一次预检结果，不重复上传完整数据。
- `decision_answers`（复检时 AI 归纳）：只包含后端列出的待确认项及用户逐项回答，不接受新增业务假设。
- `people_resolution_ref`（复检时原样传递）：来自 `resolve_people`；没有负责人时可空。
- `actor_open_id`（上下文传入）：当前用户 OpenID，只用于权限与计划绑定。

`data` 至少输出：`source_fingerprint`、`normalized_ref`、`plan_id`、`departments`、`normalized_count`、`coverage`、`people_issues`、`date_issues`、`duplicates`、`broad_strategies`、`blocking_issues`、`review_items`、`plan_preview`。存在待确认项时返回 `status=needs_confirmation` 且 `plan_id` 为空；所有决策都有答案、后端校验通过并生成不可变计划后，才返回 `status=ready` 和 `plan_id`。

## 2. `resolve_people`

用途描述：预检发现负责人原文且需要匹配飞书成员时调用。只读，不修改人员字段。

输入：

- `names`（必填，来自预检）：去重后的负责人原文列表。
- `source_fingerprint`（必填，原样传递）：来自 `inspect_ogsm_source`。
- `candidate_open_ids`（可选，上下文传入）：用户 @ 的成员 OpenID，只作为候选线索。

`data` 至少输出 `people_resolution_ref`、`matches`、`unresolved`、`ambiguous`。每个姓名的 `match_status` 只能是 `zero`、`unique` 或 `ambiguous`；只有 `unique` 可返回 `person_open_id`。不得自动选择歧义人员。

## 3. `inspect_target_base`

用途描述：用户确认固定计划后、任何写入前调用；写操作超时后也可调用以恢复真实状态。只读。

输入：

- `plan_id`、`source_fingerprint`（必填，原样传递）：来自当前预检。
- `targets`（必填，来自固定计划）：批量 Base 目标；新建目标使用后端计划引用，不让模型编造 token。
- `upsert_key`（固定）：`源记录ID`。
- `actor_open_id`（上下文传入）：必须与计划执行人一致。

后端必须读完全部分页；不能解析响应结构时视为失败。`data` 至少输出 `snapshot_id`、`has_more`、`record_count`、`blank_keys`、`duplicate_keys`、`unexpected_records`、`object_config`、`permission_check`。只有分页完成且不存在阻断项时返回 `status=ready`。

## 4. `execute_approved_ogsm_plan`

用途描述：仅在用户明确同意当前固定计划、且目标检查通过后调用。这是唯一普通写操作。

输入：

- `plan_id`、`source_fingerprint`、`snapshot_id`（必填，原样传递）：来自本轮前序操作。
- `approval_summary`（必填）：必须与后端保存的当前计划摘要完全一致。
- `approved`（必填）：只在用户刚刚明确批准当前摘要时为 `true`，不得预设。
- `actor_open_id`（上下文传入）：必须与计划执行人一致。
- `enable_workflows`（默认固定为 `false`）：只有用户另行批准并已给出接收人时才允许改变。

后端必须拒绝：`approved` 不为 `true`；计划过期或跨用户；摘要、指纹、计划或快照变化；出现新空键、重复键或计划外记录；包含未经单独授权的删除；缺少接收人却要求启用工作流。

执行顺序为字段与选项、按 `源记录ID` upsert 记录、视图、仪表盘、默认关闭的工作流。`data` 至少输出每个目标的 `base_url`、`created`、`updated`、`objects_result`、`workflow_states`、`operation_log_id`。响应未知时返回 `status=unknown`，不得建议直接重试。

## 5. `verify_ogsm_base`

用途描述：写操作完成或结果未知后调用。完整回读并执行同一计划的第二次幂等 upsert；不接受新计划或删除请求。

输入：

- `plan_id`、`targets`、`operation_log_id`（必填，原样传递）。
- `actor_open_id`（上下文传入）：必须与当前计划一致。

`data` 至少输出每个目标的 `base_url`、`record_count`、`unique_key_count`、`second_upsert_created`、`second_upsert_updated`、`object_config`、`workflow_states`、`issues` 和总计 `acceptance_passed`。只有所有目标 `second_upsert_created=0` 且其余验收项通过时返回 `status=completed`。

## Aily 字段配置检查

- 允许 AI 从用户话语推断：`source`、`scope`、`topology_hint`、`names`、受限的 `decision_answers`、用户是否批准当前摘要。
- 只能从上下文或上一步原样传递：所有 `*_id`、`*_ref`、`*_fingerprint`、`targets`、`approval_summary`。
- 固定默认值：`upsert_key=源记录ID`、`enable_workflows=false`。
- 不应进入模型上下文：访问令牌、完整规范数据、原始通讯录、API 全量响应、内部堆栈和敏感日志。
- 错误 `retryable=true` 只表示技术上可重试；涉及写操作时仍须先回读，不等于允许 Agent 立即重试。
