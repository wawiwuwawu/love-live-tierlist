# Security Policy

This is a **static, read-only fan website** serving pre-generated data — there
is no backend, database, or user authentication to exploit. Still, we take
security seriously.

## Supported Versions

Only the latest `main` branch (the deployed GitHub Pages site) is supported.

## Reporting a vulnerability

Please **do not open a public issue** for security problems. Report privately
via a [GitHub Security Advisory](https://github.com/wawiwuwawu/love-live-tierlist/security/advisories/new)
(if you are a maintainer) or by opening a private disclosure through your
GitHub profile contact.

Given the nature of this project (static content only), most concerns fall
into these categories:

- **Data integrity** — wrong cover maps, accidental attribution of a song to
  the wrong album. Not a security bug, but please report it via a normal
  issue/PR.
- **Dependency risk** — the only runtime dependency is a pinned
  `html2canvas` script from a CDN. If that CDN is ever unavailable, the
  "Export PNG" button silently degrades; nothing is auto-executed beyond that
  script.
- **Supply chain** — our data pipeline uses `openpyxl`, `pillow`, `requests`,
  `pykakasi`. We pin versions in `requirements.txt`.

## Disclosure

We'll acknowledge reports promptly and, for valid issues, aim to update the
deployed site within a reasonable time. Thank you for helping keep the fan
community safe.