#!/usr/bin/env node
import http from "node:http";
import { handleRequest } from "./mcp-unified-core.mjs";

const host = process.env.HOST || "127.0.0.1";
const port = Number(process.env.PORT || 18787);

const server = http.createServer((req, res) => {
  if (req.method !== "POST" || req.url !== "/mcp") {
    res.statusCode = 404;
    res.setHeader("content-type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ error: "not_found" }));
    return;
  }

  let body = "";
  req.setEncoding("utf8");
  req.on("data", (chunk) => {
    body += chunk;
  });
  req.on("end", () => {
    let parsed;
    try {
      parsed = JSON.parse(body);
    } catch {
      res.statusCode = 400;
      res.setHeader("content-type", "application/json; charset=utf-8");
      res.end(JSON.stringify({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "parse error" } }));
      return;
    }

    const response = handleRequest(parsed);
    if (response == null) {
      res.statusCode = 204;
      res.end();
      return;
    }

    res.statusCode = 200;
    res.setHeader("content-type", "application/json; charset=utf-8");
    res.end(JSON.stringify(response));
  });
});

server.listen(port, host, () => {
  console.error(`mcp unified server listening on http://${host}:${port}/mcp`);
});
