#!/bin/bash
# AOM Compliance Check — macOS/Linux compatible v1.0.1
SEARCH_PATH=${1:-"./rosters/seo/agents"}
PASS=0; FAIL=0; WARN_COUNT=0
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

echo ""; echo -e "${BLUE}=================================================="; echo "  AOM Compliance Check — v1.0.1 (macOS compatible)"; echo -e "==================================================${NC}"; echo "  Checking: $SEARCH_PATH"; echo ""

FILES=$(find "$SEARCH_PATH" -name "agent-*.yaml" | sort)
[ -z "$FILES" ] && echo "No agent YAML files found" && exit 0

for file in $FILES; do
  filename=$(basename "$file"); file_errors=(); file_warns=()

  # S1.1 Agent ID format
  id=$(grep "^  id:" "$file" 2>/dev/null | head -1 | sed 's/^  id: *//' | tr -d '"')
  [ -z "$id" ] && file_errors+=("FAIL [S1.1] agent.id missing") || \
  { ! echo "$id" | grep -qE "^[a-z][a-z0-9_]*_agent$" && file_errors+=("FAIL [S1.1] '$id' must end in _agent and be lowercase"); }

  # S2.1 Version semver
  ver=$(grep "^  version:" "$file" 2>/dev/null | head -1 | sed 's/^  version: *//' | tr -d '"')
  [ -z "$ver" ] && file_errors+=("FAIL [S2.1] agent.version missing") || \
  { ! echo "$ver" | grep -qE "^[0-9]+\.[0-9]+\.[0-9]+$" && file_errors+=("FAIL [S2.1] version '$ver' not valid semver"); }

  # S2.2 Required agent fields
  for f in name role roster discipline version; do
    grep -q "^  ${f}:" "$file" 2>/dev/null || file_errors+=("FAIL [S2.2] agent.${f} missing")
  done

  # S2.2 definition_depth, lifecycle_status, aom_compliance
  grep -q "definition_depth:" "$file" 2>/dev/null || file_errors+=("FAIL [S2.2] definition_depth missing")
  grep -q "aom_compliance:" "$file" 2>/dev/null || file_errors+=("FAIL [S2.2] aom_compliance missing")

  # S5.4 lifecycle_status valid value
  if ! grep -q "lifecycle_status:" "$file" 2>/dev/null; then
    file_errors+=("FAIL [S5.4] lifecycle_status missing")
  else
    ls=$(grep "lifecycle_status:" "$file" | head -1 | sed 's/.*lifecycle_status: *//' | tr -d '"')
    echo "draft review active deprecated archived" | grep -qw "$ls" || file_errors+=("FAIL [S5.4] lifecycle_status '$ls' invalid")
  fi

  # S2.2 Required agent sections
  for s in goal backstory constraints; do
    grep -q "^  ${s}:" "$file" 2>/dev/null || file_errors+=("FAIL [S2.2] agent.${s} section missing")
  done

  # S2.1 Required top-level sections
  for s in inputs outputs handoffs; do
    grep -q "^${s}:" "$file" 2>/dev/null || file_errors+=("FAIL [S2.1] top-level '${s}:' missing")
  done

  # S2.1 All 5 cycle phases
  for p in goal_phase plan_phase act_phase review_phase learn_phase; do
    grep -q "${p}:" "$file" 2>/dev/null || file_errors+=("FAIL [S2.1] cycle.${p} missing")
  done

  # S3.1 Handoff to_agent IDs
  if grep -q "^handoffs:" "$file" 2>/dev/null; then
    while IFS= read -r line; do
      ref=$(echo "$line" | sed 's/.*to_agent: *//' | tr -d '"' | tr -d "'")
      echo "$ref" | grep -qE "self|human_ai_manager|All active|Querying" && continue
      echo "$ref" | grep -qE "_agent$" || file_errors+=("FAIL [S3.1] to_agent '$ref' must end in _agent")
    done < <(grep "to_agent:" "$file" 2>/dev/null)
    echo "$id" | grep -q "orchestrator" || \
      grep -q "orchestrator_agent" "$file" 2>/dev/null || \
      file_warns+=("WARN [S3.3] No escalation to orchestrator agent found")
  fi

  # S8.4 Non-fabrication gate
  grep -iE "non.fabrication|non-fabrication|fabricat" "$file" 2>/dev/null | grep -q . || \
    file_errors+=("FAIL [S8.4] Non-fabrication quality gate missing")
  grep -q "blocking: true" "$file" 2>/dev/null || \
    file_errors+=("FAIL [S8.1] No 'blocking: true' gate found")

  # Output
  if [ ${#file_errors[@]} -eq 0 ] && [ ${#file_warns[@]} -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} $filename"; PASS=$((PASS+1))
  elif [ ${#file_errors[@]} -eq 0 ]; then
    echo -e "  ${YELLOW}~${NC} $filename"
    for w in "${file_warns[@]}"; do echo -e "      ${YELLOW}$w${NC}"; done
    PASS=$((PASS+1)); WARN_COUNT=$((WARN_COUNT+${#file_warns[@]}))
  else
    echo -e "  ${RED}✗${NC} $filename"
    for e in "${file_errors[@]}"; do echo -e "      ${RED}$e${NC}"; done
    for w in "${file_warns[@]}"; do echo -e "      ${YELLOW}$w${NC}"; done
    FAIL=$((FAIL+1)); WARN_COUNT=$((WARN_COUNT+${#file_warns[@]}))
  fi
done

echo ""; echo "=================================================="; echo "  Results: ${PASS} passed, ${FAIL} failed, ${WARN_COUNT} warnings"; echo "=================================================="
if [ $FAIL -gt 0 ]; then
  echo -e "\n  ${RED}Resolve failures before activating agents.${NC}\n"; exit 1
else
  echo -e "\n  ${GREEN}All agents pass AOM v1.0.0 compliance.${NC}\n"; exit 0
fi
