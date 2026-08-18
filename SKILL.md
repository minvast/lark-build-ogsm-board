---
name: lark-build-ogsm-board
description: 将本地 Excel/CSV OGSM 一页纸、飞书电子表格或现有极简 OGSM 表，转换为经过预检和确认的飞书多维表格执行看板。当 Codex 需要检查并标准化 O/G/S/M/行动数据、报告对齐关系及负责人和日期问题、确认有歧义的映射，再创建或更新部门或个人的单表 OGSM 系统时使用；支持真实人员负责人、自动进度、自动健康灯、视图、仪表盘和默认关闭的提醒工作流。
---

# 构建极简 OGSM 多维表看板

只构建 V1 极简单表系统。不得擅自扩展为公司级 KPI 事实模型、多表目标树或绩效系统。

## 必须执行的流程

1. 识别数据来源和适用范围：部门或个人；新建多维表格或更新现有多维表格。
2. 阅读 [references/input-contract.md](references/input-contract.md)。处理本地 `.xlsx`、`.csv` 或 `.tsv` 时，运行 `scripts/precheck_ogsm.py`。处理飞书电子表格时，使用 `lark-sheets` 读取源数据，保留文档、工作表、区域和行号来源，并标准化为相同的规范字段。
3. 在任何多维表格写入前展示预检结果。列明 O/G/S/M 覆盖率、行动数量、负责人、日期、重复项、过宽策略和所有未解决的映射。
4. 出现 [references/decision-gates.md](references/decision-gates.md) 中任一决策门时，停止并请求确认。不得根据弱证据推断最终策略归属、真实人员身份、业务阈值或权限。
5. 获得确认后，运行 `scripts/build_base_plan.py` 生成确定性的搭建计划。开始创建前阅读 [references/minimal-schema.md](references/minimal-schema.md)。
6. 使用 `lark-contact` 解析每个唯一负责人。将真实负责人写入单值人员字段，将协作人单独写入多值人员字段；负责人原文只保留在备查字段。
7. 使用 `lark-base` 快捷命令完成所有多维表格创建和更新。写入前阅读当前命令帮助和所需的 Base 参考说明；使用 `--as user`，对高风险或全量替换写入先执行 dry-run，按顺序串行执行，并回读关键对象。
8. 先创建字段和单选项，再分批创建记录，每批最多 200 条；随后创建视图、公式、仪表盘组件和工作流。
9. 在负责人和日期校验通过、且用户明确批准启用提醒前，保持所有工作流关闭。除非用户要求，不得发送测试消息。
10. 执行 [references/acceptance-checklist.md](references/acceptance-checklist.md) 中的验收检查，并返回多维表格链接、记录数量、未解决事项、提醒状态和验证摘要。

## 本地预检命令

处理 `.xlsx` 时，使用带有 `openpyxl` 的捆绑 Python 运行时。

```bash
python3 scripts/precheck_ogsm.py <source.xlsx> --output-dir <output-dir> --scope department
python3 scripts/build_base_plan.py <output-dir>/normalized.json --output <output-dir>/base-plan.json --base-name "<部门或个人> OGSM看板"
```

若生成的 `normalized.json` 包含阻断问题，不得继续搭建。需要复核的问题必须由用户确认，不得自动忽略。

## V1 输出约定

创建一张行动表，包含：

- O、G、S、M 和行动文本；
- 一名主要人员负责人，以及可选的协作人；
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

- 保留原始数据源，不得改写用户的输入工作簿。
- 使用 `源记录ID` 作为稳定的更新键。重复运行时更新匹配的源记录，不得生成重复记录。
- 除非用户明确选择“以源数据为准刷新”，不得覆盖人工维护的进度状态、风险、下一步动作、证据或人员分配。
- 将视图视为展示方式，不得将其当作安全权限。只有在角色负责人和可见范围规则明确时，才配置高级权限。
- 不得从旧模板复制特定部门的策略名称、人员、阈值或提醒接收人。
- API 返回无操作或部分响应时，回读资源并验证目标状态后再继续。

## 随附资源

- `scripts/precheck_ogsm.py`：解析矩形表和带合并单元格的 Excel/CSV 表，向下填充 OGSM 层级字段，标准化记录，并生成 JSON、CSV 和 Markdown 预检产物。
- `scripts/build_base_plan.py`：生成确定性的 V1 搭建计划和记录载荷来源。
- `assets/ogsm-import-template.xlsx`：推荐使用的可编辑输入模板。
- `assets/config-example.json`：默认规则示例；将业务阈值和提醒接收人视为可配置项。
