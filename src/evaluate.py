"""
evaluate.py
Evaluation script to benchmark intent classification and escalation accuracy
on the 200 hand-labelled golden set.
Generates metrics.json and confusion matrix representation.
"""

import csv
import json
import os
from collections import defaultdict
from typing import Dict, List, Tuple

from src.classifier import IntentClassifier
from src.escalation import EscalationEngine
from src.reply_generator import ReplyGenerator


def load_golden_set(filepath: str) -> List[Dict[str, str]]:
    rows = []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def calculate_metrics(y_true: List[str], y_pred: List[str], classes: List[str]):
    """Calculate accuracy, macro precision, recall, and F1 score."""
    total = len(y_true)
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    accuracy = correct / total if total > 0 else 0.0

    class_metrics = {}
    macro_p, macro_r, macro_f1 = 0.0, 0.0, 0.0

    for cls in classes:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p == cls)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != cls and p == cls)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p != cls)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        class_metrics[cls] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "support": sum(1 for t in y_true if t == cls)
        }
        macro_p += prec
        macro_r += rec
        macro_f1 += f1

    num_classes = len(classes)
    return {
        "accuracy": round(accuracy, 4),
        "macro_precision": round(macro_p / num_classes, 4),
        "macro_recall": round(macro_r / num_classes, 4),
        "macro_f1": round(macro_f1 / num_classes, 4),
        "class_breakdown": class_metrics
    }


def build_confusion_matrix(y_true: List[str], y_pred: List[str], classes: List[str]):
    matrix = {c_true: {c_pred: 0 for c_pred in classes} for c_true in classes}
    for t, p in zip(y_true, y_pred):
        if t in matrix and p in matrix[t]:
            matrix[t][p] += 1
    return matrix


def render_confusion_matrix_ascii(matrix: Dict[str, Dict[str, int]], classes: List[str]) -> str:
    lines = []
    header = f"{'True v / Pred >':<22}" + "".join([f"{c[:8]:>10}" for c in classes])
    lines.append(header)
    lines.append("-" * len(header))
    for t in classes:
        row_str = f"{t:<22}" + "".join([f"{matrix[t][p]:>10}" for p in classes])
        lines.append(row_str)
    return "\n".join(lines)


def run_evaluation():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    golden_file = os.path.join(base_dir, 'data', 'golden_set.csv')
    results_dir = os.path.join(base_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    print(f"Loading golden set from {golden_file}...")
    dataset = load_golden_set(golden_file)
    print(f"Loaded {len(dataset)} examples.")

    classifier = IntentClassifier()
    escalation_engine = EscalationEngine()
    reply_gen = ReplyGenerator()

    # Intent Evaluation
    y_true_intent = [d['intent'] for d in dataset]
    y_pred_intent = [classifier.predict_one(d['text'])['intent'] for d in dataset]
    classes = list(set(y_true_intent))
    classes.sort()

    intent_metrics = calculate_metrics(y_true_intent, y_pred_intent, classes)
    conf_matrix = build_confusion_matrix(y_true_intent, y_pred_intent, classes)

    # Escalation Evaluation
    y_true_esc = [d['escalate'].lower() == 'true' for d in dataset]
    y_pred_esc = []
    for d, pred_intent in zip(dataset, y_pred_intent):
        esc_res = escalation_engine.evaluate(d['text'], pred_intent)
        y_pred_esc.append(esc_res['escalate'])

    esc_classes = ["False", "True"]
    esc_metrics = calculate_metrics(
        [str(x) for x in y_true_esc],
        [str(x) for x in y_pred_esc],
        esc_classes
    )

    combined_results = {
        "dataset_size": len(dataset),
        "intent_classification": intent_metrics,
        "escalation_detection": esc_metrics,
        "confusion_matrix": conf_matrix
    }

    # Save metrics.json
    metrics_path = os.path.join(results_dir, 'metrics.json')
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(combined_results, f, indent=2)
    print(f"Saved evaluation metrics to {metrics_path}")

    # Print summary & ASCII confusion matrix
    print("\n=== INTENT CLASSIFICATION METRICS ===")
    print(f"Accuracy:  {intent_metrics['accuracy']:.4f}")
    print(f"Macro F1:  {intent_metrics['macro_f1']:.4f}")
    print("\nConfusion Matrix:")
    print(render_confusion_matrix_ascii(conf_matrix, classes))

    print("\n=== ESCALATION METRICS ===")
    print(f"Accuracy:  {esc_metrics['accuracy']:.4f}")
    print(f"Macro F1:  {esc_metrics['macro_f1']:.4f}")


if __name__ == "__main__":
    run_evaluation()
