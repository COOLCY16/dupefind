#!/usr/bin/env python3
"""dupefind: find duplicate files by content. No dependencies.

Usage: python dupefind.py FOLDER [FOLDER ...] [--min-size BYTES] [--json]
"""

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

__version__ = "0.1.0"
CHUNK_SIZE = 1024 * 1024  # 1 MiB


def iter_files(root, min_size=1):
    """Yield regular files under root of at least min_size bytes (skips symlinks)."""
    for dirpath, _dirs, names in os.walk(root):
        for name in names:
            path = Path(dirpath) / name
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                if path.stat().st_size >= min_size:
                    yield path
            except OSError:
                continue


def hash_file(path, algorithm="sha256"):
    digest = hashlib.new(algorithm)
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(paths, algorithm="sha256"):
    """Group identical files: bucket by size first, then hash only matching sizes."""
    by_size = defaultdict(list)
    for path in paths:
        try:
            by_size[path.stat().st_size].append(path)
        except OSError:
            continue

    groups = defaultdict(list)
    for same_size in by_size.values():
        if len(same_size) < 2:
            continue
        for path in same_size:
            try:
                groups[hash_file(path, algorithm)].append(path)
            except OSError:
                continue

    return {d: sorted(f) for d, f in groups.items() if len(f) > 1}


def wasted_bytes(groups):
    return sum(f[0].stat().st_size * (len(f) - 1) for f in groups.values())


def human_size(num_bytes):
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{int(size)} B" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="dupefind", description="Find duplicate files in one or more folders."
    )
    parser.add_argument("folders", nargs="+", type=Path, help="folders to scan")
    parser.add_argument("--min-size", type=int, default=1, metavar="BYTES",
                        help="ignore files smaller than this (default: 1)")
    parser.add_argument("--algorithm", default="sha256",
                        choices=["md5", "sha1", "sha256", "blake2b"])
    parser.add_argument("--json", action="store_true", help="output JSON")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)

    for folder in args.folders:
        if not folder.is_dir():
            print(f"error: not a directory: {folder}", file=sys.stderr)
            return 2

    files = (p for folder in args.folders for p in iter_files(folder, args.min_size))
    groups = find_duplicates(files, args.algorithm)

    if args.json:
        print(json.dumps({
            "groups": [[str(p) for p in paths] for paths in groups.values()],
            "wasted_bytes": wasted_bytes(groups),
        }, indent=2))
    elif not groups:
        print("No duplicates found.")
    else:
        for number, paths in enumerate(groups.values(), start=1):
            print(f"Group {number} ({human_size(paths[0].stat().st_size)} each):")
            for path in paths:
                print(f"  {path}")
        print(f"\n{len(groups)} duplicate group(s), "
              f"{human_size(wasted_bytes(groups))} reclaimable.")

    return 1 if groups else 0


if __name__ == "__main__":
    sys.exit(main())
