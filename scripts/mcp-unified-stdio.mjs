#!/usr/bin/env node
import fs from "node:fs";
import { handleRequest } from "./mcp-unified-core.mjs";

const input = fs.readFileSync(0, "utf8");
const lines = input.split(/\r?\n/).filter((l) => l.trim().length > 0);
const outputs = [];
for (const line of lines) {
  try {
    const req = JSON.parse(line);
    const response = handleRequest(req);
    if (response) outputs.push(JSON.stringify(response));
  } catch {
    outputs.push(JSON.stringify(jsonRpcError(null, -32700, "parse error")));
  }
}

if (outputs.length > 0) {
  process.stdout.write(outputs.join("\n") + "\n");
}
