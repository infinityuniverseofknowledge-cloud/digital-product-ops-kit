# Digital Product Ops Kit

A lightweight, review-first system for cataloging static HTML projects and preparing accurate English digital-product listing drafts.

## What it does

- inventories HTML files, titles, sizes, forms and third-party scripts
- flags simple release-review risks such as credential-like strings
- writes JSON, CSV and Markdown catalogs
- produces a human review gate
- prepares conservative product-listing drafts from verified metadata

## What it deliberately does not do

- publish products, change prices, submit applications or send outreach
- handle passwords, API keys, payment data, wallets or private data
- fabricate testimonials, earnings, licences, security claims or AI capabilities

Publishing, pricing and external submissions require human review and explicit approval.

## Run

```bash
python3 pipeline.py catalog /path/to/html-projects --out output/catalog
python3 pipeline.py gate output/catalog/catalog.json --out output/release-gate.md
python3 pipeline.py draft output/catalog/catalog.json --project Example.html --out output/listing-draft.md
```

## Recommended workflow

1. Catalog a small batch.
2. Open and manually test every project proposed for release.
3. Resolve or disclose every gate warning.
4. Add genuine screenshots, exact deliverables, licence and support terms.
5. Review the English listing and market-based price.
6. Publish one product only after an explicit approval.

## Limits

Static analysis is not a security certification. A project may still behave differently at runtime, so manual browser testing remains mandatory before public claims or sale.
