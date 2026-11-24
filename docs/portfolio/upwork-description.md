# Upwork portfolio description

**Enterprise Web UI Automation Framework (Playwright + Python)**

I designed and built a browser automation framework for a local work-tracking application called HarborDesk. The suite uses the Page Object Model, Playwright fixtures, and Pytest. It runs on Chromium, Firefox, and WebKit, headless or headed, with environment YAML files and CLI options for the browser, profile, base URL, and failure video.

The framework covers login and logout, registration, dashboard counts, profile edits, create/update/delete, search and filters, pagination, session expiry, and role checks. Invalid cases come from JSON files. New users and items come from Faker. An HTTP client creates and deletes data around the UI flow. Failures keep a screenshot and a Playwright trace. Video is available with `--record-video`. Reports are pytest-html and Allure. GitHub Actions runs the suite on every push and pull request for all three browsers and uploads the results.

HarborDesk is a self-contained FastAPI app with synthetic accounts. The run does not depend on a public website.

Verification on macOS, Python 3.13.2, recorded in `docs/execution-evidence.md`:

- 96 tests passed on Chromium with 2 workers in 8.90s (35 unit, 8 API, 53 UI)
- The same 53 UI tests passed on Firefox in 20.28s and on WebKit in 12.79s, each with 2 workers
- Ruff reported no findings and the secret scan passed
- pip-audit reported no known vulnerabilities
- An intentional failure produced a 34,004-byte screenshot, a 75,771-byte trace, and a 109,108-byte video

**Skills:** Python, Playwright, Pytest, pytest-xdist, Page Object Model, FastAPI, GitHub Actions, UI test automation, cross-browser testing
