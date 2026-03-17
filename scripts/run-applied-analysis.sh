#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

TARGET=""
NAME=""
OUT_ROOT="$ROOT/reports/analysis"
LANGUAGES="python,typescript,mjs"
INCLUDE_GLOBS=""
EXCLUDE_GLOBS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --name)
      NAME="${2:-}"
      shift 2
      ;;
    --out-root)
      OUT_ROOT="${2:-}"
      shift 2
      ;;
    --languages)
      LANGUAGES="${2:-}"
      shift 2
      ;;
    --include-globs)
      INCLUDE_GLOBS="${2:-}"
      shift 2
      ;;
    --exclude-globs)
      EXCLUDE_GLOBS="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

[[ -n "$TARGET" ]] || { echo "missing --target" >&2; exit 2; }
[[ -n "$NAME" ]] || { echo "missing --name" >&2; exit 2; }
[[ "$NAME" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "invalid --name: use [A-Za-z0-9._-]" >&2; exit 2; }
[[ -d "$TARGET" ]] || { echo "target must be a directory: $TARGET" >&2; exit 2; }

OUT_DIR="$OUT_ROOT/$NAME"
ASG_DIR="$OUT_DIR/asg"
PATTERN_DIR="$OUT_DIR/patterns"
mkdir -p "$ASG_DIR" "$PATTERN_DIR"

REPORT_JSON="$OUT_DIR/report.json"
REPORT_MD="$OUT_DIR/report.md"
RECEIPT_JSON="$OUT_DIR/receipt.json"

python3 "$ROOT/scripts/semantic-analyze.py" \
  --target "$TARGET" \
  --languages "$LANGUAGES" \
  --include-globs "$INCLUDE_GLOBS" \
  --exclude-globs "$EXCLUDE_GLOBS" \
  --out-json "$REPORT_JSON" \
  --out-md "$REPORT_MD" \
  >/dev/null

mapfile -t SOURCE_FILES < <(python3 - <<PY
from pathlib import Path
from runtime.atomic_kernel.repo_analysis import list_repo_sources, normalize_languages
target = Path(r"$TARGET").resolve()
langs = normalize_languages([x for x in r"$LANGUAGES".split(",") if x.strip()])
include_globs = [x.strip() for x in r"$INCLUDE_GLOBS".split(",") if x.strip()]
exclude_globs = [x.strip() for x in r"$EXCLUDE_GLOBS".split(",") if x.strip()]
for p in list_repo_sources(target, languages=langs, include_globs=include_globs or None, exclude_globs=exclude_globs or None):
  print(p.as_posix())
PY
)

for src in "${SOURCE_FILES[@]}"; do
  rel="$(python3 - <<PY
from pathlib import Path
print(Path(r"$src").resolve().relative_to(Path(r"$TARGET").resolve()).as_posix())
PY
)"
  stem="${rel//\//__}"
  ext="${src##*.}"
  asg_out="$ASG_DIR/${stem}.json"
  pat_out="$PATTERN_DIR/${stem}.json"

  if [[ "$ext" == "py" ]]; then
    python3 "$ROOT/scripts/ingest-python-asg.py" \
      --input "$src" \
      --source-path "$rel" \
      --namespace "analysis.python.${rel//\//.}" \
      --out "$asg_out" \
      >/dev/null
  elif [[ "$ext" == "ts" ]]; then
    python3 "$ROOT/scripts/ingest-typescript-asg.py" \
      --input "$src" \
      --source-path "$rel" \
      --namespace "analysis.typescript.${rel//\//.}" \
      --out "$asg_out" \
      >/dev/null
  elif [[ "$ext" == "mjs" ]]; then
    python3 "$ROOT/scripts/ingest-mjs-asg.py" \
      --input "$src" \
      --source-path "$rel" \
      --namespace "analysis.mjs.${rel//\//.}" \
      --out "$asg_out" \
      >/dev/null
  else
    echo "unsupported source extension: $src" >&2
    exit 1
  fi

  python3 "$ROOT/scripts/extract-patterns.py" --asg "$asg_out" --out "$pat_out" >/dev/null
done

python3 - <<PY > "$RECEIPT_JSON"
import hashlib
import json
from pathlib import Path

report = json.loads(Path(r"$REPORT_JSON").read_text(encoding="utf-8"))
asg_files = sorted(Path(r"$ASG_DIR").glob("*.json"))
pattern_files = sorted(Path(r"$PATTERN_DIR").glob("*.json"))

def sha(path: Path) -> str:
  return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()

receipt = {
  "v": "analysis-receipt.v0",
  "authority": "advisory",
  "name": r"$NAME",
  "target": str(Path(r"$TARGET").resolve()),
  "languages": [x for x in r"$LANGUAGES".split(",") if x.strip()],
  "report_json_sha": sha(Path(r"$REPORT_JSON")),
  "report_md_sha": sha(Path(r"$REPORT_MD")),
  "asg_count": len(asg_files),
  "pattern_count": len(report.get("instances", [])),
  "inputs_digest": report["inputs_digest"],
  "evidence_digest": report["evidence_digest"],
  "outputs_digest": report["outputs_digest"],
  "asg_digest": "sha256:" + hashlib.sha256(
    json.dumps([sha(p) for p in asg_files], sort_keys=True, separators=(",", ":")).encode("utf-8")
  ).hexdigest(),
  "patterns_digest": "sha256:" + hashlib.sha256(
    json.dumps([sha(p) for p in pattern_files], sort_keys=True, separators=(",", ":")).encode("utf-8")
  ).hexdigest(),
}
print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
PY

echo "ok applied analysis out=$OUT_DIR"
