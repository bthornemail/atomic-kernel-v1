# Scan Verify Render Demo
Status: Advisory
Authority: Projection
Depends on: `docs/badges/payloads/*`, `releases/0.1.0/ARTIFACTS.sha256`, `propagation/aztec/schemas/*.json`

Purpose: interactive demo for the projection flow: input payload -> verify contract -> render XML projection.

<div id="ak-demo" style="display:grid; gap:1rem;">
  <div style="display:flex; gap:.5rem; flex-wrap:wrap;">
    <button id="load-readme">Load README badge</button>
    <button id="load-p1">Load P1 badge</button>
    <button id="load-experience">Load experience manifest</button>
    <button id="verify">Verify and Render</button>
  </div>

  <label for="payload"><strong>Payload JSON</strong></label>
  <textarea id="payload" rows="18" style="width:100%; font-family:monospace;"></textarea>

  <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1rem;">
    <div>
      <h3 style="margin:.25rem 0;">Verification</h3>
      <pre id="verify-out" style="padding:.75rem; border:1px solid #ccc; min-height:8rem; white-space:pre-wrap;"></pre>
    </div>
    <div>
      <h3 style="margin:.25rem 0;">Canonical JSON</h3>
      <pre id="json-out" style="padding:.75rem; border:1px solid #ccc; min-height:8rem; white-space:pre-wrap;"></pre>
    </div>
    <div>
      <h3 style="margin:.25rem 0;">XML Projection</h3>
      <pre id="xml-out" style="padding:.75rem; border:1px solid #ccc; min-height:8rem; white-space:pre-wrap;"></pre>
    </div>
  </div>
</div>

<script>
(() => {
  const payloadEl = document.getElementById('payload');
  const verifyOut = document.getElementById('verify-out');
  const jsonOut = document.getElementById('json-out');
  const xmlOut = document.getElementById('xml-out');

  const docBadgeKeys = [
    'schema','authority','doc_id','doc_path','release','version',
    'hash_alg','doc_hash','artifacts_ref','verify_mode'
  ];

  const experienceKeys = [
    'schema','authority','manifest_id','release','version',
    'kernel','entry_points','render','policy'
  ];

  function base(rel) {
    return new URL(rel, window.location.href).toString();
  }

  async function loadJson(relPath) {
    const res = await fetch(base(relPath));
    if (!res.ok) throw new Error(`fetch failed: ${relPath}`);
    return await res.json();
  }

  async function loadText(relPath) {
    const res = await fetch(base(relPath));
    if (!res.ok) throw new Error(`fetch failed: ${relPath}`);
    return await res.text();
  }

  function strictKeys(obj, expected, label) {
    const got = Object.keys(obj).sort();
    const want = [...expected].sort();
    if (JSON.stringify(got) !== JSON.stringify(want)) {
      throw new Error(`${label} key mismatch: got=[${got.join(',')}], want=[${want.join(',')}]`);
    }
  }

  function parseArtifacts(text) {
    const map = new Map();
    for (const raw of text.split('\n')) {
      const line = raw.trim();
      if (!line || line.startsWith('#')) continue;
      const parts = line.split(/\s+/);
      if (parts.length !== 2) throw new Error('invalid ARTIFACTS.sha256 line');
      map.set(parts[1], parts[0]);
    }
    return map;
  }

  function escapeXml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }

  function renderDocBadgeXml(p) {
    return `<ak:doc-badge schema="${escapeXml(p.schema)}" authority="${escapeXml(p.authority)}" release="${escapeXml(p.release)}">\n` +
      `  <ak:doc id="${escapeXml(p.doc_id)}" path="${escapeXml(p.doc_path)}" hash="${escapeXml(p.doc_hash)}"/>\n` +
      `  <ak:verify mode="${escapeXml(p.verify_mode)}" artifacts_ref="${escapeXml(p.artifacts_ref)}"/>\n` +
      `</ak:doc-badge>`;
  }

  function renderExperienceXml(p) {
    const entries = Object.entries(p.entry_points)
      .map(([k,v]) => `  <ak:entry name="${escapeXml(k)}" path="${escapeXml(v)}"/>`)
      .join('\n');
    return `<ak:experience schema="${escapeXml(p.schema)}" authority="${escapeXml(p.authority)}" release="${escapeXml(p.release)}">\n` +
      `  <ak:kernel package="${escapeXml(p.kernel.package)}" api="${escapeXml(p.kernel.public_api)}" artifacts="${escapeXml(p.kernel.release_artifacts)}"/>\n` +
      `${entries}\n` +
      `  <ak:policy verify_before_render="${p.policy.verify_before_render}" projection_cannot_upgrade_authority="${p.policy.projection_cannot_upgrade_authority}"/>\n` +
      `</ak:experience>`;
  }

  async function verifyDocBadge(p) {
    strictKeys(p, docBadgeKeys, 'doc badge');
    if (p.schema !== 'atomic-kernel.doc.badge/1') throw new Error('invalid schema');
    if (p.authority !== 'projection') throw new Error('authority must be projection');
    if (p.version !== 1) throw new Error('version must be 1');
    if (p.hash_alg !== 'sha256') throw new Error('hash_alg must be sha256');
    if (p.verify_mode !== 'hash-match') throw new Error('verify_mode must be hash-match');

    const expectedRef = `releases/${p.release}/ARTIFACTS.sha256`;
    if (p.artifacts_ref !== expectedRef) throw new Error('artifacts_ref mismatch');

    const artText = await loadText(`../../${p.artifacts_ref}`);
    const artifacts = parseArtifacts(artText);
    if (!artifacts.has(p.doc_path)) throw new Error('doc_path missing in artifacts index');
    const expectedHash = `sha256:${artifacts.get(p.doc_path)}`;
    if (p.doc_hash !== expectedHash) throw new Error('doc_hash mismatch vs artifacts index');

    return { ok: true, summary: 'doc badge verified against release artifacts' };
  }

  async function verifyExperience(p) {
    strictKeys(p, experienceKeys, 'experience');
    if (p.schema !== 'atomic-kernel.experience.manifest/1') throw new Error('invalid schema');
    if (p.authority !== 'projection') throw new Error('authority must be projection');
    if (p.version !== 1) throw new Error('version must be 1');
    if (!p.kernel || p.kernel.package !== 'atomic-kernel') throw new Error('kernel.package mismatch');
    if (p.kernel.public_api !== 'atomic_kernel.*') throw new Error('kernel.public_api mismatch');

    const expectedRef = `releases/${p.release}/ARTIFACTS.sha256`;
    if (p.kernel.release_artifacts !== expectedRef) throw new Error('release_artifacts mismatch');

    await loadText(`../../${p.kernel.release_artifacts}`);

    for (const [name, path] of Object.entries(p.entry_points)) {
      if (typeof path !== 'string' || !path.length) throw new Error(`entry point invalid: ${name}`);
      await loadText(`../../${path}`);
    }

    const expectedRender = { xml_projection:'supported', clipboard_profile:'supported', aztec_profile:'supported' };
    if (JSON.stringify(p.render) !== JSON.stringify(expectedRender)) throw new Error('render block mismatch');

    const expectedPolicy = {
      verify_before_render: true,
      projection_cannot_upgrade_authority: true,
      fork_scope: ['extension','projection']
    };
    if (JSON.stringify(p.policy) !== JSON.stringify(expectedPolicy)) throw new Error('policy block mismatch');

    return { ok: true, summary: 'experience manifest verified (schema, authority, refs, policy)' };
  }

  async function verifyAndRender() {
    verifyOut.textContent = 'running verification...';
    jsonOut.textContent = '';
    xmlOut.textContent = '';

    try {
      const payload = JSON.parse(payloadEl.value);
      let result;
      let xml;

      if (payload.schema === 'atomic-kernel.doc.badge/1') {
        result = await verifyDocBadge(payload);
        xml = renderDocBadgeXml(payload);
      } else if (payload.schema === 'atomic-kernel.experience.manifest/1') {
        result = await verifyExperience(payload);
        xml = renderExperienceXml(payload);
      } else {
        throw new Error('unsupported schema');
      }

      verifyOut.textContent = `PASS\n${result.summary}\n\nRule enforced: verify before render.`;
      jsonOut.textContent = JSON.stringify(payload, null, 2);
      xmlOut.textContent = xml;
    } catch (err) {
      verifyOut.textContent = `FAIL\n${err.message}`;
      jsonOut.textContent = '';
      xmlOut.textContent = '';
    }
  }

  async function loadSample(rel) {
    try {
      const payload = await loadJson(rel);
      payloadEl.value = JSON.stringify(payload, null, 2);
      verifyOut.textContent = 'sample loaded';
      jsonOut.textContent = '';
      xmlOut.textContent = '';
    } catch (err) {
      verifyOut.textContent = `FAIL\n${err.message}`;
    }
  }

  document.getElementById('load-readme').addEventListener('click', () => loadSample('../../badges/payloads/doc-badges/README.json'));
  document.getElementById('load-p1').addEventListener('click', () => loadSample('../../badges/payloads/doc-badges/P1-Kernel.json'));
  document.getElementById('load-experience').addEventListener('click', () => loadSample('../../badges/payloads/experience-manifest.json'));
  document.getElementById('verify').addEventListener('click', verifyAndRender);

  loadSample('../../badges/payloads/doc-badges/README.json');
})();
</script>

## Boundary
This demo is projection-layer UX. Canonical authority remains in verified artifacts and release contracts.
