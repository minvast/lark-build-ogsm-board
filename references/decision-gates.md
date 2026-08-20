# Mandatory decision gates

Stop and request confirmation before a Base write when any of these conditions appears.

## OGSM semantics

- The source contains multiple departments but the Base topology (one Base per department or one combined Base) is not confirmed.
- O is missing, copied from an uncertain parent, or expressed only as a slogan with no confirmed scope.
- An action lacks S or M alignment.
- One strategy contains at least 10 actions or at least 4 distinct measures; propose child strategies but do not apply them silently.
- A strategy will be split or renamed but `S｜策略原文（备查）` and the existing `源记录ID` have not been preserved.
- A cell appears to contain multiple actions.
- The same action appears under multiple O/G/S/M paths.

## Accountability

- No owner is provided.
- Multiple people appear in the primary owner cell. Ask for one accountable owner; move the rest to collaborators.
- Name search returns zero, multiple, external, inactive, or conflicting people.
- The source contains a nickname that maps to a different display name. Show the mapping explicitly.
- The owner cell contains a role, question mark, `inhouse N名`, or another placeholder instead of an identifiable person. Propose leaving the people field blank; never bind an arbitrary member.

## Dates, progress, and health

- Deadline is missing or not parseable.
- Source progress conflicts with status.
- A color, icon, or free-text source status needs mapping to a Base status. Show the mapping explicitly, for example green to completed, and wait for confirmation.
- Work is recurring, milestone-based, or frequency-based and the default status-to-progress model could be misleading.
- The user has not accepted the default 7-day due/stale thresholds or supplies a different health policy.

## Writes, reminders, and permissions

- The target Base already exists and the refresh authority is unclear.
- A full readback is paginated, cannot be parsed, contains blank `源记录ID`, or contains duplicate `源记录ID`.
- Any record deletion is proposed, including duplicate cleanup. Report the exact count, retention rule, record ID plan, and irreversibility before requesting authorization.
- Existing manual status, risk, next action, evidence, or owner values would be overwritten.
- Reminder recipients or escalation owners are unresolved.
- Enabling workflows would send live messages.
- Row-level visibility or advanced permissions are requested but role membership is incomplete.

Use a concise review table with: issue, affected rows/actions, proposed resolution, and effect if accepted.
