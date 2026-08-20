---
name: lark-build-ogsm-board
description: 将本地 Excel/CSV OGSM 一页纸、飞书电子表格或现有极简 OGSM 表，转换为经过预检、人工确认和幂等验收的飞书多维表格执行看板。适用于 WorkBuddy、Codex、飞书 Aily，以及其他支持 Agent Skills、系统提示词、函数调用、插件或工作流的智能体；用于标准化 O/G/S/M/行动数据、拆分过宽策略、解析真实负责人、为一个或多个部门分别创建或更新 Base，并安全审计或清理由误导入产生的重复记录。
---

# 构建极简 OGSM 多维表看板

只构建 V1 极简单表系统。不得擅自扩展为公司级 KPI 事实模型、多表目标树或绩效系统。

## 先选择运行时适配层

本文件定义平台无关的业务和安全规则。开始前读取 [references/platform-adapters.md](references/platform-adapters.md)，选择当前运行时对应的适配层：

- 支持 Agent Skills 文件：直接加载本目录，并映射所需能力。
- WorkBuddy：优先让 Agent 从公开 GitHub 仓库下载安装；若当前环境不能自动安装，上传同一个通用 Skill ZIP，并读取 [adapters/workbuddy/runtime.md](adapters/workbuddy/runtime.md)。
- 飞书 Aily / 飞书智能伙伴：依次读取 [部署说明](adapters/feishu-aily/deployment.md)、[可粘贴提示词](adapters/feishu-aily/agent-skill-prompt.md) 和 [5 个操作契约](adapters/feishu-aily/operation-contracts.md)。Agent Skill 只负责对话、决策门和操作调度；复杂且必须稳定执行的搭建过程交给工作流或自定义连接器后端。
- Codex：读取 [adapters/codex/runtime.md](adapters/codex/runtime.md)。
- Dify、扣子、FastGPT、MaxKB：读取各自适配说明；不宣称可原生导入本目录。
- 其他支持函数调用的 Agent：使用 [adapters/generic/system-prompt.md](adapters/generic/system-prompt.md) 与 [adapters/generic/tool-contract.json](adapters/generic/tool-contract.json)。

运行时至少应提供以下能力：读取数据源、解析人员、完整读取 Base、按计划写入 Base、回读验收，以及在写入前与用户确认。能力名称可以不同，由适配层映射。若缺少写入或回读能力，只能生成预检报告和搭建计划，不得声称已完成 Base 搭建。

## 安装与分发

首推把公开仓库地址 `https://github.com/minvast/lark-build-ogsm-board` 直接交给 Agent，并要求它从仓库根目录安装 `lark-build-ogsm-board`、检查根目录 `SKILL.md`，再验证技能已可用。只有在 Agent 没有联网下载、本地文件写入或 Skill 安装能力时，才让用户下载并上传通用包 `lark-build-ogsm-board.zip`。

通用 ZIP 适用于 Codex、WorkBuddy 及其他兼容 Agent Skills 文件结构的平台，不得为 WorkBuddy 维护内容相同的专用包。不要宣称所有平台的图形界面都能直接粘贴 GitHub URL；“从 GitHub 安装”可以由 Agent 自行下载并放入其 Skill 目录完成。飞书 Aily 当前采用“粘贴提示词并绑定操作”的适配方式，不把仓库或 ZIP 宣称为可直接导入的 Aily 应用包。安装只加载流程和资源，不得在安装阶段运行 OGSM 脚本、连接飞书或读取业务数据。

## 面向 AI 小白沟通

- 默认使用小白模式：先说结论，再说当前只需做的一步；每次最多问一个必须由用户决定的问题。
- 不主动展示 SHA-256、来源指纹、plan ID、snapshot ID、record ID、API 参数或命令行。它们仅用于内部校验，用户要求技术细节时再展示。
- 把“执行 upsert”说成“更新已有记录，不重复新增”，把“完整回读验收”说成“搭完后再检查一遍”。
- 安装时先给 GitHub 地址这一条最短路径；能自动安装就验证后报告。不能自动安装时，再给同一个通用 ZIP 和平台上传入口，不得假装成功。
- 完成时优先报告：已建几个 Base、各有多少条行动、哪些信息仍需补充、提醒是否开启。技术日志放到可选附录。

## 必须执行的流程

1. 识别数据来源和范围：部门或个人；新建或更新 Base。来源包含多个部门时，先确认“每部门独立 Base”或“合并 Base”，不得自行决定拓扑。
2. 阅读 [references/input-contract.md](references/input-contract.md)。处理本地 `.xlsx`、`.csv` 或 `.tsv` 时，运行 `scripts/precheck_ogsm.py`。处理在线表格时，由适配层的“读取数据源”能力读取，保留文档、工作表、区域、行号和版本来源，并标准化为相同规范字段。
3. 在任何 Base 写入前展示预检结果。列明 O/G/S/M 覆盖率、行动数量、负责人、日期、重复项、过宽策略和所有未解决映射。
4. 出现 [references/decision-gates.md](references/decision-gates.md) 中任一决策门时，停止并请求确认。不得根据弱证据推断最终策略归属、真实人员身份、状态映射、业务阈值或权限。
5. 过宽策略只有在用户确认后才能按衡量项拆成子策略；将拆分标签写入 `S｜策略`，始终把源策略原文保存在 `S｜策略原文（备查）`，且不得改变已生成的 `源记录ID`。
6. 获得确认后，运行 `scripts/build_base_plan.py` 生成确定性计划。开始创建前阅读 [references/minimal-schema.md](references/minimal-schema.md) 和 [references/provisioning-safety.md](references/provisioning-safety.md)。
7. 通过“解析人员”能力逐一解析唯一负责人。真实负责人写入单值人员字段，协作人写入多值人员字段。角色、问号、`inhouse N名` 等占位文本在确认后保持人员字段为空；原文仅存入备查字段。
8. 通过适配层的 Base 能力执行创建和更新。使用用户身份或与用户授权范围等价的身份；高风险或全量替换写入先 dry-run，串行写入，并对暂时性限流做有界退避重试。
9. 在任何记录写入前完整回读目标表。兼容记录列表的矩阵和对象两种结构；验证 `has_more=false`、记录总数、空键和重复 `源记录ID`。不得把“解析不到记录”当成空表。
10. 先创建字段和单选项，再按 `源记录ID` 执行 upsert，每批最多 200 条；随后创建视图、公式、仪表盘组件和工作流。所有对象创建后都回读配置，而不只检查名称。
11. 完成后再次运行同一 upsert：必须得到“新增 0、更新数等于规范记录数”。若出现重复，先用 `scripts/audit_base_records.py` 生成只读审计和精确清理计划，获得用户对固定 record ID 清单的删除授权后才删除，并再次回读。
12. 在负责人和日期校验通过、且用户明确批准启用提醒前，保持所有工作流关闭。除非用户要求，不得发送测试消息。
13. 执行 [references/acceptance-checklist.md](references/acceptance-checklist.md) 中的验收检查，并返回每个 Base 的链接、记录数量、未解决事项、提醒状态、删除结果和验证摘要。

## 本地预检命令

处理 `.xlsx` 时，使用带有 `openpyxl` 的 Python 运行时。

```bash
python3 scripts/precheck_ogsm.py <source.xlsx> --output-dir <output-dir> --scope department
python3 scripts/build_base_plan.py <output-dir>/normalized.json --output <output-dir>/base-plan.json --base-name "<部门或个人> OGSM看板"
```

若运行时无法执行本地脚本，应在后端操作或工作流中等价实现字段标准化、来源指纹和稳定 `源记录ID` 算法。若 `normalized.json` 包含阻断问题，不得继续搭建。

## V1 输出约定

创建一张行动表，包含 O、G、S、源策略原文、M、行动文本、一名主要负责人、可选协作人、截止日期、进度状态、自动进度、自动健康灯、风险或卡点、下一步动作、交付物或证据、负责人原文、稳定的源记录 ID 和来源审计信息。

创建六个可复用视图：

1. `00｜O-G-S-M行动总览`
2. `01｜红灯事项`
3. `02｜风险关注`
4. `03｜待更新`
5. `04｜进度状态看板`
6. `05｜策略进度看板`

创建一个小型仪表盘，展示总体进度、健康灯分布、策略进度和负责人进度。严格区分结果与行动；V1 不得虚构业务 KPI 实际值。

## 安全与幂等性

- 保留原始数据源，不得改写用户输入。
- 使用 `源记录ID` 作为稳定更新键。重复运行时更新匹配记录，不得生成重复记录。
- 完整读回必须验证实际结构；矩阵响应需使用列名、行数据和 record ID 列表还原记录。
- 目标表已有空键、重复键、分页未读完或计划外记录时，停止创建并先审计；不得以“补写一次”方式修复。
- 删除重复记录属于不可恢复操作。先固定保留/删除 record ID 清单，再请求明确授权；执行前重新校验清单仍与在线状态一致。
- 除非用户明确选择“以源数据为准刷新”，不得覆盖人工维护的状态、风险、下一步动作、证据或人员分配。
- 将视图视为展示，不得当作安全权限。只有角色负责人和可见范围明确时才配置高级权限。
- 不得从旧模板复制特定部门的策略名称、人员、阈值或提醒接收人。
- API 返回无操作、超时或部分响应时，回读资源并验证目标状态后再继续。
- 执行写入的后端操作必须再次校验确认状态；不得只依赖提示词约束。

## 随附资源

- `scripts/precheck_ogsm.py`：标准化 Excel/CSV 并生成 JSON、CSV 和 Markdown 预检产物。
- `scripts/build_base_plan.py`：生成确定性的 V1 搭建计划和记录载荷来源。
- `scripts/audit_base_records.py`：只读审计重复键，并在安全条件满足时生成精确清理计划；不会删除记录。
- `references/provisioning-safety.md`：记录写入、限流重试、幂等验证和重复清理的强制守则。
- `adapters/`：各智能体运行时的提示词、能力映射和部署方法。
- `assets/ogsm-import-template.xlsx`：推荐使用的可编辑输入模板。
- `assets/config-example.json`：默认规则示例；业务阈值和提醒接收人始终为可配置项。
