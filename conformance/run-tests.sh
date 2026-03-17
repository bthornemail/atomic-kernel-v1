#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
cd "$ROOT"
python3 -m unittest \
  atomic_kernel.tests.test_public_api \
  runtime.atomic_kernel.tests.test_asg \
  runtime.atomic_kernel.tests.test_pattern_extract \
  runtime.atomic_kernel.tests.test_repo_analysis \
  runtime.atomic_kernel.tests.test_workspace_ingest \
  runtime.atomic_kernel.tests.test_living_xml \
  runtime.atomic_kernel.tests.test_living_xml_fuzz \
  runtime.atomic_kernel.tests.test_identity_occurrence \
  runtime.atomic_kernel.tests.test_semantic_identity \
  runtime.atomic_kernel.tests.test_seed_algebra \
  runtime.atomic_kernel.tests.test_seed_companion \
  runtime.atomic_kernel.tests.test_lane16 \
  runtime.atomic_kernel.tests.test_vnext_lane
