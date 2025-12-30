import json
import os

def run_evaluation(log_path="logs/steered_activations.jsonl"):
    """
    Implements PRD Section 5.4: SAE-Based Evaluation.
    Calculates activation statistics from generated logs.
    """
    if not os.path.exists(log_path):
        print(f"Error: Log file {log_path} not found. Run generate first.")
        return

    metrics = {
        "identity": {"vals": [], "threshold": 0.5},
        "landmark": {"vals": [], "threshold": 0.3}
    }

    with open(log_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                data = json.loads(line)
                if "identity_activation" in data:
                    metrics["identity"]["vals"].append(data["identity_activation"])
                if "landmark_activation" in data:
                    metrics["landmark"]["vals"].append(data["landmark_activation"])
            except json.JSONDecodeError:
                continue


    print("--- DUAL-LAYER SAE EVALUATION REPORT ---")
    for name, m in metrics.items():
        if not m["vals"]:
            print(f"No {name} activations found in log.")
            continue
        avg = sum(m["vals"]) / len(m["vals"])
        recall = len([v for v in m["vals"] if v > m["threshold"]]) / len(m["vals"])
        print(f"[{name.upper()}] Avg Act: {avg:.4f} | Recall (T>{m['threshold']}): {recall*100:.1f}%")
    print("-----------------------------------------")


if __name__ == "__main__":
    run_evaluation()
