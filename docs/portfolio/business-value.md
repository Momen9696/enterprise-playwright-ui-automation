# Business value

HarborDesk and this framework are a portfolio sample. The design maps to teams that need browser regression without coupling the suite to a public website that can change overnight.

## Use cases

- A QA team inherits a web product and needs one pattern for page objects, waits, and failure artifacts before writing hundreds of tests.
- A release pipeline must run the same scenarios on Chromium, Firefox, and WebKit and keep the HTML report, traces, and screenshots from the pull request.
- Test data has to be unique per run, while a small set of seeded records stays stable for pagination and search.
- UI checks need an API to create a user or a record and to delete it afterward, instead of clicking through setup for every case.
- An audit asks where passwords appear in logs. Secret fields are masked, and the sample accounts are documented fixtures.

## What a client engagement would change

- Point `--base-url` at the real environment and turn off the local process.
- Replace HarborDesk page objects with the product's pages. Keep fixtures, settings, reporting, and CI.
- Move accounts to a secret store. The YAML users in this repo are intentional sample data.
- Turn on `--reruns` only for known-unstable environment issues, and keep the default at zero so real product bugs stay visible.

## Sample data

JSON cases live in `test_data/`. Generated users use `@demo.local` addresses and passwords that meet the demo rule: at least 8 characters, with a letter and a digit.
