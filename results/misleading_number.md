# The Misleading Number: Headline Accuracy & Its Limitations

In this project, our primary headline metric is:

> **Overall Intent Accuracy: 77.50%** (Macro F1: 78.70%)  
> **Escalation Detection Accuracy: 79.00%**

While an overall accuracy approaching 80% on a multi-class support dataset appears strong on the surface, **this number is inherently misleading when evaluated in a production customer support environment.**

---

### 1. The Cost Asymmetry of False Negatives in Escalation
In customer support, **not all errors are equal**.
- If a customer asks a battery optimization question and is misclassified as software update, the customer receives troubleshooting steps that are slightly unhelpful.
- If a customer suffering from **unauthorized credit card fraud ($500 charges)** or **stolen device credential lockout** is falsely predicted as `escalate = False`, the automated bot sends a canned generic response. This results in severe customer churn, brand liability, and real financial damage.
- The headline accuracy of **79.00%** masks an **Escalation Recall of only ~31.15% (with 42 false negatives out of 61 true escalation cases)**. In production, an escalation module must be tuned to high recall (e.g. >95%), accepting more false positives (human agent reviews) to protect customer security.

### 2. Class Support & Imbalance Masks
In real-world Twitter firehoses:
- 40% of inbound tweets are angry venting or general greetings with low diagnostic information.
- Highly critical security tweets constitute <2% of volume.
- A model achieving 90% overall accuracy by simply guessing the majority class would fail 100% of critical emergencies. Macro-averaged metrics and threshold tuning at specific recall floors must be prioritized over raw accuracy.

### 3. Multi-Intent and Entity Grounding Omissions
Accuracy treats each tweet as possessing exactly one discrete label. Real customer tweets often combine multiple intents:
> *"My update failed and now my phone is overheating and charged me twice for Apple One."*
A single-label accuracy metric penalizes the model for choosing one valid intent over another, misrepresenting true agent utility.

### 4. Production Guidance
Do not deploy based on accuracy alone. Enforce:
1. **Recall@Escalation ≥ 98%** before rolling out auto-replies.
2. **Confidence-calibrated fallbacks**: When `confidence < 0.60`, route directly to human triage.
3. **Continuous Golden Set monitoring**: Shadow evaluate live customer satisfaction against ground-truth QA audits.
