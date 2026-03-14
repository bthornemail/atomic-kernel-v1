#!/usr/bin/env python3
"""Generate deterministic protocol/state flow SVG from analysis artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def box(x: int, y: int, w: int, h: int, title: str, subtitle: str = "") -> str:
  title_svg = (
    f'<text x="{x + w//2}" y="{y + 28}" text-anchor="middle" font-family="monospace" font-size="16" fill="#111827">{title}</text>'
  )
  subtitle_svg = ""
  if subtitle:
    subtitle_svg = (
      f'<text x="{x + w//2}" y="{y + 52}" text-anchor="middle" font-family="monospace" font-size="13" fill="#374151">{subtitle}</text>'
    )
  return (
    f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8" fill="#f8fafc" stroke="#1f2937" stroke-width="2"/>'
    + title_svg
    + subtitle_svg
  )


def arrow(x1: int, y1: int, x2: int, y2: int, label: str = "") -> str:
  midx = (x1 + x2) // 2
  midy = (y1 + y2) // 2 - 6
  label_svg = ""
  if label:
    label_svg = (
      f'<text x="{midx}" y="{midy}" text-anchor="middle" font-family="monospace" font-size="12" fill="#374151">{label}</text>'
    )
  return (
    f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#111827" stroke-width="2" marker-end="url(#arrow)"/>'
    + label_svg
  )


def transition_count(flow: dict, src: str, dst: str) -> int:
  total = 0
  for t in flow.get("transitions", []):
    if t.get("from") == src and t.get("to") == dst:
      total += int(t.get("count", 0))
  return total


def render_svg(report: dict, flow: dict, pattern_file_count: int) -> str:
  summary = report.get("summary", {})
  patterns = summary.get("patterns", {})
  bridge = int(patterns.get("BridgeLayer", 0))
  carrier = int(patterns.get("CarrierLayer", 0))
  boundary = int(patterns.get("BoundarySplit", 0))
  conf = int(patterns.get("ConformanceSurface", 0))
  proj = int(patterns.get("ProjectionOnlySurface", 0))

  c_to_b = transition_count(flow, "control", "bridge")
  b_to_c = transition_count(flow, "bridge", "carrier")
  c_to_p = transition_count(flow, "carrier", "projection")
  to_conf = sum(transition_count(flow, s["id"], "conformance") for s in flow.get("states", []))

  w = 1280
  h = 760
  parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
    "<defs>",
    '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
    '<path d="M 0 0 L 10 5 L 0 10 z" fill="#111827"/>'
    "</marker>",
    "</defs>",
    '<rect x="0" y="0" width="1280" height="760" fill="#ffffff"/>',
    '<text x="640" y="36" text-anchor="middle" font-family="monospace" font-size="22" fill="#111827">TETRAGRAMMATRON PROTOCOL FLOW</text>',
    box(80, 90, 200, 90, "Control", f"BoundarySplit: {boundary}"),
    box(340, 90, 200, 90, "Bridge", f"BridgeLayer: {bridge}"),
    box(600, 90, 200, 90, "Carrier", f"CarrierLayer: {carrier}"),
    box(860, 90, 200, 90, "Projection", f"ProjectionOnly: {proj}"),
    arrow(280, 135, 340, 135, f"edges: {c_to_b}"),
    arrow(540, 135, 600, 135, f"edges: {b_to_c}"),
    arrow(800, 135, 860, 135, f"edges: {c_to_p}"),
    box(110, 300, 220, 90, "Boundary Split", f"instances: {boundary}"),
    box(430, 300, 220, 90, "Core Runtime", f"pattern files: {pattern_file_count}"),
    box(750, 300, 240, 90, "Conformance", f"Conformance: {conf} / flow: {to_conf}"),
    box(1040, 300, 170, 90, "Receipts", "deterministic"),
    arrow(180, 180, 180, 300, "control law"),
    arrow(440, 180, 540, 300, "invoke"),
    arrow(700, 180, 850, 300, "transport"),
    arrow(980, 180, 1125, 300, "verify"),
    '<text x="640" y="700" text-anchor="middle" font-family="monospace" font-size="13" fill="#374151">'
    "All transitions deterministic and verifiable. Projection surfaces cannot upgrade authority."
    "</text>",
    "</svg>",
  ]
  return "".join(parts) + "\n"


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--report", required=True, help="analysis report json path")
  parser.add_argument("--patterns", required=True, help="pattern output directory")
  parser.add_argument("--flow", required=True, help="protocol flow json path")
  parser.add_argument("--output", required=True, help="output svg path")
  args = parser.parse_args()

  report = json.loads(Path(args.report).read_text(encoding="utf-8"))
  flow = json.loads(Path(args.flow).read_text(encoding="utf-8"))
  patterns_dir = Path(args.patterns)
  pattern_file_count = len(sorted(patterns_dir.glob("*.json"))) if patterns_dir.is_dir() else 0

  svg = render_svg(report, flow, pattern_file_count)
  out = Path(args.output)
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(svg, encoding="utf-8")
  print(f"ok protocol diagram svg={out}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
