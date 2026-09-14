# Failure Analysis: Intent Misclassifications

This document examines 5 concrete misclassifications from the evaluation of the intent classification model on the 200 hand-labelled golden set. Each case breaks down the input text, expected label, predicted label, root cause, and engineering mitigation.

---

### Case 1: Overlapping Hardware & AirPods Audio
- **Tweet**: `"@AppleSupport left AirPod won't connect or show battery percentage in popup widget."`
- **True Intent**: `airpods_audio`
- **Predicted Intent**: `battery_issue`
- **Root Cause**: The tweet contains strong lexical indicators for battery (`"battery percentage"`) alongside AirPods mentions. The bag-of-words / TF-IDF weights gave equal or higher priority to `"battery"` than the product context `"airpod"`.
- **Mitigation**: Introduce hierarchical classification or entity-aware feature weighting where device product identifiers (e.g., AirPods, Watch, Mac) act as prior context masks, or use contextual transformer embeddings (e.g. `RoBERTa-base` fine-tuned on customer support conversations).

---

### Case 2: Account Security vs. Hardware Theft Confusion
- **Tweet**: `"@AppleSupport Lost my phone and Find My was disabled by thief. Please secure my account!"`
- **True Intent**: `account_security`
- **Predicted Intent**: `hardware_defect`
- **Root Cause**: The occurrence of `"phone"` and lack of explicit Apple ID phrasing led the model away from account recovery, while the device term slightly biased it towards general hardware/device issues.
- **Mitigation**: Add n-gram feature expansion for security-specific phrases like `"find my disabled"`, `"secure my account"`, and `"thief"` to the security lexicon, and train multi-intent models that flag cross-cutting concerns.

---

### Case 3: Software Update Triggering Hardware Bootloop False Positive
- **Tweet**: `"@AppleSupport iPhone stuck in boot loop showing Apple logo after system update."`
- **True Intent**: `software_update`
- **Predicted Intent**: `hardware_defect`
- **Root Cause**: `"boot loop"` and `"apple logo"` are frequently associated with hardware motherboard/logic board failures in customer vocabulary, despite being caused directly by an OS software update.
- **Mitigation**: Implement temporal / causal dependency detection (e.g., `"after system update"`, `"post-update"`) so symptoms following an update trigger are routed primarily to the software recovery playbook before escalating to in-store hardware diagnostics.

---

### Case 4: Subscription Renewal vs. General Inquiry
- **Tweet**: `"@AppleSupport Where can I view all active subscriptions linked to my Apple ID?"`
- **True Intent**: `billing_subscription`
- **Predicted Intent**: `account_security`
- **Root Cause**: The phrase `"Apple ID"` strongly activated the security intent, overwhelming the informational billing keyword `"subscriptions"`.
- **Mitigation**: Disambiguate queries containing `"Apple ID"` when paired with non-critical verbs like `"view"`, `"linked to"`, or `"subscriptions"` through negative constraint weights or calibrated intent thresholds.

---

### Case 5: Trade-in Device Condition Ambiguity
- **Tweet**: `"@AppleSupport Can I trade in my cracked iPad for the latest M4 iPad Pro in store directly?"`
- **True Intent**: `general_inquiry`
- **Predicted Intent**: `hardware_defect`
- **Root Cause**: The presence of physical damage terms (`"cracked"`) immediately triggered the hardware defect rule/weights, ignoring the intent verb (`"trade in"`).
- **Mitigation**: Intent syntax parsing: treat transactional intents (`trade in`, `purchase`, `warranty`) as primary intent drivers, and physical descriptors as secondary metadata for trade-in valuation rather than repair requests.
