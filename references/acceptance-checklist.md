# V1 acceptance checklist

## Source and records

- Confirm the input fingerprint and source provenance were retained.
- Confirm every imported action has a unique `源记录ID`.
- Confirm the total record count and `has_more=false` for full readbacks.
- Confirm the record-list response was parsed from its actual object or matrix shape; a nonempty matrix was not treated as an empty table.
- Confirm a second plan/upsert run reports `created=0`, updates the expected records, and leaves the online count unchanged.
- Confirm all O/G/S/M/action text matches the reviewed mapping.
- Confirm reviewed child strategies retain the source strategy text and original `源记录ID`.

## People and dates

- Confirm every required action has one real people owner.
- Confirm approved unresolved placeholders remain blank in the people field and are retained in `负责人原文（备查）`.
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

- Read back all six standard views and confirm type, filters, and groups; names alone are insufficient.
- Confirm each dashboard block returns data and reads `当前进度（自动）`, `健康灯（自动）`, `S｜策略`, and the people owner field.
- Confirm charts show real display names and reviewed strategy labels.
- Confirm chart detail paths expose the underlying action records.

## Workflows and safety

- Confirm workflows are disabled immediately after creation.
- Read back each workflow and require `status=disabled`; a successful create/disable response alone is insufficient.
- Confirm deadline reminder receiver references the real people owner field.
- Confirm the red summary receiver is the escalation field and deduplication is configured.
- Do not send a test message unless requested.
- If reminders are enabled, report the exact workflow names and status.

## Duplicate cleanup, when needed

- Confirm the approved cleanup plan contains exact keep/delete record IDs and was regenerated only before, not after, user authorization.
- Immediately before deletion, confirm the live record ID set exactly matches the approved plan.
- After deletion, confirm every keep ID remains, every delete ID is absent, total count equals the expected unique count, and the deletion is reported as unrecoverable.

## Multiple Bases, when needed

- Run the complete checklist independently for each Base.
- Confirm each department has its own Base link, table, views, dashboard, workflows, source fingerprint, and verification artifact.

## Handoff

Return the Base link, table and dashboard names, record/owner/strategy counts, unresolved review items, formula verification, workflow states, and whether advanced permissions were configured.
