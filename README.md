# Apple Support Agent 🍏🤖

An intelligent, production-ready AI customer support agent designed to classify incoming customer inquiries (tweets), provide empathetic self-service troubleshooting replies, evaluate urgency/frustration levels, and escalate critical issues to human specialists.

---

## 📚 Dataset Citation

This project utilizes real-world customer support patterns and subsamples derived from:
- **Dataset Title**: Customer Support on Twitter — BERD Platform
- **Authors**: Axelbrooke, Stuart (2017)
- **Official Citation & URL**: [https://berd-platform.de/records/4c9xb-k5q03](https://berd-platform.de/records/4c9xb-k5q03)
- **Description**: A public dataset of 3+ million tweets and replies across top brands on Twitter, capturing authentic customer phrasing, frustration, and technical support interactions.

---

## ⚡ Run Instructions

The entire end-to-end pipeline executes in **under 15 minutes**:

### 1. Clone Repository & Setup
```bash
git clone https://github.com/manoj-sb/apple-support-agent.git
cd apple-support-agent
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
# or for Node runtime tools
npm install
```

### 3. Run Notebooks
- Launch Jupyter:
  ```bash
  jupyter notebook notebooks/intent_model.ipynb
  ```
- Or run the baseline notebook:
  ```bash
  jupyter notebook notebooks/intent_baseline.ipynb
  ```

### 4. Run Automated Evaluation & Tests
```bash
# Run Python evaluation pipeline (generates metrics.json and confusion matrix)
python -m src.evaluate

# Run automated test suite
npm test
```

### 5. Interactive CLI & Live Web Dashboard
```bash
# Interactive CLI mode:
node cli.js

# Launch Web Dashboard at http://localhost:3000:
npm start
```

---

## 📊 Summary of Results

Evaluated against the curated 200-sample hand-labelled `golden_set.csv`:

| Metric | Score |
| :--- | :--- |
| **Intent Classification Accuracy** | **77.50%** |
| **Intent Macro Precision** | **86.73%** |
| **Intent Macro Recall** | **77.50%** |
| **Intent Macro F1 Score** | **78.70%** |
| **Escalation Detection Accuracy** | **79.00%** |
| **Escalation Precision** | **100.00%** |

Full metrics breakdown by class is stored in [`results/metrics.json`](results/metrics.json) and visualized in [`results/confusion_matrix.png`](results/confusion_matrix.png).

---

## 🔍 Links to Optional Polish & Deep Dives

- **[Failure Analysis](results/failure_analysis.md)**: In-depth analysis of 5 real misclassifications, detailing lexical overlap, root causes, and architectural mitigations.
- **[The Misleading Number](results/misleading_number.md)**: Critical evaluation of why headline accuracy (77.5%) is deceptive in production support environments, emphasizing cost-asymmetry in false negatives and the necessity of high recall for escalation.
- **[Decision Log](results/decision_log.md)**: Comprehensive log of 10 architectural, linguistic, and engineering decisions made during development.

---

## 📁 Repository Structure

```text
apple-support-agent/
│── data/
│   ├── raw/
│   │   └── apple_tweets_sample.csv   # Subsampled raw inbound Apple tweets
│   ├── golden_set.csv                # 200 hand-labelled evaluation samples
│
│── notebooks/
│   ├── intent_baseline.ipynb         # TF-IDF + Logistic Regression baseline
│   ├── intent_model.ipynb            # Advanced model evaluation & confusion matrix
│
│── src/
│   ├── __init__.py
│   ├── preprocess.py                 # Text cleaning, normalization, Twitter handle removal
│   ├── classifier.py                 # Multi-class intent classification engine
│   ├── reply_generator.py            # Apple-styled conversational response generator
│   ├── escalation.py                 # Urgency, sentiment, and risk escalation rules
│   ├── evaluate.py                   # Benchmark & evaluation pipeline
│
│── test/
│   └── test_agent.js                 # Automated unit tests (100% passing)
│
│── results/
│   ├── metrics.json                  # Accuracy, macro F1, and class breakdown
│   ├── confusion_matrix.png          # Visual heatmap of classification results
│   ├── failure_analysis.md           # 3–5 misclassifications explained
│   ├── misleading_number.md          # Headline metric + limitations analysis
│   ├── decision_log.md               # 10 architecture & modeling choices documented
│
│── cli.js                            # Interactive command-line agent tool
│── server.js                         # Web UI dashboard with live inference
│── package.json                      # Scripts & project metadata
│── requirements.txt                  # Python dependencies
│── README.md                         # Complete documentation
│── submission.txt                    # GitHub link + email to Hiver
```
