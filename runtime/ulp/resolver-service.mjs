#!/usr/bin/env node
import http from "node:http";
import { URL } from "node:url";

const PORT = Number(process.env.PORT || 18810);

function send(res, code, body) {
  const data = JSON.stringify(body);
  res.writeHead(code, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "content-length": Buffer.byteLength(data)
  });
  res.end(data);
}

function parseSubject(pathname) {
  const p = pathname.replace(/^\/+/, "");
  if (!p) return null;
  const [subject] = p.split("/");
  if (!/^[A-Za-z0-9._:-]+$/.test(subject)) return null;
  return subject;
}

const server = http.createServer((req, res) => {
  const method = req.method || "GET";
  const host = String(req.headers.host || "");
  const url = new URL(req.url || "/", "http://localhost");

  if (method !== "GET" && method !== "HEAD") {
    return send(res, 405, {
      v: "ulp.resolver.response.v0",
      authority: "advisory",
      valid: false,
      reason: "method_not_allowed",
      allowed_methods: ["GET", "HEAD"]
    });
  }

  const subject = parseSubject(url.pathname);
  if (!subject) {
    return send(res, 200, {
      v: "ulp.resolver.response.v0",
      authority: "advisory",
      valid: true,
      surface: "resolver",
      host,
      mode: host.startsWith("sid.") ? "sid" : host.startsWith("oid.") ? "oid" : "unknown",
      endpoints: {
        describe: "/<id>",
        lineage: "/<id>/lineage",
        verify: "/<id>/verify"
      },
      mutation_allowed: false
    });
  }

  const parts = url.pathname.replace(/^\/+/, "").split("/");
  const action = parts[1] || "describe";
  if (!["describe", "lineage", "verify"].includes(action)) {
    return send(res, 404, {
      v: "ulp.resolver.response.v0",
      authority: "advisory",
      valid: false,
      reason: "unknown_action",
      subject,
      action
    });
  }

  return send(res, 200, {
    v: "ulp.resolver.response.v0",
    authority: "advisory",
    valid: true,
    surface: "resolver",
    mode: host.startsWith("sid.") ? "sid" : host.startsWith("oid.") ? "oid" : "unknown",
    subject,
    action,
    canonical_ref: `artifact://${subject}`,
    replay_ref: `sha256:${subject}`,
    mutation_allowed: false
  });
});

server.listen(PORT, "127.0.0.1", () => {
  process.stderr.write(`resolver-service listening on 127.0.0.1:${PORT}\n`);
});
