# Digital Product Ops Kit

A lightweight, review-first toolkit for inventorying local static HTML projects and preparing truthful digital product listings. It does not publish, sell, send outreach, or make AI, security, or earnings claims.

## Offline HTML inventory

Requirements: Python 3.8+ and a POSIX shell (including Termux). No third-party packages or paid services. The scanner reads HTML as data and does not run its scripts or make network requests.

```sh
sh audit_html_batch.sh /path/to/projects /path/to/new-output
# or
python3 audit_html_batch.py /path/to/projects /path/to/new-output
```

The output directory must be outside the source tree. `catalog.csv` and `release-gate.md` must not already exist; previous work is never intentionally overwritten. The scanner reads `.html` files up to 5 MiB each, skips and counts symlinks, fails on unreadable or oversized inputs, and does not silently report partial results as complete. Output may still contain filenames and titles; treat it as potentially sensitive and review it before sharing. Spreadsheet-formula-like path and title cells receive a leading apostrophe, so these cells do not preserve the literal original value.

The catalog lists file size, parsed title, form presence, static HTTP(S) or protocol-relative script `src` count, and a simple credential-like text marker. The queue flags files needing human review. A marker is not proof a secret exists, and absence of a marker is not proof it doesn't. Titles containing known marker words are redacted; other sensitive text could still appear in titles or paths.

**Limitations:** This is not a security audit or a release approval. Detection is heuristic: it does not execute JavaScript or discover dynamic imports, other resource types, CSS URLs, obfuscated credentials, malformed or unusual encodings, privacy violations, rights issues, or product functionality. HTML is decoded as UTF-8 with replacement. Scanning assumes a trusted local filesystem without concurrent malicious modification. Manually test every proposed product and verify rights, exact deliverables, claims and support terms before distribution. License is not specified in this repository.

## Tests

```sh
python3 -m unittest -v test_audit_html_batch
```

## Review-first workflow

1. Inventory a small batch locally.
2. Manually test each proposed product and resolve or disclose review warnings.
3. Verify authorship, third-party licenses, privacy, factual claims, and actual deliverables.
4. Prepare truthful English listings and real screenshots; review before publishing.
5. Obtain approval for spending, binding commitments or other consequential actions.
