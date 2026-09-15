"""Offline import of an authorized account-list snapshot. Never drives a browser."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def parse_snapshot(text, source):
    lines = text.splitlines()
    headers = [(i, len(line) - len(line.lstrip())) for i, line in enumerate(lines)
               if re.match(r"^\s*- listitem \[ref=[^\]]+\]:", line)]
    if not headers:
        raise ValueError("No account list items found; select the list container")
    level = min(indent for _, indent in headers)
    starts = [i for i, indent in headers if indent == level]
    accounts = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        block = '\n'.join(lines[start:end])
        name = None
        for value in re.findall(r'^\s*- (?:generic \[ref=[^\]]+\]|text): (.+)$', block, re.M):
            if re.fullmatch(r'\d+个作品未看|认证徽章', value.strip()):
                continue
            name = value.strip()
            break
        if name is None:
            raise ValueError(f"Item {index + 1} has no readable name; refusing silent omission")
        icons = re.findall(r'^\s*- img "([^\"]+)"', block, re.M)
        token = hashlib.sha256(f'{source}:{index}:{name}'.encode()).hexdigest()[:16]
        accounts.append(dict(record_id='provisional-' + token, ordinal=index + 1,
                             nickname=name, visible_image_labels=icons,
                             profile_url=None, douyin_id=None,
                             identity_status='unverified', content_status='unreviewed',
                             source_snapshot=source, evidence=[], user_confirmed=False))
    return dict(schema_version=1, source_snapshot=source, observed_records=len(accounts),
                distinct_nicknames=len({a['nickname'] for a in accounts}),
                identity_deduplicated=False, list_complete=False, accounts=accounts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = parse_snapshot(args.snapshot.read_text(encoding='utf-8-sig'), str(args.snapshot))
    if args.output.exists():
        parser.error('Output exists; do not overwrite a research checkpoint')
    if not args.output.parent.is_dir():
        parser.error('Create/verify the private output directory first')
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(f'Imported {result["observed_records"]} provisional records; none content-verified')


if __name__ == '__main__':
    main()
