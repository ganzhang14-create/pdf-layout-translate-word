"""Read-only DOCX structural audit; standard library only. Not a rendering check."""
import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def audit(path, expected_pages=None):
    findings = []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError('Corrupt ZIP entry: ' + bad)
        root = ET.fromstring(archive.read('word/document.xml'))
        texts = [n.text or '' for n in root.iter(W + 't')]
        sections = list(root.iter(W + 'sectPr'))
        tables = list(root.iter(W + 'tbl'))
        if not tables:
            findings.append('No native Word tables found; check editable-table requirement.')
        if expected_pages is not None and len(sections) != expected_pages:
            findings.append('Section count differs from expected pages; render to determine actual pagination.')
        chinese = [t for t in texts if re.search(r'[\u4e00-\u9fff]', t)]
        if chinese:
            findings.append('Chinese text remains in editable XML; review whether intentional.')
        suspicious = [t for t in texts if re.search(r'Evaluation Warning|Spire\.Doc|\bTODO\b|\bTBD\b|\[handwritten.*?unclear\]|\billegible\b|\bmasked\b', t, re.I)]
        if suspicious:
            findings.append('Review trial marks, placeholders or explicitly uncertain source text.')
        comments = [n for n in archive.namelist() if re.search(r'word/comments[^/]*\.xml$', n)]
        if comments:
            findings.append('Comments present; verify that printing does not change the layout.')
        dimensions = []
        for section in sections:
            size = section.find(W + 'pgSz')
            dimensions.append({k: round(int(size.get(W + k))/20, 2) for k in ('w', 'h')} if size is not None else None)
    return {'file': str(path.resolve()), 'native_tables': len(tables),
            'sections_not_rendered_pages': len(sections), 'section_sizes_pt': dimensions,
            'chinese_text_examples': chinese[:8], 'review_text_examples': suspicious[:8],
            'findings': findings, 'visual_review_required': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('docx', type=Path)
    parser.add_argument('--expected-pages', type=int, help='Only for documents deliberately authored one section per page')
    args = parser.parse_args()
    try:
        report = audit(args.docx, args.expected_pages)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True))
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 1 if report['findings'] else 0


if __name__ == '__main__':
    sys.exit(main())
