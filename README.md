# GitHub Copilot App: shopping-cart workshop

Learn to direct Copilot App through a realistic Java development loop:
**reproduce → plan → implement → inspect → verify**.

Follow the [workshop handbook](https://www.julien-dubois.com/workshops/copilot-app/).
Start with a cart bug, item removal and a Hibernate N+1 investigation through
MCP, then improve the UI with Browser/Canvas, integrate two isolated worktree
improvements with Agent Merge and independently critique the result. A fourth
ticket uses exactly five specialists to build checkout; their orchestrator
delivers it to **your repository's `main`** after your approval. Use Chronicle to
review workshop usage and prepare the final handoff. The native App steps still
need classroom validation.

## Create your own repository

Choose **Use this template → Create a new repository** on
[this repository](https://github.com/jdubois/copilot-shopping-cart-workshop).
Leave **Include all branches** off: `main` contains the intentionally broken
starter. Your new repository has independent history and does not inherit the
solution tags.

In Copilot App, click **+** next to **Sessions** in the sidebar, then
**Add GitHub repository**. Choose your new repository, not the template; the App
clones it for you. Start a session in that repository with **Environment → This
computer** and **Workspace → New worktree**.

Let Copilot handle Git bookkeeping for branches, commits and integration.
Review the **Changes** diff before authorizing commits or integration.
You do not need to type Git commands for the workshop.
Use JDK 21+, Git and a supported App account. No Docker, Node, external database
or payment provider is needed. The three Java skills are already installed in
`.github/skills/`.

Run the initial tests in your workshop session's terminal:

```sh
./mvnw -q -Dtest=BaselineTest test
```

Four baseline tests pass, but adding the same product twice is not covered.
In that session's worktree terminal, start one shop. Stop any previous workshop
server before starting another:

```sh
./mvnw spring-boot:run
```

Once ready, the startup banner prints the home URL and the BootUI UI installation
URL using the bound port and configured paths, or marks BootUI as disabled.

Open http://127.0.0.1:18765. Add the €10 Notebook twice: the starter incorrectly
shows quantity 1 / €10 instead of 2 / €20.
Opening a Browser canvas does not restart the server or change its revision.
After approved UI edits, Copilot confirms the shop runs from its worktree, runs
`./mvnw compile` there to copy static resources, then reloads the existing Browser
canvas and verifies the visible change. Static edits do not need a JVM restart;
compiled Java changes can trigger DevTools auto-restart. Saving source alone
does not update the running app. Copilot reports any ownership, compilation or
browser-control blocker rather than claiming the preview was refreshed.
You own the single persistent server and manual restarts for switching runtime
worktrees or recovery: for final verification, run the accepted, merged `main`
revision, not an earlier worktree build.
Restarting or using Reset cart clears synthetic data. Windows: `.\mvnw.cmd`.
The code is intentionally defective and local-only; do not deploy it or use real
customer data.

## First three separate tickets

1. Generate `CartContractTest.java` from agreed quantity acceptance criteria.
   Repeated additions must accumulate quantity and total without duplicating
   lines; quantities, including accumulated quantities, must stay within 1–99.
   Rejected additions must preserve the cart. Fix persisted state, not just
   displayed text.
2. Use `/spring-boot-testing` to generate `RemoveContractTest.java` from agreed
   removal acceptance criteria before implementing DELETE
   `/api/cart/items/{productId}` and a Remove button. Removing an item
   returns 200 with the updated cart and remaining item count. If the item is
   not in the cart, return 404 without changing the cart, whether or not the
   product exists in the catalogue.
3. Inspect GET `/api/cart` through BootUI MCP for 8 distinct products. Generate
   `QueryContractTest.java` before optimizing: completed HTTP GET `/api/cart`
   responses with 8 and 16 distinct products must each use exactly 1 SELECT
   after the fix, instead of the starter's 9 and 17. Exclude all seeding/setup
   SELECTs from measurement. Assert that product names, server-owned prices,
   quantities, line totals, item count and cart total are preserved. Do not use
   global eager loading or add dependencies.

Ask Copilot to generate each acceptance file in
`src/test/java/com/juliendubois/workshop/`, reusing `HttpFixture` and the existing
Spring Boot/H2/JUnit stack. Review its assertions against the acceptance card and
observe the intended failures before fixing code. The starter deliberately has
no ready-made `teaching/` answer tests. Generated test counts vary; do not replace
reviewed generated assertions with historical references or weaken them to pass.
Keep bug, feature and query changes separately reviewed, with a separate commit
per exercise.

```sh
./mvnw -q -Dtest=BaselineTest,CartContractTest,RemoveContractTest,QueryContractTest test
```

Run that selector once all three contracts exist; use each contract's selector
as it is generated. Generated boundary and checkout tests add cases alongside
the reviewed contracts. CI runs all activated tests on pushes and PRs. Passing
the four initial tests does not mean the known cart bug is fixed.

Current `main` also runs two `QuantityInputTest` regressions: fractional JSON
quantities must return 400 without creating an item or changing an existing cart.
Four `StartupLogTest` cases also cover the startup links, so the full starter
suite has ten tests. Integer-input hardening and keyboard focus-ring spacing do
not solve the quantity, removal or query tickets.

## UI, parallel improvements and checkout delivery

Follow the handbook's acceptance cards for Browser/Canvas UI work, then two
bounded improvements in isolated worktree sessions. Review each diff and grant
scoped permission before using Agent Merge to integrate its PR. Independently
critique the integrated result and add boundary tests without weakening the
reviewed contracts.

For the fourth ticket, use the existing orchestrator session with **exactly five
bounded specialists**: Order model, Checkout service, REST API, UI and Acceptance
tests. Agree their interfaces and file ownership before implementation; each
specialist returns its changes and evidence to the orchestrator, not a separate
checkout PR. The orchestrator owns integration and the full test suite:

```sh
./mvnw -q test
```

Checkout is a synthetic order-and-receipt exercise: no payment provider,
authentication or personal/customer data. Keep integer cents, server-owned prices,
quantities of 1–99 including accumulated quantities, and the existing cart contracts.
The supplied starter has no checkout implementation or checkout acceptance file;
generate those tests from the fourth ticket's acceptance card.

Review the final integrated diff and explicitly authorize publishing and merging
this checkout delivery. Only then does the orchestrator commit and push one
checkout branch, open one PR targeting **your repository's `main`**, and address
CI and review feedback within the approved scope. It squash-merges only with
passing checks and required approvals, reruns the full suite on postmerge `main`,
and verifies checkout and the receipt in the running app at that merged revision
after your restart. Do not reuse or retarget the earlier worker PRs.

Feature-branch tests or offline changes are not a merge. If publishing, approval,
checks, merging or runtime verification is blocked, preserve the work and mark
delivery incomplete. The reusable template's `main` stays intentionally unsolved;
only the participant's `main` should finish with the completed app.

## Skills, MCP and Chronicle

`java-junit`, `spring-boot-testing` and `java-hibernate-jpa` are complete pinned
Awesome Copilot skills with references and source records. Use only the guidance
relevant to the task. Their general recommendations never override the workshop's
H2-only, no-Docker stack; do not introduce Testcontainers or replace H2.

The `bootui-shopping-cart` MCP server in `.github/mcp.json` uses a loopback-only
endpoint. BootUI runs normally with masked values; this workshop uses it only
through the two configured diagnostic tools.
You do not need to use the dashboard. You control the running app and restart it
when needed.

Use `/chronicle` in Copilot App to investigate your named workshop sessions,
identify avoidable usage and choose one improvement. Before running it, limit the
analysis to those sessions and an explicit time range, and check what data will
be accessed. Review the results for private information before sharing. Missing
usage data is unknown, not zero; usage multipliers and byte counts are not token
counts or dollar costs.

## Reference solutions

This repository's immutable history remains the canonical source for the
published sample-code checkpoints. Reference tests are maintainer recovery
material, not files supplied in the learner starter.

| Versioned tag | State | Passing tests |
|---|---|---:|
| [`v2-start`](https://github.com/jdubois/copilot-shopping-cart-workshop/tree/v2-start) | Intentionally broken starter | 4 |
| [`v2-bugfix`](https://github.com/jdubois/copilot-shopping-cart-workshop/tree/v2-bugfix) | Repeated additions fixed | 7 |
| [`v2-feature`](https://github.com/jdubois/copilot-shopping-cart-workshop/tree/v2-feature) | Removal implemented | 10 |
| [`v2-performance`](https://github.com/jdubois/copilot-shopping-cart-workshop/tree/v2-performance) | N+1 fixed | 12 |

These immutable checkpoints cover only the first three tickets and their 12
historical reference tests, not the expanded curriculum, generated acceptance
tests, boundary tests or checkout.
They predate the current starter's fractional-input and keyboard-geometry
hardening; keep their pinned code and recorded results unchanged.
They are commits in one reference history on `reference/v2`, not duplicated
project directories. The `v1-*` tags and `reference/v1` remain unchanged for older
workshops. Review each ticket's diff, then the
[whole change across the first three tickets](https://github.com/jdubois/copilot-shopping-cart-workshop/compare/v2-start...v2-performance):
check application behavior, activated tests and the Remove button together, not
just the last performance commit. If you need help restarting from a reference
checkpoint, ask your facilitator. Keep your original project and distinguish
results from the reference solution from results you verified in your own work.

## Maintainers

Java 21 baseline, Spring Boot 4.1.2, BootUI 2.3.0, Maven wrapper 3.9.9.
Skills are pinned to `7e408815ddcb64889a3683799a85399331cfd4ef`.
See `NOTICE.md` and `.github/skills/provenance.json`.

For facilitator-led recovery, clone a tag into a separate directory:

```sh
git clone --branch v2-bugfix --single-branch https://github.com/jdubois/copilot-shopping-cart-workshop.git cart-reference-bugfix
```

This clone starts in detached HEAD. Create a local branch to continue editing;
its `origin` points to the template, not the participant's repository. Do not push
to the template. Preserve the participant's original project and record which
reference checkpoint was used.

The checkpoint verifier loads `tools/checkpoint-pins.json` from current `main` and
verifies every published checkpoint tag and reference tip against its expected
full commit SHA before running tests. Its `contractSourceRevision` pins
`c0ac24920dc16812e2c7187cc95245faffc84316`: the verifier reads
`teaching/{CartContractTest,RemoveContractTest,QueryContractTest}.java` directly
from that Git commit, not from the starter working tree or an unpublished website
copy. It compares every checkpoint's staged and activated contracts byte-for-byte
with that source, then activates contracts only in temporary reference worktrees.
Missing source commits or files are errors. Maintainers can recover a file with
`git show c0ac24920dc16812e2c7187cc95245faffc84316:teaching/CartContractTest.java`;
never overwrite a learner's reviewed generated tests.

Use a current maintainer checkout with full history and all published refs:

```sh
git fetch origin main 'refs/heads/reference/*:refs/remotes/origin/reference/*' --tags
git switch main
git merge --ff-only origin/main
python3 tools/verify-checkpoints.py
```

For recovery, compare `git rev-parse 'v2-bugfix^{commit}'` with the `v2-bugfix`
entry in the reviewed pin manifest before using the clone. The canonical
maintainer verifier checks all pins; a single-branch recovery clone is not a
replacement for that check. Missing or moved refs are errors: investigate rather
than updating the manifest to match an unexpected remote value.

Python is maintainer-only. The verifier uses temporary Git worktrees and changes
neither your current checkout nor tags. Receipts and per-check logs are written
under `target/checkpoint-checks/`. The seven checks execute 4, 3, 7, 3, 10, 2 and
12 tests with respectively 0, 2, 0, 2, 0, 2 and 0 expected assertion failures,
and no errors or skips. Reference CI runs only in the template
repository; participant repositories run the normal Maven suite.
`tools/vendor-skills.py` intentionally refreshes the pinned complete skill folders.
Do not move published tags or reference branches; create a new edition for later
fixture changes. Add its pins in a maintenance commit on `main` after creating
the tagged checkpoints, so no checkpoint needs to contain its own SHA. `main`
must retain starter behavior even after maintenance updates.
