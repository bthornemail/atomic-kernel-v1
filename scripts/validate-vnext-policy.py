#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_KEYS = {
  "v",
  "authority",
  "vnext_status",
  "promotion_approved",
  "no_authority_change",
  "compat_window",
}


def validate(payload: dict) -> None:
  if set(payload.keys()) != REQUIRED_KEYS:
    raise ValueError("vnext policy keyset mismatch")
  if payload["v"] != "ak.vnext.policy.v0":
    raise ValueError("vnext policy v mismatch")
  if payload["authority"] != "advisory":
    raise ValueError("vnext policy authority mismatch")
  if payload["compat_window"] != "one_major_cycle":
    raise ValueError("compat_window mismatch")
  status = payload["vnext_status"]
  approved = payload["promotion_approved"]
  frozen = payload["no_authority_change"]

  # Only two constitutional policy states are valid.
  if status == "draft_extension_lane":
    if approved is not False:
      raise ValueError("draft lane requires promotion_approved=false")
    if frozen is not True:
      raise ValueError("draft lane requires no_authority_change=true")
    return

  if status == "promoted_normative_lane":
    if approved is not True:
      raise ValueError("promoted lane requires promotion_approved=true")
    if frozen is not False:
      raise ValueError("promoted lane requires no_authority_change=false")
    return

  raise ValueError("vnext policy status mismatch")


def main() -> int:
  parser = argparse.ArgumentParser(description="Validate vNext policy artifact.")
  parser.add_argument("--file", required=True)
  args = parser.parse_args()

  payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
  if not isinstance(payload, dict):
    raise ValueError("policy payload must be object")
  validate(payload)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
