#!/usr/bin/env python3
"""Offline, review-first inventory of local HTML. Standard library only."""
import argparse
import csv
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys

MAX_FILE_BYTES = 5 * 1024 * 1024
CREDENTIAL = re.compile(r'password|api[_-]?key|secret|private[_-]?key|seed\s+phrase', re.I)


def spreadsheet_safe(value):
    """Prevent common spreadsheet formula execution; this changes risky cells."""
    value = str(value)
    return "'" + value if value.lstrip(' \t\r\n').startswith(('=', '+', '-', '@')) or value.startswith(('\t', '\r', '\n')) else value


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.title_parts = []
        self.form = False
        self.remote_scripts = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True
        elif tag == 'form':
            self.form = True
        elif tag == 'script':
            for name, value in attrs:
                if name == 'src' and value and re.match(r'^(https?:)?//', value.strip(), re.I):
                    self.remote_scripts += 1

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)


def scan(source):
    records, skipped = [], 0
    def onerror(error):
        raise error
    for root, dirs, files in os.walk(source, followlinks=False, onerror=onerror):
        root = Path(root)
        skipped += sum((root / name).is_symlink() for name in dirs)
        dirs[:] = sorted(name for name in dirs if not (root / name).is_symlink())
        for name in sorted(files):
            p = root / name
            if p.is_symlink():
                skipped += 1
                continue
            if p.suffix.lower() != '.html':
                continue
            if not p.is_file():
                raise ValueError(f'Not a regular HTML file: {p.relative_to(source)!s}')
            # Refuse large inputs rather than silently providing an incomplete scan.
            with p.open('rb') as f:
                raw = f.read(MAX_FILE_BYTES + 1)
            if len(raw) > MAX_FILE_BYTES:
                raise ValueError(f'HTML exceeds {MAX_FILE_BYTES} bytes: {p.relative_to(source)!s}')
            text = raw.decode('utf-8', errors='replace')
            parser = Inspector()
            parser.feed(text)
            parser.close()
            title = ' '.join(''.join(parser.title_parts).split())[:160]
            risk = bool(CREDENTIAL.search(text))
            # Avoid recording a possibly sensitive title in the output.
            if CREDENTIAL.search(title):
                title = '[redacted: credential-like title]'
            flags = []
            if not title: flags.append('MISSING_TITLE')
            if parser.form: flags.append('REVIEW_FORM_PRIVACY')
            if parser.remote_scripts: flags.append('REVIEW_REMOTE_SCRIPTS')
            if risk: flags.append('REVIEW_CREDENTIAL_LIKE_TEXT')
            records.append({'path': str(p.relative_to(source)), 'title': title, 'bytes': len(raw),
                            'has_form': 'yes' if parser.form else 'no',
                            'remote_script_count': parser.remote_scripts,
                            'credential_marker': 'yes' if risk else 'no', 'flags': flags})
    return records, skipped


def run(source, out):
    source = Path(source).resolve(strict=True)
    if not source.is_dir():
        raise ValueError('SOURCE must be a directory')
    out = Path(out).resolve()
    if out == source or source in out.parents:
        raise ValueError('Output directory must be outside SOURCE')
    records, skipped = scan(source)
    out.mkdir(parents=True, exist_ok=True)
    catalog, report = out / 'catalog.csv', out / 'release-gate.md'
    # Never overwrite previous review work, symlinks, or unrelated files.
    if catalog.exists() or catalog.is_symlink() or report.exists() or report.is_symlink():
        raise ValueError('Output files already exist; choose a new output directory')
    fields = ['path', 'title', 'bytes', 'has_form', 'remote_script_count', 'credential_marker']
    catalog_created = False
    report_created = False
    try:
        with catalog.open('x', encoding='utf-8', newline='') as f:
            catalog_created = True
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for record in records:
                writer.writerow({k: spreadsheet_safe(record[k]) for k in fields})
        with report.open('x', encoding='utf-8', newline='\n') as f:
            report_created = True
            f.write('# Release review queue\n\n')
            f.write('Static indicators only; not a security audit or a release approval.\n\n')
            f.write(f'HTML files scanned: {len(records)}. Symlinks skipped: {skipped}.\n\n')
            for record in records:
                if record['flags']:
                    # JSON escaping plus HTML escaping prevents markup and control injection.
                    safe_name = html.escape(json.dumps(record['path'], ensure_ascii=True))
                    f.write(f'- {safe_name}: {", ".join(record["flags"])}\n')
    except Exception:
        # Remove only files opened successfully by this invocation.
        if catalog_created:
            catalog.unlink(missing_ok=True)
        if report_created:
            report.unlink(missing_ok=True)
        raise
    return len(records), skipped


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='local directory containing HTML files')
    parser.add_argument('out', nargs='?', default='output', help='new output directory outside source')
    args = parser.parse_args(argv)
    try:
        count, skipped = run(args.source, args.out)
    except (OSError, ValueError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1
    print(f'Inventoried {count} HTML files; skipped {skipped} symlinks.')
    print(f'Catalog: {Path(args.out) / "catalog.csv"}')
    print(f'Review queue: {Path(args.out) / "release-gate.md"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
