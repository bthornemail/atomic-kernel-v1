#!/usr/bin/env python3
"""Generate deterministic architecture summary SVG from analysis report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def box(x: int, y: int, w: int, h: int, title: str, subtitle: str) -> str:
  return (
    f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8" fill="#f8fafc" stroke="#1f2937" stroke-width="2"/>'
    f'<text x="{x + w//2}" y="{y + 28}" text-anchor="middle" font-family="monospace" font-size="16" fill="#111827">{title}</text>'
    f'<text x="{x + w//2}" y="{y + 52}" text-anchor="middle" font-family="monospace" font-size="13" fill="#374151">{subtitle}</text>'
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


def to_svg(report: dict) -> str:
  summary = report.get("summary", {})
  patterns = summary.get("patterns", {})
  domains = summary.get("domain_counts", {})
  bridge = int(patterns.get("BridgeLayer", 0))
  carrier = int(patterns.get("CarrierLayer", 0))
  boundary = int(patterns.get("BoundarySplit", 0))
  conf = int(patterns.get("ConformanceSurface", 0))
  proj = int(patterns.get("ProjectionOnlySurface", 0))
  core = int(domains.get("core", 0))

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
    '<text x="640" y="36" text-anchor="middle" font-family="monospace" font-size="22" fill="#111827">TETRAGRAMMATRON ARCHITECTURE</text>',
    box(80, 90, 240, 90, "Control Surface", f"BoundarySplit: {boundary}"),
    box(400, 90, 240, 90, "Bridge Layer", f"BridgeLayer: {bridge}"),
    box(720, 90, 240, 90, "Carrier Layer", f"CarrierLayer: {carrier}"),
    box(1040, 90, 180, 90, "Projection", f"ProjectionOnly: {proj}"),
    arrow(320, 135, 400, 135),
    arrow(640, 135, 720, 135),
    arrow(960, 135, 1040, 135),
    box(140, 270, 240, 90, "Core", f"domain core: {core}"),
    box(520, 270, 300, 90, "Conformance Surface", f"ConformanceSurface: {conf}"),
    arrow(520, 180, 520, 270),
    arrow(820, 180, 820, 270),
    box(240, 470, 800, 130, "Projection Surfaces", f"advisory-only (domain projection: {domains.get('projection', 0)})"),
    arrow(640, 360, 640, 470, "render/projection"),
    '<text x="640" y="700" text-anchor="middle" font-family="monospace" font-size="13" fill="#374151">'
    "Derived from deterministic ASG + pattern analysis report. Projection cannot upgrade authority."
    "</text>",
    "</svg>",
  ]
  return "".join(parts) + "\n"


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--report", required=True, help="analysis report json path")
  parser.add_argument("--output", required=True, help="output svg path")
  args = parser.parse_args()

  report = json.loads(Path(args.report).read_text(encoding="utf-8"))
  svg = to_svg(report)
  out = Path(args.output)
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(svg, encoding="utf-8")
  print(f"ok architecture diagram svg={out}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
