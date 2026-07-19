# Implementation prompt

Implement only the ready scope described in the issue dossier.

1. Add or update a regression test.
2. Run it and establish that it fails for the expected reason.
3. Do not modify production code until that failure is confirmed.
4. Make the smallest production change that passes the test.
5. Run focused tests, formatting, linting, and type checks.
6. Do not update dependencies or reformat unrelated code.
7. Do not add generated, temporary, or agent-conversation files.
8. Stop if expected behavior is ambiguous or upstream ownership has changed.

Return:

- files changed;
- commands run and results;
- remaining uncertainty;
- compatibility and operational risks;
- proposed pull-request summary.
