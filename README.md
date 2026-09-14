# Apple Support Agent 🍏🤖

An intelligent, production-ready AI customer support agent designed to classify incoming customer inquiries (tweets), provide empathetic self-service troubleshooting replies, evaluate urgency/frustration levels, and escalate critical issues to human specialists.

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
│   ├── preprocess.py                 # Text cleaning, normalization, Twitter handle removal
│   ├── classifier.py                 # Multi-class intent classification engine
│   ├── reply_generator.py            # Apple-styled conversational response generator
│   ├── escalation.py                 # Urgency, sentiment, and risk escalation rules
│   ├── evaluate.py                   # Benchmark & evaluation pipeline
│
│── results/
│   ├── metrics.json                  # Accuracy, macro F1, and class breakdown
│   ├── confusion_matrix.png          # Visual heatmap of classification results
│
│── requirements.txt                  # Python dependencies
│── README.md                         # Architecture & quickstart guide
```

---

## 🎯 Intents Covered

The classifier recognizes 8 distinct customer inquiry categories:

| Intent | Description | Example Query |
| :--- | :--- | :--- |
| `battery_issue` | Battery drain, overheating, charging problems | *"Battery dying in 2 hours on my iPhone 14 Pro since updating."* |
| `billing_subscription` | Charges, refunds, renewals, payment methods | *"I was charged $9.99 twice for Apple Music subscription."* |
| `icloud_sync` | Photos, drive, notes, sync pauses, storage | *"Photos not uploading to iCloud from my iPad Air 5."* |
| `hardware_defect` | Screens, buttons, microphone, physical damage | *"Screen on my iPhone 14 Pro has green vertical lines."* |
| `software_update` | Stuck updates, boot loops, error codes | *"Update stuck at 'Verifying Update' on iPhone 12."* |
| `airpods_audio` | ANC, crackling, microphone, pairing, charging case | *"Right AirPod Pro has buzzing static sound."* |
| `account_security` | Stolen devices, locked IDs, unauthorized access | *"Someone changed my Apple ID email and password! URGENT!"* |
| `general_inquiry` | Trade-in values, eSIM transfer, store appointments | *"How do I transfer eSIM from older iPhone to new iPhone 15?"* |

---

## ⚡ Escalation Engine

Customer tickets are dynamically scored and flagged for human intervention (`escalate = True`) based on:
1. **Security & Identity Hazards:** Locked Apple IDs, phishing reports, remote unauthorized charges, or stolen hardware.
2. **Device Safety:** Device overheating, battery swelling, or boot loop scenarios.
3. **Sentiment & Frustration:** Detection of angry phrasing, repeated failed contacts, or high-value charge discrepancies.

---

## 📊 Benchmark Results

Evaluated on the 200 hand-labelled `golden_set.csv`:

- **Intent Classification Accuracy:** `77.50%`
- **Macro Precision:** `86.73%`
- **Macro Recall:** `77.50%`
- **Macro F1 Score:** `78.70%`
- **Escalation Detection Accuracy:** `79.00%`

*Detailed per-class breakdown and confusion matrix available in `results/metrics.json` and `results/confusion_matrix.png`.*

---

## 🚀 Quickstart & Usage

### 1. Installation
```bash
cd apple-support-agent
pip install -r requirements.txt
```

### 2. Preprocess & Test Classification
```python
from src.preprocess import clean_tweet
from src.classifier import IntentClassifier
from src.escalation import EscalationEngine
from src.reply_generator import ReplyGenerator

text = "@AppleSupport I lost my iPhone at the airport, please blacklist IMEI immediately!"
cleaned = clean_tweet(text)

classifier = IntentClassifier()
intent = classifier.predict_one(text)

escalation = EscalationEngine().evaluate(text, intent["intent"])
reply = ReplyGenerator().generate_reply(text, intent["intent"], escalation)

print("Intent:", intent["intent"])
print("Escalation:", escalation["escalate"], f"({escalation['urgency']} urgency)")
print("Response:", reply)
```

### 3. Run Benchmark Pipeline
```bash
python -m src.evaluate
```
