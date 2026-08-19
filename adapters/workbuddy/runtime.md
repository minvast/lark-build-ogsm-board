# WorkBuddy 适配

## 安装

首推把公开仓库地址 `https://github.com/minvast/lark-build-ogsm-board` 发给 WorkBuddy，并要求它下载仓库、从根目录安装 `lark-build-ogsm-board`，再确认技能出现在已安装列表。只有在当前会话没有联网下载、本地文件写入或 Skill 安装能力时，才改走界面上传。

界面上传使用通用包 `lark-build-ogsm-board.zip`：进入“技能”，选择“添加技能”与“上传技能”，上传包含根目录 `SKILL.md` 的 ZIP。WorkBuddy 不需要专用包，该通用 ZIP 与 Codex 和其他兼容 Agent 共用同一份内容。

无论来源是 GitHub 还是 ZIP，都先检查根目录、`SKILL.md` frontmatter 和脚本范围，再安装并验证。若没有安装能力，只告诉用户完成上述点击步骤；不得声称已经安装。安装阶段不得运行 OGSM 脚本、连接飞书或读取业务数据。

## 第一次使用

首次执行选择 Plan 模式，启用本 Skill，并让用户上传 OGSM 文件或提供飞书表格链接。先预检并用小白语言展示结果，用户确认后再进入可写模式。

## 能力映射

| 统一能力 | WorkBuddy 实现 |
| --- | --- |
| `inspect_ogsm_source` | 本地文件工具 + `scripts/precheck_ogsm.py` |
| `resolve_people` | 已授权的飞书连接器、MCP 或受控 API |
| `inspect_target_base` | 同一飞书连接能力的完整分页读取 |
| `execute_approved_ogsm_plan` | 用户确认后的连接器、MCP 或本地 CLI |
| `verify_ogsm_base` | 完整回读 + 第二次相同更新验证 |

安装 Skill 只代表 WorkBuddy 学会流程，不代表自动获得飞书权限。没有可读写飞书 Base 的连接器、MCP 或 CLI 时，只输出预检和搭建计划，并告诉用户“尚未写入飞书”。

默认不要求用户理解 SHA、ID 或 API。只在审计失败、重复清理或用户主动询问时展示技术详情。
