"use strict";

// ---- state -----------------------------------------------------------------
let STATE = null;
let CURRENT_ENG = null;
let CURRENT_TAB = "waves";
let CURRENT_DOC = null;

const TABS = [
  ["waves", "Wave board"],
  ["metrics", "Metrics timeline"],
  ["learning", "Learning by version"],
  ["integrity", "Integrity log"],
  ["inbox", "Decision inbox"],
  ["rag", "RAG"],
  ["raid", "RAID"],
  ["docs", "Documents"],
  ["creds", "Credentials"],
];

const KNOWN_SERVICES = [
  ["anthropic", "ANTHROPIC_API_KEY", "Run Claude agents"],
  ["vercel", "VERCEL_TOKEN", "Deploy"],
  ["neon", "NEON_API_KEY", "Database"],
  ["clerk", "CLERK_SECRET_KEY", "Auth"],
  ["resend", "RESEND_API_KEY", "Email"],
  ["booking_provider", "BOOKING_PROVIDER_API_KEY", "Bookings"],
  ["payment_provider", "PAYMENT_PROVIDER_API_KEY", "Payments"],
];

// ---- helpers ---------------------------------------------------------------
const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, html) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html != null) n.innerHTML = html;
  return n;
};
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2600);
}

function curEng() {
  return STATE.engagements.find((e) => e.id === CURRENT_ENG) || STATE.engagements[0];
}

function fmtDur(ms) {
  if (ms == null) return "—";
  const m = Math.round(ms / 60000);
  if (m < 60) return m + "m";
  return (m / 60).toFixed(1) + "h";
}
function fmtNum(n) { return n == null ? "—" : Number(n).toLocaleString(); }

function ageHours(iso) {
  if (!iso) return null;
  const then = new Date(iso).getTime();
  if (isNaN(then)) return null;
  return (Date.now() - then) / 3600000;
}
function fmtAge(h) {
  if (h == null) return "—";
  if (h < 1) return Math.round(h * 60) + "m";
  if (h < 48) return h.toFixed(0) + "h";
  return (h / 24).toFixed(1) + "d";
}

// ---- boot ------------------------------------------------------------------
async function boot() {
  try {
    const r = await fetch("/api/state");
    STATE = await r.json();
  } catch (e) {
    $("#view").innerHTML = '<div class="empty">Could not load /api/state — is server.py running?</div>';
    return;
  }
  $("#sampleTag").textContent = STATE.using_sample ? "SAMPLE DATA" : "LIVE STATE_DIR";
  const sel = $("#engSel");
  sel.innerHTML = "";
  STATE.engagements.forEach((e) => {
    const o = el("option");
    o.value = e.id; o.textContent = e.id;
    sel.appendChild(o);
  });
  // default to the demo engagement (fall back to any RED, then the first listed)
  const preferred = STATE.engagements.find((e) => e.id === "riverside-bookings")
    || STATE.engagements.find((e) => e.rag === "RED")
    || STATE.engagements[0];
  CURRENT_ENG = preferred ? preferred.id : null;
  if (CURRENT_ENG) sel.value = CURRENT_ENG;
  sel.onchange = () => { CURRENT_ENG = sel.value; render(); };

  const nav = $("#tabs");
  nav.innerHTML = "";
  TABS.forEach(([id, label]) => {
    const b = el("button", id === CURRENT_TAB ? "active" : "", esc(label));
    b.onclick = () => { CURRENT_TAB = id; document.querySelectorAll("nav.tabs button").forEach((x) => x.classList.remove("active")); b.classList.add("active"); render(); };
    nav.appendChild(b);
  });
  render();
}

function render() {
  const v = $("#view");
  v.innerHTML = "";
  if (!STATE.engagements.length && CURRENT_TAB !== "creds") {
    v.innerHTML = '<div class="empty">No engagements found in state directory.</div>';
    return;
  }
  ({
    waves: renderWaves, metrics: renderMetrics, learning: renderLearning,
    integrity: renderIntegrity, inbox: renderInbox, rag: renderRag,
    raid: renderRaid, docs: renderDocs, creds: renderCreds,
  }[CURRENT_TAB] || renderWaves)(v);
}

function title(v, t, desc) {
  v.appendChild(el("h2", "view-title", esc(t)));
  v.appendChild(el("p", "view-desc", desc));
}

// ---- view 1: wave board ----------------------------------------------------
function renderWaves(v) {
  title(v, "Wave board — " + esc(CURRENT_ENG),
    "Per-wave state machine from <code>wave-status.yaml</code>. DEAD / GATE_BLOCKED / TIMED_OUT flagged red.");
  const waves = ((curEng().wave_status || {}).waves) || {};
  const keys = Object.keys(waves);
  if (!keys.length) { v.appendChild(el("div", "empty", "No wave-status.yaml for this engagement yet.")); return; }
  const grid = el("div", "wave-grid");
  keys.forEach((k) => {
    const w = waves[k] || {};
    const st = w.state || "PENDING";
    const card = el("div", "wave s-" + st);
    card.appendChild(el("h3", null, esc(k)));
    card.appendChild(el("div", null, `<span class="pill p-${st}"><span class="dot" style="background:currentColor"></span>${esc(st)}</span>`));
    let meta = "";
    if (w.agent) meta += `agent: ${esc(w.agent)}`;
    if (w.agent_version) meta += ` <code>${esc(w.agent_version)}</code>`;
    if (w.blocked_by) meta += `<br>blocked by: ${esc(w.blocked_by)}`;
    if (w.port) meta += `<br>port: ${esc(w.port)}`;
    if (meta) card.appendChild(el("div", "meta", meta));
    if (w.detail) card.appendChild(el("div", "detail", esc(w.detail)));
    grid.appendChild(card);
  });
  v.appendChild(grid);
}

// ---- view 2: metrics timeline ----------------------------------------------
function renderMetrics(v) {
  title(v, "Agent metrics timeline — " + esc(CURRENT_ENG),
    "One row per agent run from <code>metrics-ledger.jsonl</code>. Absent fields show &mdash; (never fabricated).");
  const rows = curEng().metrics || [];
  if (!rows.length) { v.appendChild(el("div", "empty", "No metrics-ledger.jsonl entries yet.")); return; }
  const wrap = el("div", "card table-scroll");
  const t = el("table");
  t.innerHTML = `<thead><tr>
    <th>ts</th><th>wave</th><th>agent</th><th>ver</th><th>termination</th>
    <th class="num">tokens</th><th class="num">dur</th><th class="num">tools</th>
    <th class="num">gates ✓/✗</th><th class="num">rework</th></tr></thead>`;
  const tb = el("tbody");
  rows.slice().sort((a, b) => String(a.ts).localeCompare(String(b.ts))).forEach((m) => {
    const tr = el("tr");
    const cause = m.termination_cause || "—";
    const causeCls = (cause === "DIED" || cause === "GATE_BLOCKED" || cause === "TIMED_OUT") ? "resolution-open" : "";
    tr.innerHTML = `
      <td>${esc((m.ts || "").replace("T", " ").replace("Z", ""))}</td>
      <td>${esc(m.wave)}</td>
      <td>${esc(m.agent_id)}</td>
      <td><code>${esc(m.agent_version)}</code></td>
      <td class="${causeCls}">${esc(cause)}</td>
      <td class="num">${fmtNum(m.tokens)}</td>
      <td class="num">${fmtDur(m.duration_ms)}</td>
      <td class="num">${fmtNum(m.tool_uses)}</td>
      <td class="num">${m.gates_passed == null && m.gates_failed == null ? "—" : (m.gates_passed || 0) + "/" + (m.gates_failed || 0)}</td>
      <td class="num">${fmtNum(m.rework_count)}</td>`;
    tb.appendChild(tr);
  });
  t.appendChild(tb);
  wrap.appendChild(t);
  v.appendChild(wrap);
}

// ---- view 3: learning by version -------------------------------------------
function renderLearning(v) {
  title(v, "Learning & efficiency by agent VERSION",
    "Metrics grouped by <code>agent_version</code> across ALL engagements, so improvement is attributable to LEARN&rarr;bump cycles — not assumed. Quality signals (rework, gate-fail rate) over raw tokens.");
  // gather all metrics across engagements
  const all = [];
  STATE.engagements.forEach((e) => (e.metrics || []).forEach((m) => all.push(m)));
  // group by agent_id -> version
  const byAgent = {};
  all.forEach((m) => {
    if (!m.agent_id) return;
    byAgent[m.agent_id] = byAgent[m.agent_id] || {};
    const g = (byAgent[m.agent_id][m.agent_version] = byAgent[m.agent_id][m.agent_version] || { runs: 0, rework: 0, gpass: 0, gfail: 0, tokens: 0, hasRework: 0 });
    g.runs++;
    if (m.rework_count != null) { g.rework += m.rework_count; g.hasRework++; }
    if (m.gates_passed != null) g.gpass += m.gates_passed;
    if (m.gates_failed != null) g.gfail += m.gates_failed;
    if (m.tokens != null) g.tokens += m.tokens;
  });

  Object.keys(byAgent).sort().forEach((agent) => {
    const versions = Object.keys(byAgent[agent]).sort();
    const card = el("div", "card");
    card.appendChild(el("h3", null, esc(agent)));
    if (versions.length < 2) {
      card.appendChild(el("div", "note", "Only one version observed (" + versions.length + " version, " +
        byAgent[agent][versions[0]].runs + " run" + (byAgent[agent][versions[0]].runs > 1 ? "s" : "") +
        "). A trend needs &ge;2 versions — data is sparse; showing what exists, not extrapolating."));
    }
    // avg rework per run per version (lower = better)
    const maxRework = Math.max(0.001, ...versions.map((ver) => {
      const g = byAgent[agent][ver]; return g.hasRework ? g.rework / g.hasRework : 0;
    }));
    card.appendChild(el("div", "bar-lbl", "Avg rework loops per run (lower is better):"));
    versions.forEach((ver) => {
      const g = byAgent[agent][ver];
      const avg = g.hasRework ? g.rework / g.hasRework : null;
      const row = el("div", "bar-row");
      const w = avg == null ? 0 : (avg / maxRework) * 100;
      row.innerHTML = `<span class="ver-label">${esc(ver)}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${w}%"></div></div>
        <span class="bar-lbl">${avg == null ? "—" : avg.toFixed(2)} (${g.runs} run${g.runs > 1 ? "s" : ""})</span>`;
      card.appendChild(row);
    });
    // gate fail rate summary line
    const summ = versions.map((ver) => {
      const g = byAgent[agent][ver];
      const tot = g.gpass + g.gfail;
      const rate = tot ? Math.round((g.gpass / tot) * 100) : null;
      return `<code>${esc(ver)}</code>: gate pass ${rate == null ? "n/a" : rate + "%"}`;
    }).join(" &middot; ");
    card.appendChild(el("div", "bar-lbl", summ));
    v.appendChild(card);
  });
  if (!Object.keys(byAgent).length) v.appendChild(el("div", "empty", "No metrics to group yet."));
}

// ---- view 4: integrity log -------------------------------------------------
function renderIntegrity(v) {
  title(v, "Integrity log — " + esc(CURRENT_ENG),
    "Typed events from <code>integrity-register.jsonl</code>: gate failures, dead agents, budget pauses, policy blocks, fabrication-audit findings.");
  const rows = curEng().integrity || [];
  if (!rows.length) { v.appendChild(el("div", "empty", "No integrity events — clean run.")); return; }
  const wrap = el("div", "card table-scroll");
  const t = el("table");
  t.innerHTML = `<thead><tr><th>id</th><th>type</th><th>sev</th><th>wave</th><th>agent</th><th>detail</th><th>resolution</th></tr></thead>`;
  const tb = el("tbody");
  rows.forEach((r) => {
    const tr = el("tr");
    const res = r.resolution || "";
    const rc = /^OPEN/i.test(res) ? "resolution-open" : "resolution-resolved";
    tr.innerHTML = `
      <td><code>${esc(r.id)}</code></td>
      <td>${esc(r.type)}</td>
      <td><span class="sev sev-${esc(r.severity)}">${esc(r.severity)}</span></td>
      <td>${esc(r.wave)}</td>
      <td>${esc(r.agent || "—")}</td>
      <td>${esc(r.detail)}${r.artifact ? `<br><small class="bar-lbl">${esc(r.artifact)}</small>` : ""}</td>
      <td class="${rc}">${esc(res || "—")}</td>`;
    tb.appendChild(tr);
  });
  t.appendChild(tb); wrap.appendChild(t); v.appendChild(wrap);
}

// ---- view 5: decision inbox ------------------------------------------------
function renderInbox(v) {
  const items = ((curEng().decisions || {}).open_items) || [];
  const openN = items.filter((i) => !i.resolved).length;
  title(v, "Decision inbox — " + esc(CURRENT_ENG),
    `${openN} awaiting you. Age &amp; AOM-timeout breach clock from each item's <code>created</code>. Approve writes to the local decisions log and clears the item.`);
  if (!items.length) { v.appendChild(el("div", "empty", "No open decisions.")); return; }
  items.forEach((it) => {
    const d = el("div", "decision" + (it.resolved ? " resolved" : ""));
    const age = ageHours(it.created);
    const breach = it.aom_timeout_hours ? age - it.aom_timeout_hours : null;
    let ageCls = "ok", ageTxt = "age " + fmtAge(age);
    if (breach != null) {
      if (breach > 0) { ageCls = "breach"; ageTxt = "age " + fmtAge(age) + " — BREACHED (" + it.aom_class + " " + it.aom_timeout_hours + "h)"; }
      else if (breach > -6) { ageCls = "warn"; ageTxt = "age " + fmtAge(age) + " — breach in " + fmtAge(-breach); }
      else ageTxt = "age " + fmtAge(age) + " — " + fmtAge(-breach) + " to breach";
    }
    d.innerHTML = `<h3>${esc(it.title)} <code style="font-size:11px">${esc(it.id)}</code></h3>
      <div class="age ${ageCls}">${esc(ageTxt)}</div>
      <div class="ctx">${esc(it.context)}</div>
      <div class="bar-lbl">kind: ${esc(it.kind)} &middot; requested by ${esc(it.requested_by)} &middot; owner ${esc(it.owner)}${it.linked_document ? ` &middot; doc: ${esc(it.linked_document)}` : ""}</div>`;
    if (it.resolved) {
      d.appendChild(el("div", "stored-ok", "✓ " + esc(it.resolved.action) + " logged " + esc((it.resolved.ts || "").replace("T", " ").slice(0, 16)) + (it.resolved.comment ? " — “" + esc(it.resolved.comment) + "”" : "")));
    } else {
      const actions = el("div", "actions");
      const input = el("input", "comment");
      input.placeholder = "comment (optional)…";
      const approve = el("button", "act approve", "Approve");
      const comment = el("button", "act", "Comment");
      approve.onclick = () => postDecision(it, "APPROVE", input.value);
      comment.onclick = () => postDecision(it, "COMMENT", input.value);
      actions.append(input, comment, approve);
      if (it.linked_document) {
        const openDoc = el("button", "act", "Open document");
        openDoc.onclick = () => { CURRENT_TAB = "docs"; CURRENT_DOC = it.linked_document; document.querySelectorAll("nav.tabs button").forEach((b) => b.classList.toggle("active", b.textContent === "Documents")); render(); };
        actions.appendChild(openDoc);
      }
      d.appendChild(actions);
    }
    v.appendChild(d);
  });
}

async function postDecision(item, action, comment) {
  try {
    const r = await fetch("/api/decision", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ engagement: CURRENT_ENG, item_id: item.id, action, comment, document: item.linked_document }),
    });
    const j = await r.json();
    if (!j.ok) throw new Error(j.error || "failed");
    toast(action === "APPROVE" ? "Approved — logged locally & item cleared" : "Comment logged locally");
    STATE = await (await fetch("/api/state")).json(); // reload to reflect resolved overlay
    render();
  } catch (e) { toast("Error: " + e.message); }
}

// ---- view 6: RAG -----------------------------------------------------------
function renderRag(v) {
  title(v, "RAG status roll-up",
    "Red/Amber/Green per engagement, computed <strong>worst-of</strong> its wave states (deterministic, no AI). RED = any DEAD/GATE_BLOCKED/TIMED_OUT; AMBER = any BLOCKED/PAUSED/AWAITING_APPROVAL; else GREEN.");
  const grid = el("div", "rag-grid");
  STATE.engagements.forEach((e) => {
    const waves = ((e.wave_status || {}).waves) || {};
    const counts = {};
    Object.values(waves).forEach((w) => { const s = (w || {}).state; counts[s] = (counts[s] || 0) + 1; });
    const worst = Object.entries(counts).map(([s, n]) => `${n} ${s}`).join(", ") || "no waves";
    const tile = el("div", "rag-tile rag-" + e.rag);
    tile.innerHTML = `<h3>${esc(e.id)}</h3><div class="rag-label">${esc(e.rag)}</div><small>${esc(worst)}</small>`;
    grid.appendChild(tile);
  });
  v.appendChild(grid);
}

// ---- view 7: RAID ----------------------------------------------------------
function renderRaid(v) {
  title(v, "RAID board — " + esc(CURRENT_ENG),
    "Risks / Assumptions / Issues / Dependencies from <code>raid-log.yaml</code> (rendered as-is).");
  const raid = curEng().raid || {};
  const sections = [["risks", "Risks"], ["assumptions", "Assumptions"], ["issues", "Issues"], ["dependencies", "Dependencies"]];
  let any = false;
  sections.forEach(([key, label]) => {
    const arr = raid[key];
    if (!Array.isArray(arr) || !arr.length) return;
    any = true;
    const card = el("div", "card");
    card.appendChild(el("h3", null, esc(label) + " (" + arr.length + ")"));
    const wrap = el("div", "table-scroll");
    const t = el("table");
    const cols = key === "risks" ? ["id", "description", "likelihood", "impact", "status", "owner"]
      : key === "assumptions" ? ["id", "description", "validated", "validation_route"]
      : key === "issues" ? ["id", "description", "severity", "status", "owner"]
      : ["id", "description", "depends_on", "needed_by", "timeout_ref"];
    t.innerHTML = "<thead><tr>" + cols.map((c) => `<th>${esc(c)}</th>`).join("") + "</tr></thead>";
    const tb = el("tbody");
    arr.forEach((row) => {
      const tr = el("tr");
      tr.innerHTML = cols.map((c) => `<td>${esc(row[c])}</td>`).join("");
      tb.appendChild(tr);
    });
    t.appendChild(tb); wrap.appendChild(t); card.appendChild(wrap); v.appendChild(card);
  });
  if (!any) v.appendChild(el("div", "empty", "No raid-log.yaml for this engagement."));
}

// ---- view 8: documents -----------------------------------------------------
function renderDocs(v) {
  title(v, "Document review & approval — " + esc(CURRENT_ENG),
    "Read any agent artifact rendered cleanly. Approve / Comment write to the local decisions log. Two versions of a doc &rarr; diff view. Interview transcript &amp; client evidence are view-only reference material.");
  const docs = curEng().documents || [];
  const hasTranscript = !!curEng().has_transcript;
  const locker = curEng().locker || [];
  if (!docs.length && !hasTranscript && !locker.length) {
    v.appendChild(el("div", "empty", "No documents for this engagement.")); return;
  }
  const layout = el("div", "doc-layout");
  const list = el("div", "doc-list card");
  if (docs.length) list.appendChild(el("h3", null, "Deliverables"));
  docs.forEach((name) => {
    const b = el("button", name === CURRENT_DOC ? "active" : "", esc(name));
    b.onclick = () => { CURRENT_DOC = name; render(); };
    list.appendChild(b);
  });
  if (hasTranscript) {
    list.appendChild(el("h3", null, "Interview"));
    const b = el("button", CURRENT_DOC === "__transcript__" ? "active" : "", "Interview transcript");
    b.onclick = () => { CURRENT_DOC = "__transcript__"; render(); };
    list.appendChild(b);
  }
  // diff helper: if two versions of same base exist
  const versionsOf = (n) => {
    const m = n.match(/^(.*?)-v\d+\.\d+\.\d+(\.\w+)$/);
    if (!m) return null;
    return docs.filter((d) => d.startsWith(m[1] + "-v") && d.endsWith(m[2]));
  };
  layout.appendChild(list);
  const pane = el("div");
  const render_area = el("div", "doc-render", '<div class="empty">Select a document to read.</div>');
  if (CURRENT_DOC === "__transcript__") loadTranscript(render_area);
  else if (CURRENT_DOC) loadDoc(CURRENT_DOC, render_area, versionsOf(CURRENT_DOC));
  pane.appendChild(render_area);
  layout.appendChild(pane);
  v.appendChild(layout);

  // evidence locker — provenance table with per-item download (view-only)
  if (locker.length) {
    const card = el("div", "card");
    card.appendChild(el("h3", null, "Evidence locker (" + locker.length + " items) — client-supplied, stored verbatim with provenance"));
    const wrap = el("div", "table-scroll");
    const t = el("table");
    t.innerHTML = "<thead><tr><th>id</th><th>file</th><th>type</th><th>source / supplier</th><th>received</th><th>sha256</th><th></th></tr></thead>";
    const tb = el("tbody");
    locker.forEach((it) => {
      const tr = el("tr");
      tr.innerHTML = `
        <td><code>${esc(it.id)}</code></td>
        <td>${esc(it.file)}</td>
        <td>${esc(it.type || "—")}</td>
        <td>${esc(it.source || "—")}${it.supplier ? " · " + esc(it.supplier) : ""}</td>
        <td>${esc(it.received || "—")}</td>
        <td><code>${esc((it.sha256 || "").slice(0, 12))}…</code></td>
        <td><a class="act" href="/api/attachment?engagement=${encodeURIComponent(CURRENT_ENG)}&name=${encodeURIComponent(it.file)}" target="_blank" rel="noopener">Open</a></td>`;
      tb.appendChild(tr);
    });
    t.appendChild(tb); wrap.appendChild(t); card.appendChild(wrap);
    v.appendChild(card);
  }
}

async function loadTranscript(area) {
  area.innerHTML = '<div class="empty">Loading…</div>';
  const r = await fetch("/api/transcript?engagement=" + encodeURIComponent(CURRENT_ENG));
  if (!r.ok) { area.innerHTML = '<div class="empty">Not found.</div>'; return; }
  const doc = await r.json();
  area.innerHTML = "";
  const note = el("div", "bar-lbl",
    "View-only audit record — the verbatim interview session log. No approval actions here; the DOCUMENT you sign is the draft ECL it produced.");
  area.appendChild(note);
  const body = el("div");
  body.innerHTML = mdToHtml(doc.content);
  area.appendChild(body);
}

async function loadDoc(name, area, siblings) {
  area.innerHTML = '<div class="empty">Loading…</div>';
  const r = await fetch("/api/document?engagement=" + encodeURIComponent(CURRENT_ENG) + "&name=" + encodeURIComponent(name));
  if (!r.ok) { area.innerHTML = '<div class="empty">Not found.</div>'; return; }
  const doc = await r.json();
  area.innerHTML = "";
  // toolbar
  const bar = el("div", "actions");
  const input = el("input", "comment"); input.placeholder = "comment on this document…";
  const approve = el("button", "act approve", "Approve");
  const comment = el("button", "act", "Comment");
  // match a decisions-queue item linked to this doc, else synthesise an id
  const linked = (((curEng().decisions || {}).open_items) || []).find((i) => i.linked_document === name);
  const itemId = linked ? linked.id : "DOC:" + name;
  approve.onclick = () => postDecision({ id: itemId, linked_document: name }, "APPROVE", input.value);
  comment.onclick = () => postDecision({ id: itemId, linked_document: name }, "COMMENT", input.value);
  bar.append(input, comment, approve);
  area.appendChild(bar);

  // diff toggle if 2 versions
  if (siblings && siblings.length === 2) {
    const btn = el("button", "act", "Show version diff (" + siblings.join(" ↔ ") + ")");
    let showing = false;
    const diffBox = el("div"); diffBox.className = "hidden";
    btn.onclick = async () => {
      showing = !showing;
      diffBox.className = showing ? "" : "hidden";
      btn.textContent = showing ? "Hide diff" : "Show version diff (" + siblings.join(" ↔ ") + ")";
      if (showing && !diffBox.dataset.loaded) {
        const [a, b] = await Promise.all(siblings.map((s) =>
          fetch("/api/document?engagement=" + encodeURIComponent(CURRENT_ENG) + "&name=" + encodeURIComponent(s)).then((x) => x.json())));
        diffBox.innerHTML = "<h3>Diff: " + esc(siblings[0]) + " → " + esc(siblings[1]) + "</h3>" + renderDiff(a.content, b.content);
        diffBox.dataset.loaded = "1";
      }
    };
    bar.appendChild(btn);
    area.appendChild(diffBox);
  }

  const body = el("div");
  if (doc.ext === "md") body.innerHTML = mdToHtml(doc.content);
  else if (doc.ext === "yaml" || doc.ext === "yml") body.innerHTML = "<pre>" + esc(doc.content) + "</pre>";
  else body.innerHTML = "<pre>" + esc(doc.content) + "</pre>";
  area.appendChild(body);
}

// simple LCS-free line diff (Myers-lite: mark lines not present in the other)
function renderDiff(a, b) {
  const la = a.split("\n"), lb = b.split("\n");
  const setB = new Set(lb), setA = new Set(la);
  const out = [];
  // show removed (in a not b) and added (in b not a), plus context
  const maxLen = Math.max(la.length, lb.length);
  // align naively by walking both
  let i = 0, j = 0;
  while (i < la.length || j < lb.length) {
    if (i < la.length && j < lb.length && la[i] === lb[j]) {
      out.push(`<div class="diff-line diff-ctx">  ${esc(la[i])}</div>`); i++; j++;
    } else if (j < lb.length && !setA.has(lb[j])) {
      out.push(`<div class="diff-line diff-add">+ ${esc(lb[j])}</div>`); j++;
    } else if (i < la.length && !setB.has(la[i])) {
      out.push(`<div class="diff-line diff-del">- ${esc(la[i])}</div>`); i++;
    } else { i++; j++; }
  }
  return out.join("");
}

// minimal, safe markdown → HTML (headings, bold, code, lists, tables, hr, para)
function mdToHtml(src) {
  const lines = src.replace(/\r/g, "").split("\n");
  let html = "", i = 0;
  const inline = (s) => esc(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  while (i < lines.length) {
    const ln = lines[i];
    if (/^#{1,6}\s/.test(ln)) {
      const lvl = ln.match(/^#+/)[0].length;
      html += `<h${lvl}>${inline(ln.replace(/^#+\s/, ""))}</h${lvl}>`; i++;
    } else if (/^\s*```/.test(ln)) {
      let buf = []; i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) { buf.push(lines[i]); i++; }
      i++; html += "<pre>" + esc(buf.join("\n")) + "</pre>";
    } else if (/^\s*\|.*\|\s*$/.test(ln)) {
      const tbl = []; while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) { tbl.push(lines[i]); i++; }
      html += tableToHtml(tbl, inline);
    } else if (/^\s*[-*]\s+/.test(ln)) {
      html += "<ul>";
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) { html += "<li>" + inline(lines[i].replace(/^\s*[-*]\s+/, "")) + "</li>"; i++; }
      html += "</ul>";
    } else if (/^\s*\d+\.\s+/.test(ln)) {
      html += "<ol>";
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) { html += "<li>" + inline(lines[i].replace(/^\s*\d+\.\s+/, "")) + "</li>"; i++; }
      html += "</ol>";
    } else if (/^\s*---\s*$/.test(ln)) { html += "<hr>"; i++; }
    else if (ln.trim() === "") { i++; }
    else {
      let buf = [ln]; i++;
      while (i < lines.length && lines[i].trim() !== "" && !/^(#{1,6}\s|\s*[-*]\s|\s*\d+\.\s|\s*\||\s*```)/.test(lines[i])) { buf.push(lines[i]); i++; }
      html += "<p>" + inline(buf.join(" ")) + "</p>";
    }
  }
  return html;
}
function tableToHtml(rows, inline) {
  if (rows.length < 2) return "<pre>" + esc(rows.join("\n")) + "</pre>";
  const cells = (r) => r.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
  const head = cells(rows[0]);
  let h = "<table><thead><tr>" + head.map((c) => "<th>" + inline(c) + "</th>").join("") + "</tr></thead><tbody>";
  for (let k = 2; k < rows.length; k++) {
    h += "<tr>" + cells(rows[k]).map((c) => "<td>" + inline(c) + "</td>").join("") + "</tr>";
  }
  return h + "</tbody></table>";
}

// ---- view 9: credentials (BYOK) --------------------------------------------
const CRED_KEY = "framework-console-byok";
function loadCreds() { try { return JSON.parse(localStorage.getItem(CRED_KEY) || "{}"); } catch { return {}; } }
function saveCreds(c) { localStorage.setItem(CRED_KEY, JSON.stringify(c)); }
function maskKey(val) {
  if (!val) return "<unset>";
  if (val.length <= 4) return "*".repeat(val.length);
  return "*".repeat(Math.min(val.length - 4, 20)) + val.slice(-4);
}

function renderCreds(v) {
  title(v, "Credentials — Bring Your Own Key",
    "Enter <strong>your own</strong> keys. Stored in this browser's <code>localStorage</code> only — never sent to any server, never committed. Shown masked to last-4.");
  const banner = el("div", "note");
  banner.innerHTML = "This project ships with <strong>no</strong> credentials. If a key is missing, features that need it show an “enter your key” prompt — never a default or owner key. Clearing your browser storage removes them.";
  v.appendChild(banner);

  const creds = loadCreds();
  const card = el("div", "card");
  KNOWN_SERVICES.forEach(([svc, env, use]) => {
    const row = el("div", "cred-row");
    const stored = creds[env];
    const has = !!stored;
    row.innerHTML = `<div><div class="svc">${esc(svc)}</div><div class="envname">${esc(env)}</div></div>`;
    const mid = el("div");
    const inp = el("input", "comment");
    inp.type = "password";
    inp.placeholder = has ? "stored — enter to replace" : "paste your " + svc + " key (" + use + ")";
    mid.appendChild(inp);
    if (has) mid.appendChild(el("div", "masked", "stored: " + esc(maskKey(stored))));
    else mid.appendChild(el("div", "needkey", "⚠ enter your key to enable " + esc(use)));
    row.appendChild(mid);
    const btns = el("div");
    const save = el("button", "act approve", "Save");
    save.onclick = () => { if (!inp.value) { toast("Nothing to save"); return; } const c = loadCreds(); c[env] = inp.value; saveCreds(c); toast(svc + " key saved locally (masked)"); render(); };
    const clr = el("button", "act", "Clear");
    clr.onclick = () => { const c = loadCreds(); delete c[env]; saveCreds(c); toast(svc + " key cleared"); render(); };
    btns.append(save, clr);
    row.appendChild(btns);
    card.appendChild(row);
  });
  v.appendChild(card);

  const status = el("div", "card");
  const anth = creds["ANTHROPIC_API_KEY"];
  status.innerHTML = anth
    ? `<span class="stored-ok">✓ Anthropic key present (${esc(maskKey(anth))}) — agent-running features would be enabled.</span>`
    : `<span class="needkey">Anthropic key not set — the runtime would fail loud (CredentialError) rather than use any default. Enter your ANTHROPIC_API_KEY above.</span>`;
  v.appendChild(status);
}

boot();
