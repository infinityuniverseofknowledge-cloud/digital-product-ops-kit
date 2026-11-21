#!/bin/sh
# Compatibility entry point; the scanner itself uses Python's standard library.
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$SCRIPT_DIR/audit_html_batch.py" "$@"
