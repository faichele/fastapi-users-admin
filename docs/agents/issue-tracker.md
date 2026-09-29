# Issue tracker: GitHub

Issues and specifications for this repository live in GitHub Issues. Use the `gh` CLI from this clone; it infers the `faichele/fastapi-users-admin` repository from `origin`.

## Conventions

- Create: `gh issue create --title "..." --body "..."`
- Read: `gh issue view <number> --comments`
- List: `gh issue list --state open`
- Comment: `gh issue comment <number> --body "..."`
- Label: `gh issue edit <number> --add-label "..."`
- Close: `gh issue close <number> --comment "..."`

Use appropriate label and state filters when listing issues. For multiline bodies, use a heredoc rather than manually escaped newlines.

## Pull requests as a triage surface

**PRs as a request surface: no.** Triage skills should work from issues, not external pull requests.

## Skill routing

When a skill says to publish to the issue tracker, create a GitHub issue. When it says to fetch a relevant ticket, run `gh issue view <number> --comments`.
