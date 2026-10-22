# dupefind

Find duplicate files by content. One Python file, no dependencies.

It groups files by size first, then hashes only the files that share a size, so scanning big folders stays fast. It never deletes or changes anything; it only reports.

## Usage

```bash
python dupefind.py ~/Downloads ~/Pictures
```

```
Group 1 (2.4 MB each):
  /home/me/Downloads/photo.jpg
  /home/me/Pictures/photo-copy.jpg

1 duplicate group(s), 2.4 MB reclaimable.
```

### Options

| Option | Description |
| --- | --- |
| `--min-size BYTES` | Ignore files smaller than this (default: 1) |
| `--algorithm NAME` | `md5`, `sha1`, `sha256` (default) or `blake2b` |
| `--json` | Machine-readable output |
| `--version` | Print the version |

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | No duplicates found |
| `1` | Duplicates found |
| `2` | Invalid arguments (e.g. folder does not exist) |

Requires Python 3.8 or newer.

## License

MIT. See [LICENSE](LICENSE).
