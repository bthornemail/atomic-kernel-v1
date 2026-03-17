#!/usr/bin/env node
import { parse } from "acorn";

function getArg(name) {
  const idx = process.argv.indexOf(name);
  if (idx === -1 || idx + 1 >= process.argv.length) return "";
  return process.argv[idx + 1];
}

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
  });
}

function memberName(node) {
  if (!node) return "expr";
  if (node.type === "Identifier") return node.name;
  if (node.type === "ThisExpression") return "this";
  if (node.type === "Super") return "super";
  if (node.type === "MemberExpression") {
    const obj = memberName(node.object);
    const prop =
      node.property && node.property.type === "Identifier"
        ? node.property.name
        : "expr";
    return `${obj}.${prop}`;
  }
  return "expr";
}

function pushSorted(list, item) {
  list.push(item);
}

function walk(node, visit) {
  if (!node || typeof node !== "object") return;
  visit(node);
  for (const key of Object.keys(node)) {
    if (key === "loc" || key === "range") continue;
    const val = node[key];
    if (Array.isArray(val)) {
      for (const it of val) walk(it, visit);
    } else if (val && typeof val === "object" && typeof val.type === "string") {
      walk(val, visit);
    }
  }
}

async function main() {
  const sourcePath = getArg("--source-path") || "<stdin>.mjs";
  const source = await readStdin();

  let ast;
  try {
    ast = parse(source, {
      ecmaVersion: "latest",
      sourceType: "module",
      locations: true,
      ranges: true,
      allowHashBang: true,
    });
  } catch (err) {
    const msg = err && err.message ? String(err.message) : "parse failure";
    console.error(msg);
    process.exit(2);
  }

  const facts = {
    imports: [],
    exports: [],
    classes: [],
    methods: [],
    functions: [],
    variables: [],
    object_literals: [],
    calls: [],
  };

  for (const stmt of ast.body || []) {
    if (stmt.type === "ImportDeclaration") {
      const mod = stmt.source && typeof stmt.source.value === "string" ? stmt.source.value : "";
      if (mod) {
        pushSorted(facts.imports, {
          module: mod,
          start: stmt.start,
          end: stmt.end,
        });
      }
      continue;
    }
    if (stmt.type === "ExportNamedDeclaration") {
      if (stmt.declaration && stmt.declaration.type === "ClassDeclaration" && stmt.declaration.id) {
        pushSorted(facts.exports, {
          name: stmt.declaration.id.name,
          kind: "class",
          start: stmt.start,
          end: stmt.end,
        });
      } else if (stmt.declaration && stmt.declaration.type === "FunctionDeclaration" && stmt.declaration.id) {
        pushSorted(facts.exports, {
          name: stmt.declaration.id.name,
          kind: "function",
          start: stmt.start,
          end: stmt.end,
        });
      } else if (stmt.specifiers && stmt.specifiers.length) {
        for (const spec of stmt.specifiers) {
          if (spec.exported && spec.exported.type === "Identifier") {
            pushSorted(facts.exports, {
              name: spec.exported.name,
              kind: "named",
              start: spec.start ?? stmt.start,
              end: spec.end ?? stmt.end,
            });
          }
        }
      }
      continue;
    }
    if (stmt.type === "ExportDefaultDeclaration") {
      let name = "default";
      if (stmt.declaration && stmt.declaration.id && stmt.declaration.id.type === "Identifier") {
        name = stmt.declaration.id.name;
      }
      pushSorted(facts.exports, {
        name,
        kind: "default",
        start: stmt.start,
        end: stmt.end,
      });
      continue;
    }
  }

  walk(ast, (node) => {
    if (node.type === "ClassDeclaration" && node.id && node.id.type === "Identifier") {
      pushSorted(facts.classes, {
        name: node.id.name,
        extends: node.superClass ? memberName(node.superClass) : "",
        start: node.start,
        end: node.end,
      });
      for (const el of node.body?.body || []) {
        if (el.type === "MethodDefinition" && el.key && el.key.type === "Identifier") {
          pushSorted(facts.methods, {
            owner: node.id.name,
            name: el.key.name,
            kind: el.kind || "method",
            start: el.start,
            end: el.end,
          });
        }
      }
      return;
    }

    if (node.type === "FunctionDeclaration" && node.id && node.id.type === "Identifier") {
      pushSorted(facts.functions, {
        name: node.id.name,
        start: node.start,
        end: node.end,
      });
      return;
    }

    if (node.type === "VariableDeclaration") {
      for (const decl of node.declarations || []) {
        if (decl.id && decl.id.type === "Identifier") {
          pushSorted(facts.variables, {
            name: decl.id.name,
            kind: node.kind || "let",
            start: decl.start ?? node.start,
            end: decl.end ?? node.end,
          });
        }
      }
      return;
    }

    if (node.type === "ObjectExpression") {
      pushSorted(facts.object_literals, {
        start: node.start,
        end: node.end,
      });
      return;
    }

    if (node.type === "CallExpression") {
      pushSorted(facts.calls, {
        callee: memberName(node.callee),
        start: node.start,
        end: node.end,
      });
      return;
    }
  });

  for (const key of Object.keys(facts)) {
    facts[key].sort((a, b) => (a.start - b.start) || (a.end - b.end));
  }

  const out = {
    source_path: sourcePath,
    facts,
  };
  process.stdout.write(JSON.stringify(out));
}

main().catch((err) => {
  const msg = err && err.message ? String(err.message) : "parser failure";
  console.error(msg);
  process.exit(1);
});
