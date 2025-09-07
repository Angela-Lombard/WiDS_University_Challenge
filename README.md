<p align="center">
  <img src="https://www.widsworldwide.org/wp-content/uploads/2023/05/WiDS_logo_nav.png" alt="WiDS Logo" width="250"/>
</p>

<h1 align="center">WiDS University Datathon 2025 – Student Starter Template</h1>

Welcome! This repository is your **starter workspace** for the WiDS University Datathon 2025.
It includes:

* **Tutorial to Join External Data:** uses smaller data set to learn how to join outside data sources.
* Two Sample Approaches: **Google Colab** or **Python Scripts**
* Code for fetching **external data** (NOAA daily weather & OSM infrastructure)
* Example Slides & Research Paper for **Final Report**
* Rubric, General Guidlines & Instructions Included

---

## Tracks

### 🔹 Track 1: Accelerating Equitable Evacuations

**Core question:** How can we reduce delays in evacuation alerts and improve response times for the communities most at risk?

**Scope & goals:** Turn WatchDuty data into a working, testable solution that shortens alert lag, improves clarity, and raises completion rates among vulnerable groups.

**Expected outputs:**

* Prototype or clickable mockup + short demo
* Notebook with reproducible logic
* User story and decision pathway

**Impact metrics:**

* Minutes of lead time gained
* Share of high-need households reached in first notification window
* Reduction in message ambiguity (e.g. comprehension test)
* Evidence the approach transfers to another region without major rework

---

### 🔹 Track 2: Designing for Economic Resilience

**Core question:** How can wildfire disruption analytics inform stronger economic safety nets for workers, families, and small businesses?

**Scope & goals:** Use WatchDuty data to reduce income shocks and speed recovery by quantifying disruption, identifying who is most affected, and proposing supports.

**Expected outputs:**

* Prototype or clickable mockup + short demo
* Notebook with reproducible logic
* Policy/program brief with eligibility rules, budgets, and targeting approach

**Impact metrics:**

* Estimated workdays preserved and wages protected
* Share of benefits reaching high-vulnerability groups
* Time from incident to benefit delivery
* Benefit-to-cost ratio for a realistic scenario

---

## 📂 File Structure

```plaintext
├─ README.md                    # This file
├─ starter_notebook.ipynb       # Main Colab notebook (NOAA + OSM joins)
├─ requirements.txt             # Run: pip instal -r requirements.txt
├─ .env.example                 # change file name to .env and put NOAA API key here
├─ data/
│  └─ examples/                 # Tiny sample CSVs (5 rows each)
│    ├─ perimeter_sample.csv    # Example Dataset 1 - will be changed with larger dataset later
│    └─ geo_events_sample.csv   # Example Dataset 2 - will be changed with larger dataset later
├─ scripts/
│  ├─ common.py                 # shared helpers (paths, EWKT, retry session)
│  ├─ noaa_daily_join.py        # NOAA weather - fetch & join
│  └─ osm_infrastructure.py     # OSM infrastructure - fetch & join
└─ docs/
   ├─ walkthrough_images        # Images used for tuturial
   └─ submission_checklist.md   # Kaggle writeup requirements
```

---

## Getting Started
There are two ways to get started with this template, depending on whether you want to work in **Colab** or on your own machine.

### Option 1: Use Google Colab
1. **Download the small example datasets** (first 5 rows of the real WatchDuty data):
- [`perimeter_sample.csv`](https://github.com/WiDSWorldwide/wids-datathon-university-template/blob/main/data/examples/perimeter_sample.csv)
- [`geo_events_sample.csv`](https://github.com/WiDSWorldwide/wids-datathon-university-template/blob/main/data/examples/geo_events_sample.csv)

These act as a practice dataset to learn how to connect external datasets (NOAA, OSM) to the WatchDuty dataset.

2. **Open the Colab notebook** 

<p align="left">
  <a href="https://colab.research.google.com/github/WiDSWorldwide/wids-datathon-university-template/blob/main/starter_notebook.ipynb">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
  </a>
</p>

3. **Upload the sample CSVs** to Colab’s temporary storage (left-hand sidebar under *Files*).

![Upload sample CSVs to Colab](docs/walk_thru_images/colab_upload.png)

4. Run the notebook cells to practice NOAA + OSM joins against the sample data set.

---

### Option 2: Run locally in your IDE
1. **Fork this repository** on GitHub.  

2. **Clone your fork**:
```
git clone https://github.com/YOUR-USERNAME/wids-datathon-university-template.git
cd wids-datathon-university-template
```
3. **Ensure you have Python 3.10+** and install requirements:
```
pip install -r requirements.txt
```
4. **Run the scripts directly:**
```
python scripts/noaa_daily_join.py --help
python scripts/osm_infrastructure.py --help
```
---

## Notebook vs Scripts

* The **Colab notebook** (`starter_notebook.ipynb`) is the **main entry point**.
  It runs **joins** (NOAA + OSM) on the small sample datasets.

* The **scripts/** folder contains the **same code as the notebook**, packaged
  as standalone `.py` files so you can run them locally.

---

## Scale up with full data
When you are ready to move beyond the sample dataset download full WatchDuty CSVs from Kaggle:

[WiDS University Datathon 2025 Competition Page](https://www.kaggle.com/competitions/wids-university-datathon-2025)

Place them under data/ and update file paths in the notebook or scripts.

---

## Deliverables (Hackathon Writeup)

All submissions must include:

* **Public Kaggle Notebook** with reproducible code
* **Demo Artifact** (≤3 min video or clickable mockup)
* **Writeup** (clear narrative, methods, results, impact)
* **Links** to GitHub repo and slide deck

---

## Scoring Rubric (100 points)

* **Narrative Quality (20 pts):** Clear, concise, well-structured; notebooks documented with markdown
* **Data-Driven Justification (30 pts):** Effective use of WatchDuty; transparent, reproducible analysis
* **Solution Impact (30 pts):** Tangible, real-world effect aligned to chosen track
* **Novelty & Creativity (20 pts):** Originality in approach and demo artifacts

---

## What Success Looks Like

* **Track 1 (Evacuations):** measurable lead-time gains, clearer warning language, better reach to high-need households
* **Track 2 (Economic):** quantifiable workdays preserved, wages protected, stronger safety-net targeting
* **Both:** practical, equity-focused, reproducible, transferable beyond one region/dataset

---

## 📩 Questions?

* WiDS Community: [https://community.widsworldwide.org](https://community.widsworldwide.org)
