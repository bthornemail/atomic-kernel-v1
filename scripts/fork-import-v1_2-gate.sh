#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMPORT_ROOT="$ROOT/docs/imports/folder1-v1_2"
MANIFEST="$IMPORT_ROOT/IMPORT_MANIFEST.json"
INDEX_DOC="$ROOT/docs/FORK_IMPORT_INDEX_v1_2.md"
TRACE_DOC="$ROOT/docs/TRACEABILITY_DIFF_v1_2.md"
PROMOTION_DOC="$ROOT/docs/PROMOTION_MATRIX_v1_2.md"
LIFECYCLE_REGISTRY="$ROOT/docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json"
COQ_STATUS="$IMPORT_ROOT/FORMAL_TOOLCHAIN_STATUS.md"

[[ -f "$MANIFEST" ]] || { echo "missing manifest: $MANIFEST" >&2; exit 1; }
[[ -f "$INDEX_DOC" ]] || { echo "missing index doc: $INDEX_DOC" >&2; exit 1; }
[[ -f "$TRACE_DOC" ]] || { echo "missing traceability doc: $TRACE_DOC" >&2; exit 1; }
[[ -f "$PROMOTION_DOC" ]] || { echo "missing promotion doc: $PROMOTION_DOC" >&2; exit 1; }
[[ -f "$LIFECYCLE_REGISTRY" ]] || { echo "missing lifecycle registry: $LIFECYCLE_REGISTRY" >&2; exit 1; }

bash "$ROOT/scripts/artifact-lifecycle-v0-gate.sh" >/dev/null

python3 - "$ROOT" "$MANIFEST" "$INDEX_DOC" "$TRACE_DOC" "$PROMOTION_DOC" "$LIFECYCLE_REGISTRY" <<'PY'
import hashlib, json, pathlib, re, sys
root = pathlib.Path(sys.argv[1])
manifest_path = pathlib.Path(sys.argv[2])
index_doc = pathlib.Path(sys.argv[3])
trace_doc = pathlib.Path(sys.argv[4])
promo_doc = pathlib.Path(sys.argv[5])
lifecycle_path = pathlib.Path(sys.argv[6])

m = json.loads(manifest_path.read_text(encoding='utf-8'))
if m.get('count') != len(m.get('entries', [])):
    raise SystemExit('manifest count mismatch')

# 1) Import integrity
for entry in m['entries']:
    rel = entry['imported_path']
    fp = root / rel
    if not fp.exists():
        raise SystemExit(f'missing imported file: {rel}')
    digest = 'sha256:' + hashlib.sha256(fp.read_bytes()).hexdigest()
    if digest != entry['sha256']:
        raise SystemExit(f'digest drift: {rel}')

# 2) Reference integrity checks on wrapper docs
for doc in (index_doc, trace_doc, promo_doc):
    txt = doc.read_text(encoding='utf-8')
    # markdown links
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', txt):
        if '://' in target or target.startswith('#'):
            continue
        p = (doc.parent / target).resolve()
        if not p.exists():
            raise SystemExit(f'broken markdown link in {doc.name}: {target}')
    # backtick local paths: only enforce existence for concrete current-repo paths,
    # not future intended promotion targets.
    for target in re.findall(r'`((?:docs|kernel|dev-docs|atomic_kernel)/[^`]+)`', txt):
        enforce = (
            target.startswith('docs/imports/folder1-v1_2/')
            or target.startswith('docs/FORK_IMPORT_INDEX_v1_2.md')
            or target.startswith('docs/TRACEABILITY_DIFF_v1_2.md')
            or target.startswith('docs/PROMOTION_MATRIX_v1_2.md')
            or target.startswith('kernel/coq/')
            or target.startswith('dev-docs/prototype/')
            or target.startswith('atomic_kernel/')
        )
        if target.startswith('kernel/coq/') and 'ImportedV1_2' in target:
            enforce = False
        if enforce:
            p = (root / target).resolve()
            if not p.exists():
                raise SystemExit(f'broken path reference in {doc.name}: {target}')

# 3) Authority-boundary check: imported docs must not appear in main indexes
main_indexes = [root / 'docs' / 'index.md', root / 'docs' / 'INDEX.md']
import_filenames = [pathlib.Path(e['file']).name for e in m['entries']]
lifecycle = json.loads(lifecycle_path.read_text(encoding='utf-8'))
allowed_index_names = set()
for entry in lifecycle.get('entries', []):
    if entry.get('lifecycle_state') == 'canonical':
        allowed_index_names.add(pathlib.Path(entry.get('file', '')).name)
for idx in main_indexes:
    txt = idx.read_text(encoding='utf-8')
    for name in import_filenames:
        if name in allowed_index_names:
            continue
        if name in txt:
            raise SystemExit(f'authority-boundary breach: {name} listed in {idx.name}')

# 4a) 112 proof matrix dependencies must resolve or be deferred in trace diff
proof = root / 'docs' / 'imports' / 'folder1-v1_2' / '112_PROOFS_MATRIX.md'
ptxt = proof.read_text(encoding='utf-8')
deps_line = None
for line in ptxt.splitlines():
    if line.strip().startswith('**Depends on:**'):
        deps_line = line
        break
if deps_line:
    deps = re.findall(r'`([^`]+\.md)`', deps_line)
    trace_txt = trace_doc.read_text(encoding='utf-8')
    for d in deps:
        if (proof.parent / d).exists():
            continue
        if f'`{d}`' in trace_txt and '`defer`' in trace_txt:
            continue
        raise SystemExit(f'112 matrix dependency unresolved: {d}')

print('ok fork import integrity/reference/authority/proof deps')
PY

# 4b) Coq parse/compile sanity (or explicit toolchain missing receipt)
if command -v coqc >/dev/null 2>&1; then
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' EXIT
  cp "$IMPORT_ROOT/AtomicKernelCoq.v" "$tmpdir/AtomicKernelCoq.v"
  if coqc -q "$tmpdir/AtomicKernelCoq.v" >/dev/null 2>&1; then
    cat > "$COQ_STATUS" <<STAT
# Formal Toolchain Status (Fork Import v1.2)

Status: PASS
Tool: coqc
File: docs/imports/folder1-v1_2/AtomicKernelCoq.v
Result: parse/compile succeeded.
STAT
  else
    echo "coqc present but compilation failed for imported AtomicKernelCoq.v" >&2
    exit 1
  fi
else
  cat > "$COQ_STATUS" <<STAT
# Formal Toolchain Status (Fork Import v1.2)

Status: TOOLCHAIN_MISSING
Tool: coqc
File: docs/imports/folder1-v1_2/AtomicKernelCoq.v
Result: coqc not installed in current environment; formal check deferred.
STAT
fi

echo "ok fork import v1.2 gate"
