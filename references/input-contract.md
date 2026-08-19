# V1 input contract

## Supported inputs

- Local `.xlsx` or `.xlsm` workbooks with at least one recognizable header row.
- Local `.csv` or `.tsv` files.
- Feishu spreadsheets read through `lark-sheets`, then normalized to the canonical fields below.
- Existing minimal Base tables when the user asks to upgrade rather than create.

V1 supports rectangular tables and merged hierarchy cells. It does not promise automatic parsing of arbitrary visual one-page layouts that have no recognizable action column. For those sources, extract a review table first.

## Canonical fields

| Canonical field | Preferred Chinese header | Requirement |
|---|---|---|
| department | 部门 | Department mode review-required if blank |
| person | 个人 | Optional for department input |
| period | 周期 | Recommended |
| objective | O｜目的 | Review-required if blank |
| goal | G｜目标 | Recommended |
| strategy | S｜策略 | Review-required if blank |
| strategy_source_text | S｜策略原文（备查） | Initialize from source S; preserve when a reviewed child strategy is assigned |
| measure | M｜衡量 | Review-required if blank |
| action | 行动 | Required; one row means one action |
| owner | 负责人 | Review-required; text is not yet a people identity |
| collaborators | 协作人 | Optional |
| start_date | 开始日期 | Optional in V1 |
| due_date | 截止日期 | Review-required |
| status | 进度状态 | Optional; default `待更新` |
| progress | 当前进度 | Optional source value; V1 Base derives progress from status |
| risk | 风险/卡点 | Optional |
| next_action | 下一步动作 | Optional |
| evidence | 交付物/证据 | Optional |

## Normalization rules

- Expand merged-cell values and forward-fill only hierarchy fields: department, person, period, O, G, S, M.
- Never forward-fill action, owner, date, status, risk, next action, or evidence.
- Keep source file, sheet, row/range, and file fingerprint.
- Generate `源记录ID` from department, period, O, G, S, M, and action text.
- Generate `源记录ID` before applying reviewed strategy splits, then keep it unchanged. Prefer a source-provided stable ID when available.
- Do not split a multiline action cell automatically. Flag it for review.
- Do not turn owner text into a people value until `lark-contact` resolves it.
- Treat role names, question marks, headcount placeholders, and `inhouse N名` as unresolved owner text; keep the people field blank after confirmation.
- Do not invent missing dates, owners, goals, strategies, measures, or progress.

## Online source routing

- Feishu Sheet URL: use `lark-sheets` to resolve the spreadsheet and read the specific worksheet/range. Preserve the online URL, spreadsheet title/token, worksheet ID/name, range, source row, revision when available, and a deterministic fingerprint.
- Source color or styling is not a status until the user confirms the mapping. Preserve the original signal in the review artifacts.
- Base URL: use `lark-base +url-resolve`; inspect fields and records before proposing an upgrade.
- Local Excel that should be imported as-is: use `lark-drive +import --type bitable` only when the user wants direct import. For this skill, prefer normalization and a purpose-built Base because formulas, people fields, views, and workflows require post-import configuration.
