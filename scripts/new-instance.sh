#!/bin/bash
# ============================================================
# New Instance Bootstrap
# Creates a new business instance repo from the framework
# Usage: ./scripts/new-instance.sh {business-id}
# Example: ./scripts/new-instance.sh riverside-bookings
# ============================================================

set -e

BUSINESS_ID=$1
FRAMEWORK_DIR=$(pwd)
FRAMEWORK_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")
INSTANCE_DIR="../instance-${BUSINESS_ID}"
DATE=$(date +%Y-%m-%d)

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── Validation ───────────────────────────────────────────────

if [ -z "$BUSINESS_ID" ]; then
  echo "Usage: ./scripts/new-instance.sh {business-id}"
  echo "Example: ./scripts/new-instance.sh riverside-bookings"
  exit 1
fi

if ! echo "$BUSINESS_ID" | grep -qE "^[a-z0-9][a-z0-9-]*$"; then
  echo "Error: business-id must be lowercase letters, numbers, and hyphens only"
  echo "Example: riverside-bookings (not Riverside Bookings)"
  exit 1
fi

if [ -d "$INSTANCE_DIR" ]; then
  echo "Error: $INSTANCE_DIR already exists"
  echo "To avoid overwriting an existing instance, this script will not proceed."
  echo "If you intended to create a new instance, choose a different business-id."
  exit 1
fi

echo ""
echo -e "${BLUE}=================================================="
echo "  Agent Framework — New Instance Bootstrap"
echo -e "==================================================${NC}"
echo ""
echo "  Business ID:      $BUSINESS_ID"
echo "  Instance path:    $INSTANCE_DIR"
echo "  Framework version: $FRAMEWORK_VERSION"
echo "  Date:             $DATE"
echo ""
read -p "  Proceed? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "  Cancelled."
  exit 0
fi

# ── Create directory structure ───────────────────────────────

echo ""
echo -e "  ${GREEN}Creating directory structure...${NC}"

mkdir -p "$INSTANCE_DIR"
mkdir -p "$INSTANCE_DIR/ecl"
mkdir -p "$INSTANCE_DIR/rosters/seo/outputs/architecture"
mkdir -p "$INSTANCE_DIR/rosters/seo/outputs/content"
mkdir -p "$INSTANCE_DIR/rosters/seo/outputs/technical"
mkdir -p "$INSTANCE_DIR/rosters/seo/outputs/performance"
mkdir -p "$INSTANCE_DIR/cascade-briefings"
mkdir -p "$INSTANCE_DIR/logs"
mkdir -p "$INSTANCE_DIR/credentials"
mkdir -p "$INSTANCE_DIR/framework-ref"

# ── Copy templates ────────────────────────────────────────────

echo -e "  ${GREEN}Copying templates...${NC}"

# ECL template
if [ -f "$FRAMEWORK_DIR/templates/ecl-instance-template.md" ]; then
  cp "$FRAMEWORK_DIR/templates/ecl-instance-template.md" \
     "$INSTANCE_DIR/ecl/ecl-${BUSINESS_ID}-v0.0.0-template.md"
fi

# Roster config template
if [ -f "$FRAMEWORK_DIR/templates/roster-config-template.yaml" ]; then
  cp "$FRAMEWORK_DIR/templates/roster-config-template.yaml" \
     "$INSTANCE_DIR/rosters/seo/roster-config.yaml"
fi

# ── Create core files ─────────────────────────────────────────

echo -e "  ${GREEN}Creating core files...${NC}"

# README
cat > "$INSTANCE_DIR/README.md" << EOF
# Instance: ${BUSINESS_ID}
**Created:** ${DATE}
**Framework version:** ${FRAMEWORK_VERSION}
**Status:** Initialised — ECL interview pending

## Overview
This is the private instance repository for \`${BUSINESS_ID}\`.
It contains the live ECL, active roster configurations, agent
outputs, and engagement logs for this business.

## ⚠️ Privacy Notice
This repository is PRIVATE. It contains business-specific
objectives, performance data, and API configurations.
Never make this repository public.

## Getting Started
1. Copy \`.env.example\` to \`.env\` and fill in API credentials
2. Run the ECL interview to produce the draft ECL
3. Get human sign-off on the ECL
4. Activate the first roster

## Framework Reference
Built against: \`agent-framework@${FRAMEWORK_VERSION}\`
See \`framework-ref/framework-version.txt\`

## Structure
\`\`\`
ecl/                 ← Live ECL documents
rosters/             ← Active roster configurations and outputs
cascade-briefings/   ← All ECL cascade briefings
logs/                ← Engagement, override, and query logs
credentials/         ← API credential templates (no real values)
framework-ref/       ← Framework version pin
\`\`\`
EOF

# Framework version pin
echo "agent-framework@${FRAMEWORK_VERSION}" > "$INSTANCE_DIR/framework-ref/framework-version.txt"
echo "pinned: ${DATE}" >> "$INSTANCE_DIR/framework-ref/framework-version.txt"

# Roster registry (empty at initialisation)
cat > "$INSTANCE_DIR/rosters/seo/roster-registry.yaml" << EOF
# Roster Registry — ${BUSINESS_ID}
# Updated automatically by ecl_orchestrator_agent
business_id: "${BUSINESS_ID}"
last_updated: "${DATE}"
active_rosters: []
planned_rosters:
  - roster_id: "roster-seo"
    target_activation: "pending-ecl-signoff"
    dependency: "ECL v1.0.0 sign-off required"
EOF

# Engagement context placeholder
cat > "$INSTANCE_DIR/rosters/seo/engagement-context.yaml" << EOF
# Engagement Context — ${BUSINESS_ID}
# Populated by ecl_orchestrator_agent after ECL sign-off
business_id: "${BUSINESS_ID}"
status: "pending-ecl-interview"
ecl_version: ""
activated_date: ""

# Fields populated after ECL interview:
country: ""
service_category: ""
target_regions: []
brand_name_candidates: []
neighbourhood_depth: false
north_star_metric: ""
north_star_target: ""
north_star_horizon: ""
EOF

# Credentials template
cat > "$INSTANCE_DIR/credentials/credentials-template.yaml" << EOF
# Credentials Template — ${BUSINESS_ID}
# Lists all API keys required for active rosters
# NEVER store real values here — use .env file

seo_roster:
  # Category 1 — SERP Analysis
  semrush_api_key: "SEMRUSH_API_KEY"
  ahrefs_api_key: "AHREFS_API_KEY"
  dataforseo_login: "DATAFORSEO_LOGIN"
  dataforseo_password: "DATAFORSEO_PASSWORD"

  # Category 4 — Local SEO & Citations
  brightlocal_api_key: "BRIGHTLOCAL_API_KEY"
  gbp_oauth_client_id: "GBP_OAUTH_CLIENT_ID"
  gbp_oauth_client_secret: "GBP_OAUTH_CLIENT_SECRET"

  # Category 5 — AEO & AI Surface Monitoring
  openai_api_key: "OPENAI_API_KEY"
  perplexity_api_key: "PERPLEXITY_API_KEY"

  # Category 6 — GEO & Knowledge Graph
  google_kg_api_key: "GOOGLE_KG_API_KEY"
  wikidata_oauth_token: "WIKIDATA_OAUTH_TOKEN"

  # Category 7 — Analytics & Reporting
  ga4_property_id: "GA4_PROPERTY_ID"
  gsc_site_url: "GSC_SITE_URL"

constitutional:
  anthropic_api_key: "ANTHROPIC_API_KEY"
EOF

# .env.example
cat > "$INSTANCE_DIR/.env.example" << EOF
# Environment Variables — ${BUSINESS_ID}
# Copy this file to .env and fill in real values
# NEVER commit .env to version control

# SEO Roster — Category 1
SEMRUSH_API_KEY=
AHREFS_API_KEY=
DATAFORSEO_LOGIN=
DATAFORSEO_PASSWORD=

# SEO Roster — Category 4
BRIGHTLOCAL_API_KEY=
GBP_OAUTH_CLIENT_ID=
GBP_OAUTH_CLIENT_SECRET=

# SEO Roster — Category 5
OPENAI_API_KEY=
PERPLEXITY_API_KEY=

# SEO Roster — Category 6
GOOGLE_KG_API_KEY=
WIKIDATA_OAUTH_TOKEN=

# SEO Roster — Category 7
GA4_PROPERTY_ID=
GSC_SITE_URL=

# Constitutional Layer
ANTHROPIC_API_KEY=
EOF

# .gitignore
cat > "$INSTANCE_DIR/.gitignore" << EOF
# NEVER commit credentials
.env
*.env.local
*.env.production

# Never commit raw outputs with PII
rosters/*/outputs/content/draft-*
rosters/*/outputs/performance/raw-*

# OS files
.DS_Store
Thumbs.db

# Editor files
.vscode/
.idea/
*.swp
EOF

# Engagement log (empty)
cat > "$INSTANCE_DIR/logs/engagement-log.yaml" << EOF
# Engagement Log — ${BUSINESS_ID}
# All orchestrator decisions, cascades, queries, and escalations
# Append-only — never edit existing entries
business_id: "${BUSINESS_ID}"
framework_version: "${FRAMEWORK_VERSION}"
created: "${DATE}"
entries: []
EOF

# Override log (empty)
cat > "$INSTANCE_DIR/logs/override-log.yaml" << EOF
# Override Log — ${BUSINESS_ID}
# All human override events per AOM Section 7
business_id: "${BUSINESS_ID}"
created: "${DATE}"
entries: []
EOF

# Query log (empty)
cat > "$INSTANCE_DIR/logs/query-log.yaml" << EOF
# Query Log — ${BUSINESS_ID}
# All roster orchestrator queries to ECL Orchestrator
business_id: "${BUSINESS_ID}"
created: "${DATE}"
entries: []
EOF

# ── Initialise git repo ───────────────────────────────────────

echo -e "  ${GREEN}Initialising git repository...${NC}"

cd "$INSTANCE_DIR"
git init -q
git add .
git commit -q -m "chore: initialise instance ${BUSINESS_ID} from agent-framework@${FRAMEWORK_VERSION}"

# ── Done ──────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}=================================================="
echo "  Instance created successfully"
echo -e "==================================================${NC}"
echo ""
echo "  Location:   $INSTANCE_DIR"
echo "  Git status: Initialised with first commit"
echo ""
echo -e "${YELLOW}  Next steps:${NC}"
echo ""
echo "  1. Push to a private GitHub repo:"
echo "     cd $INSTANCE_DIR"
echo "     gh repo create instance-${BUSINESS_ID} --private --source=. --push"
echo ""
echo "  2. Set up credentials:"
echo "     cp .env.example .env"
echo "     # Edit .env with real API keys"
echo ""
echo "  3. Run the ECL interview:"
echo "     # Open Claude with ecl-interview-agent-v1.0.0.yaml loaded"
echo "     # Conduct the interview for ${BUSINESS_ID}"
echo "     # Save draft ECL to: ecl/ecl-${BUSINESS_ID}-v0.1.0.md"
echo ""
echo "  4. Get ECL sign-off and activate:"
echo "     # Human reviews and approves ECL"
echo "     # ECL Orchestrator versions to v1.0.0"
echo "     # First roster cascade issued"
echo ""
echo "  Framework reference: agent-framework@${FRAMEWORK_VERSION}"
echo ""

