# 🐉 Cymru v28 Policy Engine — Complete Deployment Guide

**Version:** v28.1  
**Status:** Ready for deployment  
**Budget:** £62.5bn matched to 3 seed policies (Cardiff, Swansea, Conwy)  
**Last updated:** 2026-06-26  

---

## 🎯 What This Is

**Cymru v28 Policy Engine** is a **non-weaponised civic planning system** that:

- Mixes **three computing/engineering policies** dynamically
- Matches them to a **£62.5bn national resilience/SPACE budget**
- Scores them against **12 De Bono cognitive lenses** (White, Red, Black, Yellow, Green, Blue, Purple, Pink, Brown, Grey, Gold, Silver)
- Generates **ACID-compliant SQL** and **Neo4j Cypher** exports in real-time
- Provides **Gantt dependency timelines** and **policy evaluation dashboards**
- Uses **weak-signal early-warning logic** (from predation ecology) as civic opportunity intelligence

**Scope:** Non-weaponised civil resilience, education, health, sport, enterprise, eco-science, and SPACE-readiness planning.

---

## 📁 Repository Structure

```
agi-ai-mi-iid-ml/
├── cymru_v27_policy_mixer_webui.html          # Dynamic HTML5 dashboard (no server needed)
├── cymru_v28_policy_engine.sql                # Complete ACID SQLite schema + data
├── cymru_v28_policy_engine.cypher             # Neo4j graph export (72 MERGE statements)
├── cymru_v27_budget_plan.json                 # Budget metadata + 13 harmonics model
├── cymru_v27_budget_plan.py                   # Python budget validation utilities
├── CYMRU_V28_DEPLOYMENT_GUIDE.md              # This file
├── README.md                                  # Original project README
└── docs/
    ├── CARDIFF_EDUCATION_DIGITAL_ARCH_001.md  # Policy 1: £22.5bn education labs
    ├── SWANSEA_APPRENTICE_TEAM_SANDBOX_002.md # Policy 2: £20.0bn apprentice pods
    └── CONWY_COMPUTING_RURAL_RESILIENCE_003.md# Policy 3: £20.0bn rural weak-signal
```

---

## 🚀 Quick Start (5 minutes)

### **Option A: Browser Dashboard (Instant, No Setup)**

1. Download `cymru_v27_policy_mixer_webui.html`
2. Open in any modern browser
3. Toggle policies, adjust budgets, watch SQL/Cypher generate in real-time
4. Copy or download exports

**URL:** `file:///path/to/cymru_v27_policy_mixer_webui.html`

### **Option B: SQLite Database**

```bash
# Install SQLite (macOS with Homebrew)
brew install sqlite3

# Load the ACID database
sqlite3 cymru_v28_policy_engine.sqlite3 < cymru_v28_policy_engine.sql

# Query all policies
sqlite3 cymru_v28_policy_engine.sqlite3 \
  "SELECT policy_id, title, scaled_allocation FROM policies;"

# Export to CSV
sqlite3 cymru_v28_policy_engine.sqlite3 \
  ".mode csv" \
  "SELECT * FROM hat_scores;" > hat_scores.csv
```

### **Option C: Neo4j Graph Database**

```bash
# Start Neo4j (Docker)
docker run --rm -p 7474:7474 -p 7687:7687 neo4j:latest

# Load Cypher file via Neo4j Browser (http://localhost:7474)
# Paste cymru_v28_policy_engine.cypher into the query editor
# Execute in batches of 50 statements

# Or via CLI
cypher-shell -u neo4j -p password < cymru_v28_policy_engine.cypher
```

---

## 📊 Budget Allocation (£62.5bn)

| Policy | Authority | Allocation | Share | Timeline |
|--------|-----------|------------|-------|----------|
| 🏛️ **Cardiff School-to-SPACE Labs** | Cardiff | **£22.5bn** | 36.0% | 60 months (5 years) |
| 🏭 **Swansea Apprentice Pods + Sandbox** | Swansea | **£20.0bn** | 32.0% | 84 months (7 years) |
| 🐭 **Conwy Rural Weak-Signal Network** | Conwy | **£20.0bn** | 32.0% | 72 months (6 years) |
| **TOTAL** | Wales | **£62.5bn** | 100% | Concurrent |

---

## 🧠 The Three Policies Explained

### **Policy 1: Cardiff Education Digital Architecture Lab (36%)**

**Mission:** Turn schools into bilingual digital hives.

**What it does:**
- 22 Welsh schools receive school-to-SPACE labs (astronomy, robotics, maker benches)
- Teachers get professional learning + wage uplift
- 1,200 Year 9 students per year coding pathway
- Feeds 120 apprentices/year to Swansea pods
- Bilingual (Welsh/English) AI ethics curriculum

**Budget breakdown:**
- School labs: £6.5bn
- Teacher capability: £3.5bn
- Learner devices: £3.0bn
- Broadband: £2.5bn
- Curriculum: £1.6bn
- Industry mentors: £2.0bn
- Evaluation: £0.9bn
- Contingency: £2.5bn

**De Bono hat scores:**
- 🥈 **Silver (Systems):** 0.92 — excellent network effects
- 🟡 **Yellow (Optimism):** 0.91 — strong upside
- 🟨 **Gold (Value):** 0.90 — high ROI
- ⚪ **White (Facts):** 0.86 — strong evidence

---

### **Policy 2: Swansea Apprentice Pods + Innovation Sandbox (32%)**

**Mission:** Make paid apprenticeships the route from education to enterprise.

**What it does:**
- 240 apprentices/year in 3-person "pods"
- Each pod works on real products (fintech, govtech, agritech)
- Mentored by industry + academic supervisors
- Apprentices get 0.1% equity in startups
- FCA regulatory sandbox testing
- Expected 192 jobs placed per year

**Budget breakdown:**
- Apprentice wages: £6.5bn
- Employer co-investment matched: £3.2bn
- Innovation sandboxes: £1.8bn
- Product labs: £2.6bn
- Mentoring: £1.7bn
- Equity/founder fund: £1.8bn
- Open-source stack: £0.9bn
- Evaluation: £1.5bn

**De Bono hat scores:**
- 🟨 **Gold (Value):** 0.93 — highest revenue potential
- 🔵 **Blue (Process):** 0.79 — some process risk
- ⚙️ **Grey (Uncertainty):** 0.71 — market volatility unknown

---

### **Policy 3: Conwy Rural Weak-Signal Early Warning Network (32%)**

**Mission:** Turn rural problems into curriculum, prototypes, jobs.

**What it does:**
- 8 distributed learning hubs (not centralized)
- Monthly "weak-signal" scans: farmers, tourism, infrastructure
- Community signals → curriculum → apprentices → products
- Agritech testbeds (soil, water, livestock sensors)
- Tourism tech integration
- Youth retention incentives (returner grants, local jobs)

**Budget breakdown:**
- Rural hubs: £3.6bn
- Agritech sensors: £3.1bn
- Broadband/edge: £2.8bn
- Weak-signal system: £2.1bn
- Tourism/heritage tech: £1.8bn
- Youth retention: £2.5bn
- Enterprise/products: £2.5bn
- Resilience: £1.6bn

**De Bono hat scores:**
- 🩷 **Pink (Empathy):** 0.93 — strongest stakeholder alignment
- 🟫 **Brown (Heritage):** 0.92 — respects local culture
- 🟢 **Green (Creativity):** 0.91 — highly adaptive

---

## 🗄️ Database Schema

### **Core Tables (SQL)**

```sql
-- Meta information
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);

-- De Bono hats
CREATE TABLE hats (
  hat_id TEXT PRIMARY KEY,
  name TEXT,
  icon TEXT,
  mode TEXT
);

-- 13 Welsh harmonics
CREATE TABLE harmonics (
  harmonic_id TEXT PRIMARY KEY,
  name TEXT,
  icon TEXT
);

-- Policies
CREATE TABLE policies (
  policy_id TEXT PRIMARY KEY,
  title TEXT,
  authority TEXT,
  template TEXT,
  pilot_budget REAL,
  scaled_allocation REAL,
  allocation_share_pct REAL,
  mission TEXT,
  summary TEXT
);

-- Budget lines (how money is spent)
CREATE TABLE budget_lines (
  line_id INTEGER PRIMARY KEY,
  policy_id TEXT,
  name TEXT,
  amount REAL,
  notes TEXT
);

-- Hat scores (policy evaluation)
CREATE TABLE hat_scores (
  policy_id TEXT,
  hat_id TEXT,
  score REAL CHECK(score BETWEEN 0 AND 1),
  PRIMARY KEY(policy_id, hat_id)
);

-- Timeline tasks
CREATE TABLE timeline_tasks (
  task_id TEXT PRIMARY KEY,
  policy_id TEXT,
  name TEXT,
  start_month INTEGER,
  duration_months INTEGER
);

-- Task dependencies
CREATE TABLE task_dependencies (
  task_id TEXT,
  depends_on_task_id TEXT,
  PRIMARY KEY(task_id, depends_on_task_id)
);

-- Policy dependencies (cross-policy feeds)
CREATE TABLE policy_dependencies (
  from_policy_id TEXT,
  to_policy_id TEXT,
  dep_type TEXT,
  lag_months INTEGER DEFAULT 0
);

-- Evaluation results
CREATE TABLE evaluator_results (
  policy_id TEXT PRIMARY KEY,
  mean_score REAL,
  min_score REAL,
  max_score REAL,
  recommendation TEXT
);
```

### **Neo4j Graph Model (Cypher)**

```cypher
-- Nodes
:Programme(id) — root Wales programme
:Policy(id) — the 3 policies
:Authority(name) — local authority (Cardiff, Swansea, Conwy)
:Harmonic(id) — 9 harmonics active in v28
:DeBonoHat(id) — 12 thinking hats
:BudgetLine(id) — budget items
:Task(id) — timeline tasks
:Domain(id) — policy domains

-- Relationships
(Programme)-[:FUNDS {amount, share_pct}]->(Policy)
(Policy)-[:IN_AUTHORITY]->(Authority)
(Policy)-[:ACTIVATES]->(Harmonic)
(Policy)-[:SCORED_BY {score}]->(DeBonoHat)
(Policy)-[:HAS_BUDGET_LINE]->(BudgetLine)
(Policy)-[:HAS_TASK]->(Task)
(Task)-[:PRECEDES]->(Task)
(Policy)-[:FEEDS {type, lag_months}]->(Policy)
```

---

## 🎩 De Bono Hat Scoring System

Each policy is evaluated across 12 cognitive lenses:

| Hat | Mode | Purpose | Cardiff Score | Swansea Score | Conwy Score |
|-----|------|---------|---|---|---|
| ⚪ **White** | Facts, data, evidence | Baseline reality check | 0.86 | 0.82 | 0.80 |
| 🔴 **Red** | Emotion, intuition, morale | Stakeholder buy-in | 0.74 | 0.78 | 0.88 |
| ⚫ **Black** | Risk, failure, critique | What can go wrong? | 0.72 | 0.76 | 0.79 |
| 🟡 **Yellow** | Benefit, upside, optimism | Best case | 0.91 | 0.89 | 0.86 |
| 🟢 **Green** | Creativity, alternatives | Novel approaches | 0.83 | 0.88 | 0.91 |
| 🔵 **Blue** | Process, control, gates | Governance & gates | 0.80 | 0.79 | 0.77 |
| 🟣 **Purple** | Strategic alignment | Fits into bigger picture | 0.88 | 0.86 | 0.84 |
| 🩷 **Pink** | Stakeholder empathy | Who cares? Who benefits? | 0.84 | 0.87 | 0.93 |
| 🟫 **Brown** | Heritage, precedent | Respects local roots | 0.78 | 0.77 | 0.92 |
| ⚙️ **Grey** | Uncertainty, unknowns | What don't we know? | 0.69 | 0.71 | 0.74 |
| 🟨 **Gold** | Value creation, synergy | Economic & social ROI | 0.90 | 0.93 | 0.87 |
| 🥈 **Silver** | Systems, networks | Emergent properties | 0.92 | 0.90 | 0.86 |

**Mean scores:**
- Cardiff: **0.82/1.00** → "scale with controls"
- Swansea: **0.83/1.00** → "scale with controls"
- Conwy: **0.85/1.00** → "scale with controls"

---

## 🧬 13 Welsh Harmonics Model

The policies activate these synergies:

| # | Harmonic | Icon | Description | Cardiff | Swansea | Conwy |
|---|----------|------|-------------|---------|---------|-------|
| 1 | Baseline intelligence | 🦉 | Known background | — | — | — |
| 2 | **Weak signal** | 🐭 | Early movement detection | — | ✅ | **PRIMARY** |
| 3 | **Hive learning** | 🐝 | Collective clubs/schools | **PRIMARY** | — | — |
| 4 | **Ant trails** | 🐜 | Skills pathways | ✅ | ✅ | ✅ |
| 5 | Flock care | 🐑 | Youth trust | — | — | — |
| 6 | Lone-wolf talent | 🐺 | Mavericks | — | — | — |
| 7 | **Team excellence** | 🦁 | Pods & collaboration | — | **PRIMARY** | ✅ |
| 8 | **Agrarian realism** | 🌾 | Land, food, ecology | — | — | ✅ |
| 9 | **Enterprise** | 🏭 | Jobs, exports, ownership | ✅ | **PRIMARY** | — |
| 10 | **SPACE capability** | 🛰️ | Astronomy, robotics | ✅ | — | — |
| 11 | **Resilience** | ��️ | Civil safety, cyber | — | — | ✅ |
| 12 | **Education** | 📚 | Learning ladder | **PRIMARY** | ✅ | — |
| 13 | **Edge-AI ethics** | 🤖 | Human-reviewed AI | ✅ | ✅ | — |

---

## 📜 Export Formats

### **1. SQL (ACID-compliant)**

```sql
-- Load into SQLite
sqlite3 my_db.sqlite3 < cymru_v28_policy_engine.sql

-- Query by policy
SELECT policy_id, title, scaled_allocation 
FROM policies 
WHERE authority = 'Cardiff';

-- Get hat scores for a policy
SELECT hat_id, score FROM hat_scores 
WHERE policy_id = 'CARDIFF_EDUCATION_DIGITAL_ARCH_001'
ORDER BY score DESC;

-- Timeline with dependencies
SELECT t.name, t.start_month, t.duration_months, d.depends_on_task_id
FROM timeline_tasks t
LEFT JOIN task_dependencies d ON t.task_id = d.task_id
WHERE t.policy_id = 'CARDIFF_EDUCATION_DIGITAL_ARCH_001'
ORDER BY t.start_month;
```

### **2. Cypher (Neo4j Graph)**

```cypher
-- Load into Neo4j
LOAD CSV FROM "file:///path/to/cymru_v28_policy_engine.cypher" AS line
...

-- Query: all policies and their budgets
MATCH (p:Programme)-[f:FUNDS]->(pol:Policy)
RETURN pol.title, f.amount, f.share_pct
ORDER BY f.amount DESC;

-- Query: policy dependency chain
MATCH (p1:Policy)-[dep:FEEDS]->(p2:Policy)
RETURN p1.title, dep.type, p2.title, dep.lag_months;

-- Query: all tasks for a policy with dependencies
MATCH (pol:Policy {id: 'CARDIFF_EDUCATION_DIGITAL_ARCH_001'})
      -[:HAS_TASK]->(t:Task)
OPTIONAL MATCH (t)-[:PRECEDES]->(next:Task)
RETURN t.name, t.start_month, t.duration_months, next.name;

-- Query: hat scores radar for comparison
MATCH (pol:Policy {id: 'CARDIFF_EDUCATION_DIGITAL_ARCH_001'})
      -[s:SCORED_BY]->(hat:DeBonoHat)
RETURN hat.name, hat.icon, s.score
ORDER BY s.score DESC;
```

### **3. JSON (Dynamic Dashboard)**

```json
{
  "metadata": {
    "id": "CYMRU_V28_POLICY_ENGINE",
    "version": "v28.1",
    "budget_total": 62500000000,
    "currency": "GBP",
    "stance": "civic, non-weaponised"
  },
  "policies": [
    {
      "id": "CARDIFF_EDUCATION_DIGITAL_ARCH_001",
      "title": "🏛️ Cardiff School-to-SPACE Digital Architecture Lab",
      "authority": "Cardiff",
      "pilot_budget": 1100000,
      "scaled_allocation": 22500000000,
      "allocation_share_pct": 36.0,
      "primary_harmonics": ["hive_learning", "ant_trails", "edge_ai", "space"],
      "hat_scores": {
        "white": 0.86,
        "silver": 0.92,
        ...
      }
    },
    ...
  ],
  "harmonics": [...],
  "dependencies": [
    {
      "from": "CARDIFF_EDUCATION_DIGITAL_ARCH_001",
      "to": "SWANSEA_APPRENTICE_TEAM_SANDBOX_002",
      "type": "feeds_skilled_learners",
      "lag_months": 12
    }
  ]
}
```

---

## 🔗 Policy Dependency Chain

```
Cardiff (Education)
    ↓ [feeds_skilled_learners, 12 months lag]
Swansea (Apprenticeships)
    ↓ [returns_products_and_enterprise_support, 9 months lag]
Conwy (Weak-Signal & Rural)

Conwy (Weak-Signal & Rural)
    ↓ [feeds_product_problems_to_apprentice_pods, 6 months lag]
Swansea (Apprenticeships)

Cardiff (Education)
    ↓ [shares_curriculum_and_teacher_capability, 6 months lag]
Conwy (Weak-Signal & Rural)
```

**Timeline:**
- Month 0–6: All three policies design phase
- Month 6–18: Cardiff labs pilot + Swansea pod recruitment
- Month 12–30: Cardiff feeds learners to Swansea
- Month 18+: Conwy scales weak-signal scanning
- Month 30+: Conwy feeds product problems to Swansea pods
- Month 60+: Spinouts and national replication

---

## 🎯 Governance & Decision Gates

Each policy has **gate review points**:

### **Cardiff Gates**

- 🚪 **Gate 1** (Month 3): Schools signed MOU? → Proceed
- 🚪 **Gate 2** (Month 6): 80% pilot attendance? → Full rollout
- 🚪 **Gate 3** (Month 12): 60% apprentice job placement? → Scale
- 🚪 **Gate 4** (Month 24): Social ROI ≥ 3:1? → Export model

### **Swansea Gates**

- 🚪 **Gate 1** (Month 6): Pod standard approved? → Recruit employers
- 🚪 **Gate 2** (Month 9): 60+ employers committed? → Launch wave 1
- 🚪 **Gate 3** (Month 18): 80% pod survival to month 6? → Wave 2
- 🚪 **Gate 4** (Month 30): 3+ spinouts funded? → National roll-out

### **Conwy Gates**

- 🚪 **Gate 1** (Month 6): 8 hubs operational? → Signal scanning
- 🚪 **Gate 2** (Month 12): 50+ farmer signals captured? → Curriculum adapt
- 🚪 **Gate 3** (Month 24): 5+ farm prototypes in testing? → Scale hub capacity
- 🚪 **Gate 4** (Month 36): 15% youth retention improvement? → Playbook export

---

## 🛡️ Scope & Safety Boundaries

**What this is:**
- ✅ Civic resilience, education, enterprise, SPACE capability planning
- ✅ Youth development and apprenticeship pathways
- ✅ Agricultural technology and rural development
- ✅ Health response, rescue readiness, cyber resilience
- ✅ Non-weaponised, human-reviewed decision support

**What this is NOT:**
- ❌ Weapons procurement or lethal capability design
- ❌ Combat operational planning
- ❌ Intelligence gathering for military purposes
- ❌ Surveillance or tracking systems
- ❌ Autonomous weapon systems

**Human review is mandatory at every decision gate.**

---

## 📈 Expected Outcomes (5-Year Horizon)

| Metric | Cardiff | Swansea | Conwy | Total |
|--------|---------|---------|-------|-------|
| **People trained** | 1,200/year | 240/year | 120/year | **1,560/year** |
| **Jobs created** | 120/year | 192/year | 60/year | **372/year** |
| **Apprentices** | 120/year | 240/year | 120/year | **480/year** |
| **New enterprises** | — | 8–12/year | 5–8/year | **13–20/year** |
| **Budget efficiency** | 6.2x ROI | 3.8x ROI | 7.4x ROI | **5.8x avg ROI** |
| **Youth retention** | +18% | — | +15% | **+33% net** |
| **Brain drain reversed** | — | 78% stay | 60% stay | **+138% net** |

---

## 🚢 Deployment Checklist

- [ ] Review budget allocations and policy summaries
- [ ] Load SQL schema into SQLite or PostgreSQL
- [ ] Import Cypher into Neo4j instance
- [ ] Deploy HTML5 dashboard to web server
- [ ] Set up Gantt and evaluator pages (PHP optional)
- [ ] Schedule gate review meetings (monthly for 24 months)
- [ ] Establish human review governance board
- [ ] Begin Month 0 design phase (Cardiff, Swansea, Conwy)
- [ ] Publish policy docs to gov.wales or local authority websites
- [ ] Train staff on weak-signal scanning and KPI tracking
- [ ] Begin public consultation (3–6 months)

---

## 🎓 How to Use This

### **For Policy Makers:**
1. Open the **HTML5 dashboard** in a browser
2. Adjust budget sliders to model scenarios
3. Review the **Gantt timeline** to see dependencies
4. Use the **De Bono evaluator** to stress-test against all 12 thinking hats
5. Export **SQL or Cypher** for integration into planning systems

### **For Data Analysts:**
1. Load the **SQLite database** into your analytics tool
2. Query by policy, authority, harmonic, or hat score
3. Generate custom reports and CSV exports
4. Track KPI progress against budgets

### **For Technology Teams:**
1. Import **Cypher into Neo4j** for graph-based analysis
2. Build custom dashboards querying the graph
3. Connect to power BI, Tableau, or Looker
4. Automate policy dependency tracking

### **For Academics:**
1. Study the **De Bono hat scoring methodology**
2. Analyze the **weak-signal intelligence model** as a civic application of predation ecology
3. Evaluate **policy interdependencies** and feedback loops
4. Model **alternative budget allocations** using the JSON structure

---

## 📚 Further Reading

- **De Bono, E.** (1985). *Six Thinking Hats*. Penguin.
- **Welsh Government.** (2024). *National resilience planning framework.*
- **Kotler, P.** (2020). *Marketing 5.0: Technology for humanity.*
- **Drucker, P.** (1993). *Managing for results.*
- **Mintzberg, H.** (1979). *The structuring of organisations.*

---

## 📞 Support & Questions

**For technical issues:**
- GitHub: `l00kingactual/agi-ai-mi-iid-ml`
- Issues: Tag `cymru-v28-policy-engine`

**For policy questions:**
- Welsh Government Cabinet Office
- Local authority partnerships (Cardiff, Swansea, Conwy)
- Medr (Skills Authority)

**For data/graph questions:**
- Neo4j support: https://neo4j.com/support
- SQLite documentation: https://sqlite.org/docs.html

---

## 🐉 Final Summary

**Cymru v28 Policy Engine** is a **live, audit-able, human-reviewed civic planning system** that:

1. **Mixes policies dynamically** — adjust budgets and watch outcomes change
2. **Scores against multiple thinking lenses** — not just one perspective
3. **Tracks dependencies** — when policy A succeeds, policy B can begin
4. **Exports everything** — SQL for databases, Cypher for graphs, JSON for dashboards
5. **Uses weak-signal intelligence** — detects opportunity early, adapts fast
6. **Stays non-weaponised** — explicitly excludes lethal or combat capabilities
7. **Requires human review** — every decision gate has governance oversight

**Motto:**

```
Cymru farms the future.
Cymru maps the land.
Cymru teaches the child.
Cymru launches the mind.
Cymru carries the hive beyond the horizon.

Ad infinitum, et ultra.

🐉 [o][o]
```

---

**Ready to deploy.** 🚀
