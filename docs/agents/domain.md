# Domain Docs

## Before exploring

Read `CONTEXT.md` at the repository root when it exists. If `CONTEXT-MAP.md` exists instead, follow it to the relevant context documents. Read relevant decisions under `docs/adr/` before changing an affected area.

If these files or directories do not yet exist, proceed without mentioning their absence. The domain-modeling workflow creates them when a glossary or recorded decision is needed.

## Layout

This is a single-context repository:

```text
/
├── CONTEXT.md
├── docs/adr/
└── src/
```

## Consumer rules

Use glossary terms from `CONTEXT.md` consistently in issues, designs, tests, and code. If a planned change conflicts with an ADR, name the conflict explicitly instead of silently overriding the decision.
