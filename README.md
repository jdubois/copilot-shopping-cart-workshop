# GitHub Copilot App: shopping-cart workshop

Learn to direct Copilot App through a realistic Java development loop:
**reproduce → plan → implement → inspect → verify**.

Follow the [workshop handbook](https://www.julien-dubois.com/workshops/copilot-app/).
This hands-on workshop covers a cart bug, generated removal
and a Hibernate N+1 investigation through MCP. Parallel sessions and integration
are required, followed by a Chronicle usage clinic after integration and a final
handoff. Native App flows remain pilot gates.

## Create your own repository

Choose **Use this template → Create a new repository** on
[this repository](https://github.com/jdubois/copilot-shopping-cart-workshop).
Leave **Include all branches** off: `main` contains the intentionally broken
starter. Your new repository has independent history and does not inherit the
solution tags.

Clone your new repository, not the template, then open it in Copilot App.
Use JDK 21+, Git and a supported App account. No Docker, Node, external database
or payment provider is needed. The three Java skills are already installed in
`.github/skills/`.

```sh
./mvnw -q -Dtest=BaselineTest test
git rev-parse HEAD
```

Four baseline tests pass, but adding the same product twice is not covered.
Record your SHA, then start one shop:

```sh
./mvnw spring-boot:run -Dspring-boot.run.arguments=--workshop.revision=YOUR_SHA
```

Open http://127.0.0.1:18765. Add the €10 Notebook twice: the starter incorrectly
shows quantity 1 / €10 instead of 2 / €20. `GET /api/workshop` returns revision/PID.
Restarting or using Reset cart clears synthetic data. Windows: `.\mvnw.cmd`.
The code is intentionally defective and local-only; do not deploy it or use real
customer data.

## Three separate tickets

1. Activate `teaching/CartContractTest.java`: 3 tests, 2 expected failures in the
   starter. Fix accumulated quantity and total, not just displayed text.
2. Activate `teaching/RemoveContractTest.java`: generate DELETE
   `/api/cart/items/{productId}`, a Remove button and tests. Existing line:
   200 with updated cart and remaining item count; missing line: 404, no state
   change, including a catalogue product that is not in the cart.
3. Activate `teaching/QueryContractTest.java`: inspect GET `/api/cart` through
   BootUI MCP for 8 distinct products. Tests measure the completed HTTP response
   at 8 and 16 products; the query budget is 1 SELECT instead of 9 and 17.

Copy each acceptance file unchanged into
`src/test/java/com/juliendubois/workshop/`, review and commit it before fixing code.
`teaching/` keeps future tests out of Maven discovery; it is not application code.
Do not weaken the tests. Keep bug, feature and query changes separately reviewed.

```sh
./mvnw -q -Dtest=BaselineTest,CartContractTest,RemoveContractTest,QueryContractTest test
```

The final suite has 12 tests. CI runs all activated tests on pushes and PRs.
Your baseline CI can be green while the known bug still exists.

## Skills, MCP and Chronicle

`java-junit`, `spring-boot-testing` and `java-hibernate-jpa` are complete pinned
Awesome Copilot skills with references and provenance. Invoke only the guidance
relevant to the task. Their general recommendations never override the workshop's
H2-only, no-Docker stack; do not introduce Testcontainers or replace H2.

The `.github/mcp.json` endpoint is loopback-only. BootUI runs normally with masked
values; this workshop uses it only through the two configured diagnostic tools.
No dashboard tour is required. The human owns the running JVM and restart.

Use `/chronicle` in Copilot App to investigate your named workshop sessions,
identify avoidable usage and choose one improvement. Scope and review results
before sharing. Do not equate missing accounting data, usage multipliers or byte
counts with tokens or dollars.

## Reference solutions

This repository is the **only source of sample code and reference solutions**.
There are no maintained source ZIPs or copies in the website repository.

| Versioned tag | State | Green tests |
|---|---|---:|
| [`v2-start`](https://github.com/jdubois/copilot-shopping-cart-workshop/tree/v2-start) | Intentionally broken starter | 4 |
| [`v2-bugfix`](https://github.com/jdubois/copilot-shopping-cart-workshop/tree/v2-bugfix) | Repeated additions fixed | 7 |
| [`v2-feature`](https://github.com/jdubois/copilot-shopping-cart-workshop/tree/v2-feature) | Removal implemented | 10 |
| [`v2-performance`](https://github.com/jdubois/copilot-shopping-cart-workshop/tree/v2-performance) | N+1 fixed | 12 |

These are commits in one reference history on `reference/v2`, not duplicated
project directories. The `v1-*` tags and `reference/v1` remain unchanged for older
workshops. Review each ticket's diff, then the
[whole change from starter to final](https://github.com/jdubois/copilot-shopping-cart-workshop/compare/v2-start...v2-performance):
check application behavior, activated tests and the Remove button together, not
just the last performance commit. Clone a tag into a separate directory for
labelled recovery:

```sh
git clone --branch v2-bugfix --single-branch https://github.com/jdubois/copilot-shopping-cart-workshop.git cart-reference-bugfix
```

This clone starts in detached HEAD. Create a local branch to continue editing;
its `origin` points to the template, not your personal repository. Do not push to
the template. Preserve your original project and mark reference work honestly.

## Maintainers

Java 21 baseline, Spring Boot 4.1.2, BootUI 2.3.0, Maven wrapper 3.9.9.
Skills are pinned to `7e408815ddcb64889a3683799a85399331cfd4ef`.
See `NOTICE.md` and `.github/skills/provenance.json`.

The reference gate loads `tools/checkpoint-pins.json` from current `main` and
verifies every published checkpoint tag and reference tip against its expected
full commit SHA before running tests. It does not trust a tag just because Git
can resolve it. Use a current maintainer checkout with all published refs:

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
12 tests with respectively 0, 2, 0, 2, 0, 2 and 0 intended assertion failures,
and no errors or skips. Reference CI runs only in the template
repository; participant repositories run the normal Maven suite.
`tools/vendor-skills.py` intentionally refreshes the pinned complete skill folders.
Do not move published tags or reference branches; create a new edition for later
fixture changes. Add its pins in a maintenance commit on `main` after creating
the tagged checkpoints, so no checkpoint needs to contain its own SHA. `main`
must retain starter behavior even after maintenance updates.
