# Minimal one-table Base schema

Use the exact business role of each field, but read current `lark-base` field JSON guidance before sending API payloads.

## Identity and OGSM

| Field | Type | Notes |
|---|---|---|
| 行动 | text, primary | One executable action per record |
| 源记录ID | text | Stable upsert key; never expose as the main title |
| O｜目的 | text | Preserve the full purpose statement |
| G｜目标 | text | Preserve the full goal statement |
| S｜策略 | single select | Use reviewed strategy or `父策略-子策略` labels |
| S｜策略原文（备查） | text | Preserve the source strategy before any reviewed split or rename |
| M｜衡量 | text | Preserve the measure/result statement |

## Accountability and execution

| Field | Type | Notes |
|---|---|---|
| 负责人 | people, single | The one accountable owner |
| 协作人 | people, multiple | Contributors; never use as a substitute for the owner |
| 负责人原文（备查） | text | Original source text and aliases |
| 开始日期 | date | Optional in V1 |
| 截止日期 | date | Required for deadline health rules |
| 进度状态 | single select | 待更新、未开始、已启动、进行中、接近完成、待验收、受阻、已完成 |
| 当前进度（自动） | formula | Default mapping: 0, 0, 20, 50, 80, 90, 20, 100 |
| 健康灯（自动） | formula | Completed green; blank deadline/status, blocked/risk/overdue red; due within 7 days below 80 or stale over 7 days yellow |
| 风险/卡点 | text | A nonblank value is red in the default profile |
| 下一步动作 | text | Required by operating policy for yellow/red items, not by storage schema |
| 交付物/证据 | text | Link or human-readable evidence reference |
| 升级提醒对象 | people, multiple | Department lead or escalation recipients |

## Audit fields

Include source document URL, source file/title, worksheet, source row/range, import fingerprint, updated time, and updated user. Preserve these fields across refreshes.

Use this default health expression after verifying current Base formula syntax:

```text
IFS([当前进度（自动）]=100,"🟢 绿灯",ISBLANK([截止日期]),"🔴 红灯",ISBLANK([进度状态]),"🔴 红灯",[进度状态]="受阻","🔴 红灯",NOT(ISBLANK([风险/卡点])),"🔴 红灯",[截止日期]<TODAY(),"🔴 红灯",AND(DAYS([截止日期],TODAY())<=7,[当前进度（自动）]<80),"🟡 黄灯",DAYS(TODAY(),[最后修改时间])>7,"🟡 黄灯",TRUE(),"🟢 绿灯")
```

## Views and dashboard

Create six standard views from `SKILL.md`. Use the strategy and status fields as kanban groups. Create four compact dashboard blocks: overall average progress, health distribution, strategy average progress, and owner average progress.

The dashboard must not fabricate KPI actuals. It visualizes execution only. A future standard operating model may add target trees, KPI definitions, monthly facts, data sources, risks, and permissions as separate tables.

## Reminder defaults

- Deadline change reminder: receiver is the real `负责人` people field.
- Red-light daily summary: receiver is `升级提醒对象`; deduplicate records.
- Name not-yet-enabled workflows with a visible `｜关闭` suffix and keep them disabled on creation.
- Enable only after owner/date readback and explicit user approval.
