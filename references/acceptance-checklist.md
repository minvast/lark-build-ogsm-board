# V1 acceptance checklist

## Source and records

- Confirm the input fingerprint and source provenance were retained.
- Confirm every imported action has a unique `源记录ID`.
- Confirm the total record count and `has_more=false` for full readbacks.
- Confirm no duplicate record was created on a second plan/upsert run.
- Confirm all O/G/S/M/action text matches the reviewed mapping.

## People and dates

- Confirm every required action has one real people owner.
- Confirm collaborators are separate from the owner.
- Confirm alias-to-display-name mappings are reported.
- Confirm required deadlines are populated and use the correct timezone/date.

## Calculations

- Sample every progress status and verify the automatic percentage.
- Verify completed items are green.
- Verify blocked, risk-present, and overdue incomplete items are red.
- Verify due-within-7-days below 80% and stale-over-7-days items are yellow.
- Verify blank or invalid inputs do not produce a false green result.

## Views and dashboard

- Confirm all six standard views exist and use the intended filters/groups.
- Confirm the dashboard reads `当前进度（自动）`, `健康灯（自动）`, `S｜策略`, and the people owner field.
- Confirm charts show real display names and reviewed strategy labels.
- Confirm chart detail paths expose the underlying action records.

## Workflows and safety

- Confirm workflows are disabled immediately after creation.
- Confirm deadline reminder receiver references the real people owner field.
- Confirm the red summary receiver is the escalation field and deduplication is configured.
- Do not send a test message unless requested.
- If reminders are enabled, report the exact workflow names and status.

## Handoff

Return the Base link, table and dashboard names, record/owner/strategy counts, unresolved review items, formula verification, workflow states, and whether advanced permissions were configured.
