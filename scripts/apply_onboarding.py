import json, os, sys
from copy import deepcopy
from datetime import datetime

def deep_merge(base, updates):
    """Merge updates into base, tracking what changed."""
    changes = []
    result = deepcopy(base)
    
    for key, new_val in updates.items():
        if new_val is None:
            continue
        old_val = base.get(key)
        if old_val != new_val:
            changes.append({
                "field": key,
                "old": old_val,
                "new": new_val,
                "reason": "confirmed in onboarding call"
            })
            result[key] = new_val
    
    return result, changes

def apply_onboarding(v1_memo_path, onboarding_memo_path, v2_output_dir):
    with open(v1_memo_path) as f:
        v1 = json.load(f)
    with open(onboarding_memo_path) as f:
        onboarding = json.load(f)

    v2, changes = deep_merge(v1, onboarding)
    v2["version"] = "v2"
    v2["source"] = "onboarding_call"

    os.makedirs(v2_output_dir, exist_ok=True)
    
    # Save v2 memo
    with open(f"{v2_output_dir}/account_memo.json", "w") as f:
        json.dump(v2, f, indent=2)

    # Save changelog
    changelog = {
        "updated_at": datetime.now().isoformat(),
        "changes": changes,
        "summary": f"{len(changes)} field(s) updated from onboarding call"
    }
    with open(f"{v2_output_dir}/changes.json", "w") as f:
        json.dump(changelog, f, indent=2)

    # Also write human-readable changes.md
    with open(f"{v2_output_dir}/changes.md", "w") as f:
        f.write(f"# Changelog: v1 -> v2\n\n")
        f.write(f"**Updated:** {changelog['updated_at']}\n\n")
        for c in changes:
            f.write(f"### `{c['field']}`\n")
            f.write(f"- **Before:** `{c['old']}`\n")
            f.write(f"- **After:** `{c['new']}`\n")
            f.write(f"- **Reason:** {c['reason']}\n\n")

    print(f"✅ v2 saved. {len(changes)} changes logged.")
    return v2, changes

if __name__ == "__main__":
    apply_onboarding(sys.argv[1], sys.argv[2], sys.argv[3])