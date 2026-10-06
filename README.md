# QA Pipeline — From Requirements to Closed Bugs

**English** | [ภาษาไทย](README.th.md)

![Skills](https://img.shields.io/badge/Skills-15-0f766e?style=flat-square)
![Playwright](https://img.shields.io/badge/Automation-Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white)
![Redmine](https://img.shields.io/badge/Defect%20Tracking-Redmine-B32024?style=flat-square&logo=redmine&logoColor=white)
![Python](https://img.shields.io/badge/Python-3-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A set of **15 AI-agent skills** that take one feature through the whole QA lifecycle — collecting requirements, writing the test plan and test cases, running Playwright automation, reporting Go / No-Go, opening Redmine tickets for failures, retesting after the fix, and closing the tickets.

> **Note:** the skill definitions (`skills/*/SKILL.md`) are written in **Thai**. They are written to work with both Claude and Gemini and avoid platform-specific tool names. This README explains the structure in English.

---

<p align="center">
  <a href="docs/images/qa-pipeline-flow-en.png"><img src="docs/images/qa-pipeline-flow-en.png" alt="QA Pipeline flow" width="100%" /></a>
</p>

## What this project demonstrates

- **A repeatable QA process, not one-off prompts:** 15 stages in 4 phases, each with defined inputs, outputs and gates.
- **Human sign-off where it matters:** only 3 points need a person (source approval, test-plan approval, and the signature on the QA report). The system is designed so automation cannot fill these in on a person's behalf.
- **Traceability:** the RTM (Requirement Traceability Matrix) is recomputed from source files every time, never trusted from a previous run.
- **Real tools, real evidence:** the worked example runs real Playwright tests, opens and closes a real Redmine ticket, and sends a real notification email, with screenshots at every external step.
- **Credential safety:** Redmine URL / API key and SMTP credentials are requested per run, passed by environment variable only, and never written to files.

## Worked example

[`examples/newsletter-email-subscription/`](examples/newsletter-email-subscription/) runs all 15 stages on one small feature (newsletter sign-up in a site footer).

| | |
| :--- | :--- |
| Test cases | 11 (TC-001 – TC-011) |
| Automation result | 10 passed, 1 failed (TC-005, found by the automation) |
| Defect lifecycle | Redmine ticket opened → developer fix → retest passed → ticket closed |
| QA report verdict | Conditional Go (no P0 failures, one P1 failure) before the fix |
| Browsers | Chromium only (see limitations below) |

**Limitations, stated plainly**

- The feature under test is **simulated**: a small Flask demo app (`automation/demo-app/server.py`) was written to follow the business rules, with one bug planted on purpose (BR-002). The pass/fail results come from real test runs against it, but it is not a production system.
- Cross-browser testing (TC-009) was planned for 4 browsers but the run environment only had Chromium. Stages 06a and 07 are therefore reported as **Complete (Partial)** rather than hidden.
- The Redmine instance is a hosted (Planio) workspace used only for this example.

---

## The 15 stages

| Phase | Purpose | Stages |
| :--- | :--- | :--- |
| **A — Analyse requirements** | Collect sources, plan, design test cases | 00-pre, 00, 01 – 05 |
| **B — Prepare & execute** | Test data, automation, results, traceability | 06, 06a, 07, RTM |
| **C — Report & decide** | Go / Conditional Go / No-Go report | 08 |
| **D — Close defects (loops)** | Open ticket → retest → close, until no failures remain | 09, 10, 10a |

| Stage | Skill | What it does | Output | Type |
| :--- | :--- | :--- | :--- | :--- |
| 00-pre | `00-pre-source-ingest` | Gather requirements from many sources into one source set; flag gaps and conflicts | `00-pre-source-ingest.md` | Needs approval |
| 00 | `00-test-plan` | Scope, exit criteria, environment, schedule, risks | `testplans/TP-*.md` | Needs approval |
| 01 | `01-requirement-review` | Extract business rules and open questions | `01-requirement-review.md` | Automatic |
| 02 | `02-e2e-flow-designer` | Design end-to-end user flows | `02-e2e-flow.md` | Automatic |
| 03 | `03-test-case-generator` | Generate test cases covering every rule and flow | `03-test-case-workbook.xlsx` | Automatic |
| 04 | `04-coverage-review` | Check the test cases against requirements for gaps | `04-coverage-review.md` | Automatic |
| 05 | `05-risk-analysis` | Assign priority P0 – P3 to each test case | `05-risk-analysis.md` | Automatic |
| 06 | `06-test-data-generator` | Turn test-data descriptions into concrete mock data | `06-test-data.md` | Automatic |
| 06a | `06a-qa-automation-script` | Write and run Playwright scripts, capture evidence | `automation/*`, `screenshots/*` | Automatic |
| 07 | `07-result-analysis` | Summarise results and root causes | `07-result-analysis.docx` | Automatic |
| RTM | `07a-RTM-qa-reconcile` | Recompute the traceability matrix from scratch | `RTM-traceability-matrix.xlsx` | Automatic |
| 08 | `08-qa-report-generator` | Final Go / Conditional Go / No-Go report | `08-qa-report.docx` | Needs signature |
| 09 | `09-redmine-logging` | Open a Redmine ticket for each failure with evidence | Redmine tickets | Automatic* |
| 10 | `10-qa-retest` | Re-run failed cases after the developer's fix | `10-retest-run-result.json` | Automatic* |
| 10a | `10a-qa-retest-closure` | Close (pass) or comment on (fail) the ticket | Ticket updated | Automatic* |

\* Stages 09, 10 and 10a need a Redmine URL and API key from the user on every run.

The full flow diagram is at the top of this page; an interactive HTML version is in [`docs/qa-pipeline-flow.html`](docs/qa-pipeline-flow.html).

---

## Repository structure

```
.
├── skills/                    # the 15 skill definitions, in flow order
│   ├── 00-pre-source-ingest/ … 10a-qa-retest-closure/
│   └── _shared/               # shared Python modules (workbook I/O, Playwright runner, Redmine & email helpers)
├── examples/
│   └── newsletter-email-subscription/   # full 15-stage worked example
├── docs/
│   └── qa-pipeline-flow.html  # standalone flow diagram
└── test-reports/              # test reports for the skills themselves
```

## Closing a feature

A feature is considered closed only when **all** of these hold:

1. Stages 01 – 10a are marked Complete in `_pipeline-manifest.md`.
2. No test case is left in Fail status in the workbook.
3. Stages 00-pre and 00 were approved by a person (the "QA Review & Sign-off" section filled in by hand).
4. The QA Lead and PM / Product Owner signature fields in `08-qa-report.docx` are signed.

Items 3 and 4 always require a real person; nothing in the pipeline can do them automatically.

## Security of credentials

- The Redmine URL and API key must be requested from the user **every time** stages 09 – 10a run, and are never saved or cached in any file.
- They are provided through environment variables only, never as command-line arguments.
- The same rule applies to the SMTP credentials used to email the developer.

## License

Released under the [MIT License](LICENSE).

## Author

**Jirapat Jiramonthon** — [GitHub @Jiramonthon-j](https://github.com/Jiramonthon-j) · [LinkedIn](https://www.linkedin.com/in/jirapat-jiramonthon-930240395)
