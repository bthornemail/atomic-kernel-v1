#!/usr/bin/env node
import http from "node:http";
import { URL } from "node:url";

const PORT = Number(process.env.PORT || 18811);
const SYMBOLS = {
  fs: { code: "0x1C", role: "file_separator" },
  gs: { code: "0x1D", role: "group_separator" },
  rs: { code: "0x1E", role: "record_separator" },
  us: { code: "0x1F", role: "unit_separator" },
  esc: { code: "0x1B", role: "escape" },
  null: { code: "0x00", role: "null" },
  codepoint: { code: "meta", role: "unicode_control_plane" },
  controlpoint: { code: "meta", role: "control_plane_registry" }
};

function send(res, code, body) {
  const data = JSON.stringify(body);
  res.writeHead(code, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "content-length": Buffer.byteLength(data)
  });
  res.end(data);
}

const server = http.createServer((req, res) => {
  const method = req.method || "GET";
  const host = String(req.headers.host || "").split(":")[0].toLowerCase();
  const symbol = host.split(".")[0];
  const url = new URL(req.url || "/", "http://localhost");

  if (method !== "GET" && method !== "HEAD") {
    return send(res, 405, {
      v: "ulp.symbol.response.v0",
      authority: "advisory",
      valid: false,
      reason: "method_not_allowed",
      allowed_methods: ["GET", "HEAD"]
    });
  }

  const meta = SYMBOLS[symbol];
  if (!meta) {
    return send(res, 404, {
      v: "ulp.symbol.response.v0",
      authority: "advisory",
      valid: false,
      reason: "unknown_symbol",
      host
    });
  }

  return send(res, 200, {
    v: "ulp.symbol.response.v0",
    authority: "advisory",
    valid: true,
    symbol,
    code: meta.code,
    role: meta.role,
    path: url.pathname,
    mutation_allowed: false,
    laws: ["CONTROL_PLANE_SPEC", "ESCAPE_ACCESS_LAW", "CHIRALITY_SELECTION_LAW_v0"]
  });
});

server.listen(PORT, "127.0.0.1", () => {
  process.stderr.write(`symbol-service listening on 127.0.0.1:${PORT}\n`);
});
