---
name: lark-build-ogsm-board
description: 将本地 Excel/CSV OGSM 一页纸、飞书电子表格或现有极简 OGSM 表，转换为经过预检、确认和幂等验收的飞书多维表格执行看板。当 Codex 需要检查并标准化 O/G/S/M/行动数据、拆分过宽策略、解析真实负责人、为一个或多个部门分别创建或更新 Base，并配置自动进度、健康灯、视图、仪表盘及默认关闭的提醒工作流时使用；也用于审计或安全清理由误导入产生的重复 OGSM 记录。
---

# 构建极简 OGSM 多维表看板

只构建 V1 极简单表系统。不得擅自扩展为公司级 KPI 事实模型、多表目标树或绩效系统。

## 必须执行的流程

1. 识别数据来源和范围：部门或个人；新建或更新 Base。来源包含多个部门时，先确认“每部门独立 Base”或“合并 Base”，不得自行决定拓扑。
2. 阅读 [references/input-contract.md](references/input-contract.md)。处理本地 `.xlsx`、`.csv` 或 `.tsv` 时，运行 `scripts/precheck_ogsm.py`。处理飞书电子表格时，使用 `lark-sheets` 读取源数据，保留文档、工作表、区域、行号和版本来源，并标准化为相同规范字段。
3. 在任何 Base 写入前展示预检结果。列明 O/G/S/M 覆盖率、行动数量、负责人、日期、重复项、过宽策略和所有未解决映射。
4. 出现 [references/decision-gates.md](references/decision-gates.md) 中任一决策门时，停止并请求确认。不得根据弱证据推断最终策略归属、真实人员身份、状态映射、业务阈值或权限。
5. 过宽策略只有在用户确认后才能按衡量项拆成子策略；将拆分标签写入 `S｜策略`，始终把源策略原文保存在 `S｜策略原文（备查）`，且不得改变已生成的 `源记录ID`。
6. 获得确认后，运行 `scripts/build_base_plan.py` 生成确定性计划。开始创建前阅读 [references/minimal-schema.md](references/minimal-schema.md) 和 [references/provisioning-safety.md](references/provisioning-safety.md)。
7. 使用 `lark-contact` 解析每个唯一负责人。将真实负责人写入单值人员字段，将协作人单独写入多值人员字段。角色、问号、`inhouse N名` 等占位文本在确认后保持人员字段为空；原文仅存入备查字段。
8. 使用 `lark-base` 快捷命令完成所有 Base 创建和更新。写入前阅读当前命令帮助和所需 Base 参考说明；使用 `--as user`，对高风险或全量替换写入先 dry-run，串行写入，并对暂时性限流做有界退避重试。
9. 在任何记录写入前完整回读目标表。兼容 `record-list` 的矩阵和对象两种 JSON 结构；验证 `has_more=false`、记录总数、空键和重复 `源记录ID`。不得把“解析不到记录”当成空表。
10. 先创建字段和单选项，再按 `源记录ID` 执行 upsert，每批最多 200 条；随后创建视图、公式、仪表盘组件和工作流。所有对象创建后都回读配置，而不只检查名称。
11. 完成后再次运行同一 upsert：必须得到“新增 0、更新数等于规范记录数”。若出现重复，先用 `scripts/audit_base_records.py` 生成只读审计和精确清理计划，获得用户删除授权后才删除指定 record ID，并再次回读。
12. 在负责人和日期校验通过、且用户明确批准启用提醒前，保持所有工作流关闭。除非用户要求，不得发送测试消息。
13. 执行 [references/acceptance-checklist.md](references/acceptance-checklist.md) 中的验收检查，并返回每个 Base 的链接、记录数量、未解决事项、提醒状态、删除结果和验证摘要。

## 本地预检命令

处理 `.xlsx` 时，使用带有 `openpyxl` 的捆绑 Python 运行时。

```bash
python3 scripts/precheck_ogsm.py <source.xlsx> --output-dir <output-dir> --scope department
python3 scripts/build_base_plan.py <output-dir>/normalized.json --output <output-dir>/base-plan.json --base-name "<部门或个人> OGSM看板"
```

若 `normalized.json` 包含阻断问题，不得继续搭建。需要复核的问题必须由用户确认，不得自动忽略。

## V1 输出约定

创建一张行动表，包含：

- O、G、S、源策略原文、M 和行动文本；
- 一名主要人员负责人，以及可选协作人；
- 截止日期、进度状态、自动进度和自动健康灯；
- 风险或卡点、下一步动作和交付物或证据；
- 负责人原文和稳定的源记录 ID；
- 来源文档、工作表、行号或区域以及导入指纹。

创建以下可复用视图：

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
- 完整读回必须验证实际结构；飞书 CLI 的矩阵响应使用 `data.data`、`data.fields` 和 `data.record_id_list` 还原记录。
- 目标表已有空键、重复键、分页未读完或计划外记录时，停止创建并先审计；不得以“补写一次”方式修复。
- 删除重复记录属于不可恢复操作。先固定保留/删除 record ID 清单，再请求明确授权；执行前重新校验清单仍与在线状态一致。
- 除非用户明确选择“以源数据为准刷新”，不得覆盖人工维护的状态、风险、下一步动作、证据或人员分配。
- 将视图视为展示，不得当作安全权限。只有角色负责人和可见范围明确时才配置高级权限。
- 不得从旧模板复制特定部门的策略名称、人员、阈值或提醒接收人。
- API 返回无操作、超时或部分响应时，回读资源并验证目标状态后再继续。

## 随附资源

- `scripts/precheck_ogsm.py`：解析矩形表和带合并单元格的 Excel/CSV 表，向下填充 OGSM 层级字段，标准化记录，并生成 JSON、CSV 和 Markdown 预检产物。
- `scripts/build_base_plan.py`：生成确定性的 V1 搭建计划和记录载荷来源。
- `scripts/audit_base_records.py`：兼容飞书记录列表的矩阵/对象响应，只读核对键、计数和期望记录，并在安全条件满足时生成精确重复清理计划；该脚本不会删除记录。
- `references/provisioning-safety.md`：记录写入、限流重试、幂等验证和重复清理的强制守则。
- `assets/ogsm-import-template.xlsx`：推荐使用的可编辑输入模板。
- `assets/config-example.json`：默认规则示例；将业务阈值和提醒接收人视为可配置项。
