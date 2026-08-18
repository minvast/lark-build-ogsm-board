# Mandatory decision gates

Stop and request confirmation before a Base write when any of these conditions appears.

## OGSM semantics

- O is missing, copied from an uncertain parent, or expressed only as a slogan with no confirmed scope.
- An action lacks S or M alignment.
- One strategy contains at least 10 actions or at least 4 distinct measures; propose child strategies but do not apply them silently.
- A cell appears to contain multiple actions.
- The same action appears under multiple O/G/S/M paths.

## Accountability

- No owner is provided.
- Multiple people appear in the primary owner cell. Ask for one accountable owner; move the rest to collaborators.
- Name search returns zero, multiple, external, inactive, or conflicting people.
- The source contains a nickname that maps to a different display name. Show the mapping explicitly.

## Dates, progress, and health

- Deadline is missing or not parseable.
- Source progress conflicts with status.
- Work is recurring, milestone-based, or frequency-based and the default status-to-progress model could be misleading.
- The user has not accepted the default 7-day due/stale thresholds or supplies a different health policy.

## Writes, reminders, and permissions

- The target Base already exists and the refresh authority is unclear.
- Existing manual status, risk, next action, evidence, or owner values would be overwritten.
- Reminder recipients or escalation owners are unresolved.
- Enabling workflows would send live messages.
- Row-level visibility or advanced permissions are requested but role membership is incomplete.

Use a concise review table with: issue, affected rows/actions, proposed resolution, and effect if accepted.
