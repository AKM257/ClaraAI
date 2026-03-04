import os, json, re
from groq import Groq
from dotenv import load_dotenv
from generate_agent_spec import generate_agent_spec
from apply_onboarding import apply_onboarding

load_dotenv()

DEMO_DIR = "dataset/demo_calls"
ONBOARDING_DIR = "dataset/onboarding_calls"
OUTPUTS_DIR = "outputs/accounts"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_memo(transcript_path, output_dir):
    with open("prompts/extract_demo.txt") as f:
        prompt_template = f.read()
    with open(transcript_path, encoding="utf-8") as f:
        transcript = f.read()

    prompt = prompt_template.replace("{{TRANSCRIPT}}", transcript)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()

    memo = json.loads(raw)

    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/account_memo.json", "w", encoding="utf-8") as f:
        json.dump(memo, f, indent=2)

    print(f"  ✅ Memo saved: {output_dir}/account_memo.json")
    return memo

def run_pipeline_a():
    print("\n=== PIPELINE A: Demo Calls -> v1 ===\n")
    for fname in os.listdir(DEMO_DIR):
        if not fname.endswith(".txt"):
            continue
        account_id = fname.replace(".txt", "").replace(" ", "_").lower()
        transcript_path = os.path.join(DEMO_DIR, fname)
        output_dir = os.path.join(OUTPUTS_DIR, account_id, "v1")

        print(f"🔄 Processing: {fname}")
        memo = extract_memo(transcript_path, output_dir)
        generate_agent_spec(f"{output_dir}/account_memo.json", output_dir, "v1")
        print(f"  ✅ v1 complete for {account_id}\n")

def run_pipeline_b():
    print("\n=== PIPELINE B: Onboarding Calls -> v2 ===\n")
    for fname in os.listdir(ONBOARDING_DIR):
        if not fname.endswith(".txt"):
            continue
        account_id = fname.replace(".txt", "").replace(" ", "_").lower()
        onboarding_path = os.path.join(ONBOARDING_DIR, fname)
        v1_dir = os.path.join(OUTPUTS_DIR, account_id, "v1")
        v2_dir = os.path.join(OUTPUTS_DIR, account_id, "v2")

        if not os.path.exists(f"{v1_dir}/account_memo.json"):
            print(f"⚠️  No v1 found for {account_id}, skipping\n")
            continue

        print(f"🔄 Updating: {fname}")
        onboarding_temp = os.path.join(OUTPUTS_DIR, account_id, "onboarding_temp")
        extract_memo(onboarding_path, onboarding_temp)

        apply_onboarding(
            f"{v1_dir}/account_memo.json",
            f"{onboarding_temp}/account_memo.json",
            v2_dir
        )

        generate_agent_spec(f"{v2_dir}/account_memo.json", v2_dir, "v2")
        print(f"  ✅ v2 complete for {account_id}\n")

if __name__ == "__main__":
    run_pipeline_a()
    run_pipeline_b()
    print("🎉 All done!")