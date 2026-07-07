#!/usr/bin/env python3
"""
Framework Validator — AOM v1.0.x deep compliance + drift prevention.

Supersedes the grep-based aom-compliance-check.sh as the authoritative
check (the shell script remains as a quick local smoke test). Run from
the repo root:

    python3 scripts/validate_framework.py

Exit code 0 = all checks pass (warnings allowed).
Exit code 1 = one or more errors — must be fixed before merge.

Checked (errors):
  E1  Agent YAML parses
  E2  agent.id format: ^[a-z][a-z0-9_]*_agent$          (AOM S1.1)
  E3  agent.version is MAJOR.MINOR.PATCH semver          (AOM S2.2)
  E4  Filename version == agent.version                  (AOM S2.2)
  E5  Header '# Version:' comment == agent.version       (drift)
  E6  Required agent fields present: name, role, roster, discipline,
      version, definition_depth, lifecycle_status, aom_compliance,
      goal, backstory, constraints                       (AOM S2)
  E7  constraints has >= 3 entries                       (AOM S2.2)
  E8  lifecycle_status is a valid stage                  (AOM S5.4)
  E9  Top-level inputs, outputs, cycle, handoffs present (AOM S2.1)
  E10 All 5 cycle phases present                         (AOM S2.1)
  E11 Non-fabrication gate present + a blocking gate     (AOM S8.4)
  E12 Every handoff to_agent resolves to a known agent id,
      'self', a human target, or an allowed broadcast    (AOM S3.1)
  E13 Manifest consistency: every non-archived agent file on disk is
      in rosters/manifest.yaml and vice versa, with matching versions
  E14 Roster/constitutional doc filename version == its **Version:** field
  E15 Roster doc version appears in its own Version History table
  E16 Handoff pass-item contract (AOM S3.1 as clarified in v1.0.2):
      every pass item is (a) a declared output/input of the sender, or
      (b) a relayed artifact declared as an output by another agent in
      the same roster or the constitutional layer, or (c) ad-hoc payload
      on an escalation/query/self/human/broadcast handoff, or (d) an
      ECL-sourced context field (engagement_context, ecl_summary,
      target_regions)
  E17 At least one phase gate in the GPARL cycle (AOM S8.2)
  E18 consumed_by / source agent references resolve to known agent ids
      (wildcard roster_*_orchestrator_agent notation allowed)

Checked (warnings):
  W1  Non-orchestrator agent has no escalation handoff to an
      orchestrator agent                                 (AOM S3.3)
  W2  inputs.required entries lack a structured 'source:' field
      (comment-only sources are not machine-checkable)   (AOM S2.2)
  W3  definition_depth is 'lean' without a deepening note
"""

import glob
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(REPO, "rosters", "manifest.yaml")

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
AGENT_ID = re.compile(r"^[a-z][a-z0-9_]*_agent$")
LIFECYCLES = {"draft", "review", "active", "deprecated", "archived"}
CYCLE_PHASES = ["goal_phase", "plan_phase", "act_phase", "review_phase", "learn_phase"]
REQ_AGENT_FIELDS = ["name", "role", "roster", "discipline", "version",
                    "definition_depth", "lifecycle_status", "aom_compliance",
                    "goal", "backstory", "constraints"]
# to_agent values that are legitimately not single agent ids:
# self-resumption, human recipients, broadcasts to all active
# orchestrators, and dynamic reply-to-querier targets
TO_AGENT_ALLOWED = re.compile(
    r"self|human|broadcast|All active|querying", re.IGNORECASE)

errors, warnings = [], []


def err(f, code, msg):
    errors.append(f"  ERROR {code} [{os.path.relpath(f, REPO)}] {msg}")


def warn(f, code, msg):
    warnings.append(f"  WARN  {code} [{os.path.relpath(f, REPO)}] {msg}")


def agent_files():
    pats = ["agents/agent-*.yaml", "rosters/*/agents/agent-*.yaml"]
    files = []
    for p in pats:
        files += glob.glob(os.path.join(REPO, p))
    return sorted(f for f in files if "/archive/" not in f)


def filename_version(path):
    m = re.search(r"-v(\d+\.\d+\.\d+)\.(ya?ml|md)$", os.path.basename(path))
    return m.group(1) if m else None


def header_version(path):
    with open(path) as fh:
        for line in fh:
            m = re.match(r"^#\s*Version:\s*([\d.]+)", line)
            if m:
                return m.group(1)
            if not line.startswith("#") and line.strip():
                break
    return None


def deep_find_gates(node, found):
    """Recursively collect dicts that look like quality gates."""
    if isinstance(node, dict):
        if "gate" in node or "check" in node:
            found.append(node)
        for v in node.values():
            deep_find_gates(v, found)
    elif isinstance(node, list):
        for v in node:
            deep_find_gates(v, found)


def validate_agent(path, known_ids):
    try:
        doc = yaml.safe_load(open(path))
    except Exception as e:
        err(path, "E1", f"YAML parse failure: {e}")
        return None
    if not isinstance(doc, dict) or "agent" not in doc:
        err(path, "E1", "no top-level 'agent:' block")
        return None
    a = doc["agent"]

    aid = a.get("id", "")
    if not AGENT_ID.match(str(aid)):
        err(path, "E2", f"agent.id '{aid}' violates naming convention")

    ver = str(a.get("version", ""))
    if not SEMVER.match(ver):
        err(path, "E3", f"agent.version '{ver}' is not semver")
    fnv = filename_version(path)
    if fnv and ver and fnv != ver:
        err(path, "E4", f"filename v{fnv} != agent.version {ver}")
    hv = header_version(path)
    if hv and ver and hv != ver:
        err(path, "E5", f"header comment v{hv} != agent.version {ver}")

    for field in REQ_AGENT_FIELDS:
        if field not in a or a[field] in (None, ""):
            err(path, "E6", f"agent.{field} missing or empty")

    cons = a.get("constraints") or []
    if isinstance(cons, list) and len(cons) < 3:
        err(path, "E7", f"only {len(cons)} constraints (minimum 3)")

    ls = a.get("lifecycle_status")
    if ls not in LIFECYCLES:
        err(path, "E8", f"lifecycle_status '{ls}' invalid")

    for section in ["inputs", "outputs", "handoffs"]:
        if section not in doc:
            err(path, "E9", f"top-level '{section}:' missing")
    cyc = doc.get("cycle") or {}
    for phase in CYCLE_PHASES:
        if phase not in cyc:
            err(path, "E10", f"cycle.{phase} missing")

    raw = open(path).read()
    if not re.search(r"non.?fabricat", raw, re.IGNORECASE):
        err(path, "E11", "non-fabrication gate missing")
    gates = []
    deep_find_gates(doc, gates)
    if not any(g.get("blocking") is True for g in gates):
        err(path, "E11", "no gate with 'blocking: true' found")

    handoffs = doc.get("handoffs") or []
    has_orch_escalation = False
    for h in handoffs:
        if not isinstance(h, dict):
            continue
        t = str(h.get("to_agent", ""))
        if TO_AGENT_ALLOWED.search(t):
            if "orchestrator" in t:
                has_orch_escalation = True
            continue
        if not t.endswith("_agent"):
            err(path, "E12", f"to_agent '{t}' is not an agent id or allowed target")
        elif t not in known_ids:
            err(path, "E12", f"to_agent '{t}' not found in any roster/manifest")
        if "orchestrator" in t:
            has_orch_escalation = True
    if aid and "orchestrator" not in str(aid) and not has_orch_escalation:
        warn(path, "W1", "no escalation handoff to an orchestrator agent")

    req_inputs = (doc.get("inputs") or {}).get("required") or []
    unstructured = [i for i in req_inputs
                    if not (isinstance(i, dict) and ("source" in i))]
    if unstructured:
        warn(path, "W2", f"{len(unstructured)} required input(s) without a "
                         "structured 'source:' field")

    if a.get("definition_depth") == "lean" and "lean" not in raw.lower().split("definition_depth")[0] \
            and not re.search(r"reason for lean", raw, re.IGNORECASE):
        warn(path, "W3", "lean definition without a documented reason/deepening note")

    return {"id": aid, "version": ver, "file": os.path.relpath(path, REPO),
            "lifecycle": ls, "roster": a.get("roster")}


CONTEXT_FIELDS = {"engagement_context", "ecl_summary", "target_regions"}
ESCALATION_TARGET = re.compile(
    r"orchestrator|human|self|querying|broadcast|All active", re.IGNORECASE)
WILDCARD_REF = re.compile(r"roster_\*_orchestrator_agents?")


def outputs_of(doc):
    outs = set()
    op = doc.get("outputs") or {}
    if isinstance(op, dict):
        for o in op.get("primary", []) or []:
            if isinstance(o, dict) and "name" in o:
                outs.add(o["name"])
        for k, v in op.items():
            if k == "primary":
                continue
            outs.add(k)
            # nested named entries (e.g. human_input_flags lists)
            if isinstance(v, list):
                for o in v:
                    if isinstance(o, dict) and "name" in o:
                        outs.add(o["name"])
    return outs


def inputs_of(doc):
    ins = set()
    for sec in ("required", "optional", "tool_data_required"):
        for i in ((doc.get("inputs") or {}).get(sec) or []):
            if isinstance(i, dict) and "name" in i:
                ins.add(i["name"])
            elif isinstance(i, dict):
                ins.update(i.keys())
            elif isinstance(i, str):
                ins.add(i.split()[0].rstrip(":"))
    return ins


def validate_contracts(parsed):
    """E16/E17/E18 — cross-agent semantic checks. parsed: {file: doc}."""
    ids = {d["agent"]["id"]: f for f, d in parsed.items()}
    roster_of, producers = {}, {}
    for f, d in parsed.items():
        aid = d["agent"]["id"]
        parts = os.path.relpath(f, REPO).split(os.sep)
        roster_of[aid] = parts[1] if parts[0] == "rosters" else "constitutional"
        for o in outputs_of(d):
            producers.setdefault(o, set()).add(aid)

    for f, d in parsed.items():
        aid = d["agent"]["id"]
        mine = outputs_of(d) | inputs_of(d) | CONTEXT_FIELDS
        # E16 — pass-item contract
        for h in (d.get("handoffs") or []):
            if not isinstance(h, dict):
                continue
            target = str(h.get("to_agent", ""))
            for item in (h.get("pass") or []):
                name = (item if isinstance(item, str) else str(item)).strip()
                if name in mine:
                    continue
                prods = producers.get(name, set())
                if any(roster_of.get(p) in (roster_of[aid], "constitutional")
                       for p in prods):
                    continue  # legitimate relay
                if ESCALATION_TARGET.search(target):
                    continue  # ad-hoc escalation/query payload
                err(f, "E16", f"handoff passes '{name}' to '{target}' — no "
                              "declared producer and not an escalation payload")
        # E17 — at least one phase gate
        cyc = d.get("cycle") or {}
        if not any(isinstance(b, dict) and ("gate" in b or "checks" in b)
                   for b in cyc.values()):
            err(f, "E17", "no phase gate anywhere in GPARL cycle (AOM S8.2)")
        # E18 — consumed_by / source references resolve
        refs = []
        op = d.get("outputs") or {}
        for o in (op.get("primary", []) or []) if isinstance(op, dict) else []:
            if isinstance(o, dict) and o.get("consumed_by"):
                refs.append(("consumed_by", str(o["consumed_by"])))
        for sec in ("required", "optional"):
            for i in ((d.get("inputs") or {}).get(sec) or []):
                if isinstance(i, dict) and i.get("source"):
                    refs.append(("source", str(i["source"])))
        for kind, ref in refs:
            cleaned = WILDCARD_REF.sub("", ref)
            for m in re.findall(r"[a-z][a-z0-9_]*_agent", cleaned):
                if m not in ids:
                    err(f, "E18", f"{kind} references unknown agent '{m}'")


def validate_versioned_doc(path):
    """Roster and constitutional markdown docs: filename vs **Version:** field."""
    fnv = filename_version(path)
    if not fnv:
        return
    text = open(path).read()
    m = re.search(r"\*\*Version:\*\*\s*`?v?([\d.]+)`?", text)
    if not m:
        err(path, "E14", "no **Version:** field found")
        return
    if m.group(1) != fnv:
        err(path, "E14", f"filename v{fnv} != document Version field v{m.group(1)}")
    # version history must mention current version
    if re.search(r"##\s*Version History", text) and f"v{fnv}" not in text.split("Version History")[1][:4000]:
        err(path, "E15", f"v{fnv} has no entry in its own Version History table")


def validate_manifest(found_agents):
    if not os.path.exists(MANIFEST_PATH):
        err(MANIFEST_PATH, "E13", "rosters/manifest.yaml missing")
        return
    try:
        manifest = yaml.safe_load(open(MANIFEST_PATH))
    except Exception as e:
        err(MANIFEST_PATH, "E13", f"manifest parse failure: {e}")
        return
    listed = {}
    for roster in (manifest.get("rosters") or []):
        for ag in (roster.get("agents") or []):
            listed[ag["id"]] = ag
    for ag in (manifest.get("constitutional_agents") or []):
        listed[ag["id"]] = ag

    disk = {a["id"]: a for a in found_agents if a}
    for aid, a in disk.items():
        if aid not in listed:
            err(MANIFEST_PATH, "E13", f"agent '{aid}' on disk but not in manifest")
        else:
            if str(listed[aid].get("version")) != a["version"]:
                err(MANIFEST_PATH, "E13",
                    f"'{aid}' manifest version {listed[aid].get('version')} != file version {a['version']}")
            if listed[aid].get("file") != a["file"]:
                err(MANIFEST_PATH, "E13",
                    f"'{aid}' manifest file path '{listed[aid].get('file')}' != actual '{a['file']}'")
    for aid in listed:
        if aid not in disk:
            err(MANIFEST_PATH, "E13", f"agent '{aid}' in manifest but not on disk")


def main():
    files = agent_files()
    # First pass: collect ids so handoff targets can be resolved
    known_ids = set()
    for f in files:
        try:
            d = yaml.safe_load(open(f))
            known_ids.add(d["agent"]["id"])
        except Exception:
            pass

    found = [validate_agent(f, known_ids) for f in files]

    parsed = {}
    for f in files:
        try:
            d = yaml.safe_load(open(f))
            if isinstance(d, dict) and "agent" in d:
                parsed[f] = d
        except Exception:
            pass  # parse failures already reported as E1
    validate_contracts(parsed)

    for doc in sorted(glob.glob(os.path.join(REPO, "rosters/*/roster-*.md")) +
                      glob.glob(os.path.join(REPO, "constitutional/*.md"))):
        validate_versioned_doc(doc)

    validate_manifest(found)

    print("=" * 60)
    print(f"  Framework Validator — {len(files)} agents, "
          f"{len(errors)} errors, {len(warnings)} warnings")
    print("=" * 60)
    for e in errors:
        print(e)
    for w in warnings:
        print(w)
    if not errors and not warnings:
        print("  All checks passed.")
    print("=" * 60)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
