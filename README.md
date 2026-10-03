# 🛡️ Network Intrusion Detection System (NIDS)

A machine learning-based network intrusion detection system trained on the CIC-IDS-2017 dataset. Detects malicious network traffic in real time using flow-based feature extraction and a Random Forest classifier — with a live Streamlit dashboard for alerts and monitoring.

---

## 📌 Project status

| Phase | Stack | Status |
|-------|-------|--------|
| Phase 1 | Python · Scapy · Scikit-learn · Streamlit · SQLite | ✅ Active |
| Phase 2 | React · Node.js · Express · Socket.io | 🔜 Planned |

> Phase 2 will upgrade the dashboard to a React + Node.js frontend with WebSocket-based real-time alerts. The entire `ml-engine/` will remain unchanged.

---

## 🧠 How it works

```
Network traffic
      │
      ▼
 Scapy sniffer          ← captures raw packets
      │
      ▼
 Flow aggregator        ← groups packets by 5-tuple (src IP, dst IP, src port, dst port, protocol)
      │
      ▼
 Feature extraction     ← computes 80 CICFlowMeter-compatible flow statistics
      │
      ▼
 Random Forest model    ← predict_proba() → attack probability
      │
      ▼
 SQLite alerts.db       ← stores alerts above threshold (default: 0.7)
      │
      ▼
 Streamlit dashboard    ← live alert table, traffic chart, model stats
```

---

## 📁 Project structure

```
nids-project/
├── ml-engine/                  # Python ML service (standalone process)
│   ├── data/                   # CIC-IDS-2017 CSVs (git-ignored, see data/README.md)
│   ├── notebooks/
│   │   ├── 01_eda.ipynb        # Exploratory data analysis
│   │   └── 02_train.ipynb      # Model training experiments
│   ├── src/
│   │   ├── preprocessor.py     # Data loading and cleaning
│   │   ├── train.py            # Training script (run once)
│   │   ├── flow_aggregator.py  # Packet → flow feature extraction
│   │   ├── sniffer.py          # Live capture + inference entry point
│   │   └── db_writer.py        # SQLite write helper
│   ├── models/                 # Saved model files (git-ignored)
│   │   ├── rf_model.pkl
│   │   ├── feature_list.json
│   │   └── metrics.json
│   └── requirements.txt
│
├── dashboard/                  # Streamlit dashboard (Phase 1)
│   ├── app.py                  # Entire dashboard (~80 lines)
│   └── requirements.txt
│
├── shared/
│   └── alerts.db               # SQLite bridge (git-ignored)
│
├── .env.example                # Environment variable template
├── .gitignore
└── README.md
```

---

## 📊 Dataset

This project uses the **CIC-IDS-2017** dataset published by the Canadian Institute for Cybersecurity.

- **Source:** https://www.unb.ca/cic/datasets/ids-2017.html
- **Size:** ~450 MB (8 CSV files)
- **Traffic types:** BENIGN + 14 attack categories

| Attack type | Examples |
|-------------|---------|
| DoS | Slowloris, Slowhttptest, Hulk, GoldenEye |
| DDoS | UDP/TCP flood |
| Brute Force | SSH, FTP |
| Web Attacks | SQL Injection, XSS |
| Other | Port Scan, Botnet, Infiltration |

> Dataset files are not included in this repo. See [`ml-engine/data/README.md`](ml-engine/data/README.md) for download instructions.

---

## ⚙️ Setup

### Prerequisites

- Python 3.10+
- `sudo` / root access (required for Scapy packet capture)

### 1. Clone the repo

```bash
git clone https://github.com/Sahil-Bhardwaj/nids-project.git
cd nids-project
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your network interface name and paths
```

### 3. Install dependencies

```bash
# ML engine
cd ml-engine
pip install -r requirements.txt

# Dashboard
cd ../dashboard
pip install -r requirements.txt
```

### 4. Download the dataset

Follow instructions in [`ml-engine/data/README.md`](ml-engine/data/README.md) to download and place the 8 CSV files.

### 5. Train the model

```bash
cd ml-engine
python src/train.py
# Saves model to models/rf_model.pkl
# Saves feature list to models/feature_list.json
# Saves metrics to models/metrics.json
```

---

## 🚀 Running the system

Open two terminals:

**Terminal 1 — ML engine (requires sudo for Scapy)**
```bash
cd ml-engine
sudo python src/sniffer.py
```

**Terminal 2 — Streamlit dashboard**
```bash
cd dashboard
streamlit run app.py
# Opens at http://localhost:8501
```

The dashboard polls `shared/alerts.db` every 3 seconds and updates automatically.

---

## 📈 Model performance

Evaluated on a stratified 80/20 train-test split of the full CIC-IDS-2017 dataset.

| Metric | Benign | Attack (macro avg) |
|--------|--------|--------------------|
| Precision | ~0.98 | ~0.97 |
| Recall | ~0.97 | ~0.96 |
| F1 Score | ~0.97 | ~0.96 |

> Accuracy alone is misleading on this dataset (~80% benign traffic). F1 score and recall on the attack class are the metrics that matter.

Two models were evaluated:

| Model | F1 (attack) | Train time | Notes |
|-------|-------------|------------|-------|
| Random Forest | 0.965 | ~3 min | Interpretable, robust — **primary model** |
| XGBoost | 0.971 | ~8 min | Marginally better, more tuning required |

---

## 🔧 Configuration

All configuration lives in `.env`:

```env
DB_PATH=../shared/alerts.db     # Path to SQLite database
IFACE=eth0                      # Network interface to sniff
THRESHOLD=0.7                   # Minimum attack probability to trigger alert
OUTPUT_MODE=sqlite              # sqlite (Phase 1) | http (Phase 2)
REFRESH_SECS=3                  # Dashboard refresh interval
```

---

## 🗺️ Roadmap

- [x] Exploratory data analysis and preprocessing
- [x] Model training — Random Forest and XGBoost
- [x] Flow aggregator — packet to feature extraction
- [x] Live inference pipeline
- [x] Streamlit dashboard with real-time alerts
- [ ] React + Node.js frontend with WebSocket (Phase 2)
- [ ] Per-alert SHAP explanations
- [ ] Anomaly detection layer for zero-day detection
- [ ] Docker Compose for one-command startup

---

## 🧱 Design decisions

**Why Random Forest over a neural network?**
Random Forest produces feature importances natively, making every prediction explainable. In security contexts, a SOC analyst needs to understand *why* a flow was flagged — black-box models are hard to justify. RF also trains in minutes on tabular data with minimal hyperparameter tuning.

**Why flow-based detection instead of deep packet inspection?**
Flow-based detection works on encrypted traffic, requires no payload access (no privacy concerns), and is computationally efficient. DPI fails on TLS and is slow at scale. The tradeoff is that payload-level attacks inside HTTPS are not directly detectable from flow statistics alone.

**Why SQLite as the Python–dashboard bridge?**
Both processes are Python running on the same machine. SQLite requires zero infrastructure and lets the sniffer write alerts while the dashboard reads them independently. In production, this would be replaced with a message queue like Redis or Kafka. Switching is a one-line change in `db_writer.py`.

**Why Streamlit for Phase 1?**
Streamlit reduces dashboard development from ~3 days to ~3 hours, allowing focus to stay on the ML pipeline. The entire frontend can be replaced in Phase 2 without touching any ML code — the SQLite schema and `OUTPUT_MODE` env var are designed for this upgrade.

---

## ⚠️ Limitations

- Model trained on 2017 traffic patterns — modern attack signatures may differ
- Supervised model cannot detect zero-day (unseen) attacks
- Adversarial attackers can shape traffic to mimic benign flow statistics
- Feature extraction latency adds a small delay before a flow is classified
- Single-machine deployment only in Phase 1 (SQLite is not networked)

---

## 📚 References

- Sharafaldin, I., Lashkari, A. H., & Ghorbani, A. A. (2018). *Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization.* ICISSP.
- Panigrahi, R., & Borah, S. (2018). *A Detailed Analysis of CICIDS2017 Dataset for Designing Intrusion Detection Systems. International Journal of Engineering & Technology, 7(3.24), 479–482.*
- [CICFlowMeter](https://github.com/iscx/CICFlowMeter) — feature extraction tool used to generate the dataset
- [Scapy documentation](https://scapy.readthedocs.io/)
- [Streamlit documentation](https://docs.streamlit.io/)

---

*Built as a summer internship project. Feedback and contributions welcome.*