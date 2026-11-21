import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import audit_html_batch as audit


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source dir'
        self.source.mkdir()
        self.out = self.root / 'out dir'

    def add(self, name, text):
        p = self.source / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf8')
        return p

    def read(self):
        with (self.out / 'catalog.csv').open(encoding='utf8', newline='') as f:
            return list(csv.DictReader(f))

    def test_inventory_and_flags(self):
        self.add('a, one.html', '<title>Hello, world</title><form></form><script src="https://example.invalid/x.js"></script> password')
        audit.run(self.source, self.out)
        row = self.read()[0]
        self.assertEqual(row['path'], 'a, one.html')
        self.assertEqual(row['title'], 'Hello, world')
        self.assertEqual((row['has_form'], row['remote_script_count'], row['credential_marker']), ('yes', '1', 'yes'))
        report = (self.out / 'release-gate.md').read_text()
        self.assertIn('REVIEW_FORM_PRIVACY', report)
        self.assertNotIn(' password', report)

    def test_real_script_src_only(self):
        self.add('x.HTML', '<title>OK</title><a href="https://example.invalid">x</a><!-- <script src="https://bad"> --><script src="//cdn.invalid/a.js"></script><script src="local.js"></script>')
        audit.run(self.source, self.out)
        self.assertEqual(self.read()[0]['remote_script_count'], '1')

    def test_missing_title(self):
        self.add('a.html', '<h1>No title</h1>')
        audit.run(self.source, self.out)
        self.assertIn('MISSING_TITLE', (self.out / 'release-gate.md').read_text())

    def test_title_and_path_formula_safe(self):
        self.add('=HYPERLINK("evil").html', '<title>=1+1</title>')
        audit.run(self.source, self.out)
        row = self.read()[0]
        self.assertTrue(row['path'].startswith("'="))
        self.assertEqual(row['title'], "'=1+1")

    def test_symlink_skipped(self):
        outside = self.root / 'outside.html'
        outside.write_text('<title>external</title>')
        (self.source / 'link.html').symlink_to(outside)
        (self.source / 'linked-dir').symlink_to(self.root, target_is_directory=True)
        self.assertEqual(audit.run(self.source, self.out), (0, 2))

    def test_no_overwrite(self):
        self.out.mkdir()
        p = self.out / 'catalog.csv'
        p.write_text('keep')
        with self.assertRaises(ValueError): audit.run(self.source, self.out)
        self.assertEqual(p.read_text(), 'keep')

    def test_output_symlink_refused(self):
        self.out.mkdir()
        (self.out / 'release-gate.md').symlink_to(self.root / 'missing')
        with self.assertRaises(ValueError): audit.run(self.source, self.out)
        self.assertFalse((self.out / 'catalog.csv').exists())

    def test_source_nested_output_refused(self):
        with self.assertRaises(ValueError): audit.run(self.source, self.source / 'output')

    def test_oversized_input_fails_before_output(self):
        self.add('big.html', 'x' * (audit.MAX_FILE_BYTES + 1))
        with self.assertRaises(ValueError): audit.run(self.source, self.out)
        self.assertFalse(self.out.exists())

    def test_sensitive_title_redacted(self):
        self.add('a.html', '<title>password: sensitive-example</title>')
        audit.run(self.source, self.out)
        self.assertNotIn('sensitive-example', (self.out / 'catalog.csv').read_text())

    def test_cli_wrapper_with_spaces(self):
        self.add('file space.html', '<title>Test</title>')
        wrapper = Path(__file__).with_name('audit_html_batch.sh')
        result = subprocess.run(['sh', str(wrapper), str(self.source), str(self.out)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.read()), 1)

    def test_missing_source(self):
        result = subprocess.run([sys.executable, audit.__file__, str(self.root / 'absent'), str(self.out)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.out.exists())

    def test_cleanup_after_report_failure(self):
        original_open = Path.open
        def failing_open(path, *args, **kwargs):
            if path.name == 'release-gate.md':
                raise OSError('simulated failure')
            return original_open(path, *args, **kwargs)
        with patch.object(Path, 'open', failing_open):
            with self.assertRaises(OSError): audit.run(self.source, self.out)
        self.assertFalse((self.out / 'catalog.csv').exists())

    def test_markup_in_path_is_escaped(self):
        self.add('<img src=x onerror=alert(1)>.html', '')
        audit.run(self.source, self.out)
        report = (self.out / 'release-gate.md').read_text()
        self.assertNotIn('<img', report)
        self.assertIn('&lt;img', report)


if __name__ == '__main__':
    unittest.main()
