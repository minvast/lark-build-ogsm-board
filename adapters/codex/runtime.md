# Codex 适配

Codex 中直接加载根 `SKILL.md`，并按以下方式映射统一能力：

| 统一能力 | Codex 实现 |
| --- | --- |
| `inspect_ogsm_source` | 本地脚本；飞书电子表格使用 `lark-sheets` |
| `resolve_people` | `lark-contact` |
| `inspect_target_base` | `lark-base` 的只读命令与完整分页 |
| `execute_approved_ogsm_plan` | `lark-base` 快捷命令，用户身份，串行执行 |
| `verify_ogsm_base` | `lark-base` 回读 + `scripts/audit_base_records.py` |

写入前阅读当前命令帮助和所需 Base 参考说明。高风险或全量替换先 dry-run。CLI 记录列表可能返回对象或矩阵结构，按 `references/provisioning-safety.md` 解析。

Codex 的 `agents/openai.yaml` 仅是 OpenAI/Codex 展示适配，不是跨平台依赖。
