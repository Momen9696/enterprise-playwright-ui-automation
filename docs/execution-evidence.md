# Execution evidence

These commands were run on macOS with Python 3.13.2 from the project virtualenv on 24 November 2026. Nothing below is estimated.

## Quality checks

```text
ruff check .            All checks passed
ruff format --check .   53 files already formatted
python scripts/secret_scan.py
                        Secret scan passed (75 files)
python -m pip_audit -r requirements.txt
                        No known vulnerabilities found
```

The audit was repeated after `requirements.txt` was pinned. The second run also reported no known vulnerabilities.

## Chromium, full suite, 2 workers

```text
created: 2/2 workers
2 workers [96 items]
96 passed in 8.90s
```

The 96 tests are 35 unit, 8 API, and 53 UI. Unit and API tests do not launch a browser. The UI tests used Chromium.

## Firefox, UI suite, 2 workers

```text
created: 2/2 workers
2 workers [53 items]
53 passed in 20.28s
```

## WebKit, UI suite, 2 workers

```text
created: 2/2 workers
2 workers [53 items]
53 passed in 12.79s
```

## Failure artifacts

`python scripts/capture_failure_evidence.py` ran `tests/meta/test_failure_artifacts.py`, which is excluded from normal runs by `-m "not evidence"`. Pytest exited 1, as intended, because the login page has no `missing-marker` element.

The script then found:

| Artifact | Size |
| --- | --- |
| `artifacts/screenshots/tests_meta_test_failure_artifacts.py_test_failure_artifacts_are_captured.png` | 34,004 bytes |
| `artifacts/traces/tests_meta_test_failure_artifacts.py_test_failure_artifacts_are_captured.zip` | 75,771 bytes |
| `artifacts/videos/.../page@1d06d1cd3954be386a3028b972aa3f96.webm` | 109,108 bytes |

A copy of the screenshot is `docs/evidence/failure-screenshot.png`. The trace and video stay in `artifacts/`, which is gitignored because those files are produced locally on failure.

## Reports

The Chromium run wrote `reports/pytest.html` and Allure result files under `reports/allure-results/`. Those directories are gitignored. Later Firefox and WebKit runs append to the same Allure directory, so a file count there is not the Chromium pass count. The pytest summaries above are the pass counts.
