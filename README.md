# Digital Product Ops Kit

A lightweight, review-first system for cataloging static HTML projects and preparing accurate English digital-product listing drafts.

## What it does

- inventories HTML files, titles, sizes, forms and third-party scripts
- flags simple release-review risks such as credential-like strings
- writes CSV review artifacts through `audit_html_batch.sh`
- supports a review-first content-factory workflow

## What it deliberately does not do

- publish products, change prices, submit applications or send outreach
- handle passwords, API keys, payment data, wallets or private data
- fabricate testimonials, earnings, licences, security claims or AI capabilities

Publishing, pricing and external submissions require human review and explicit approval.

## HTML audit

```bash
sh audit_html_batch.sh path/to/projects output
```

The audit produces a catalog and release queue. It detects only basic static indicators. Manually test every project before public claims or sale.

## Current verified run

- 238 HTML files inventoried in the Hackathon Projects Collection
- 52 projects marked for human review by basic static checks
- AetherGrid Colossus was cataloged: 44,055 bytes, no form, no remote script found by this static scan, no credential-like marker found by this static scan
- 3,000 English editorial briefs generated locally as planning data; they are not finished books or audiobooks, and none were published

## Release workflow

1. Catalog a small batch.
2. Test every proposed product manually.
3. Resolve or disclose every gate warning.
4. Add genuine screenshots, exact deliverables, licence and support terms.
5. Expand selected briefs with original writing, fact review and rights review.
6. Record audio only through an approved licensed voice workflow.
7. Review the English listing and price.
8. Publish one product after an explicit approval.
