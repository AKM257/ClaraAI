import os, json, re, logging
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from generate_agent_spec import generate_agent_spec
from apply_onboarding import apply_onboarding

load_dotenv()

# Setup logging
log_dir = "../logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

DEMO_DIR = "../dataset/demo_calls"
ONBOARDING_DIR = "../dataset/onboarding_calls"
OUTPUTS_DIR = "../outputs/accounts"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_memo(transcript_path, output_dir, force=False):
    output_path = f"{output_dir}/account_memo.json"

    # IDEMPOTENT: skip if already exists
    if os.path.exists(output_path) and not force:
        log.info(f"SKIP (already exists): {output_path}")
        with open(output_path) as f:
            return json.load(f)

    with open("../prompts/extract_demo.txt") as f:
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
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(memo, f, indent=2)

    log.info(f"Memo saved: {output_path}")
    return memo

def run_pipeline_a(force=False):
    log.info("=== PIPELINE A: Demo Calls -> v1 ===")
    results = []
    for fname in os.listdir(DEMO_DIR):
        if not fname.endswith(".txt"):
            continue
        account_id = fname.replace(".txt", "").replace(" ", "_").lower()
        transcript_path = os.path.join(DEMO_DIR, fname)
        output_dir = os.path.join(OUTPUTS_DIR, account_id, "v1")

        log.info(f"Processing demo: {fname} -> account: {account_id}")
        try:
            memo = extract_memo(transcript_path, output_dir, force)
            generate_agent_spec(f"{output_dir}/account_memo.json", output_dir, "v1")
            log.info(f"v1 complete: {account_id}")
            results.append({"account": account_id, "status": "success", "version": "v1"})
        except Exception as e:
            log.error(f"FAILED {account_id}: {e}")
            results.append({"account": account_id, "status": "failed", "error": str(e)})

    return results

def run_pipeline_b(force=False):
    log.info("=== PIPELINE B: Onboarding -> v2 ===")
    results = []
    for fname in os.listdir(ONBOARDING_DIR):
        if not fname.endswith(".txt"):
            continue
        account_id = fname.replace(".txt", "").replace(" ", "_").lower()
        v1_dir = os.path.join(OUTPUTS_DIR, account_id, "v1")
        v2_dir = os.path.join(OUTPUTS_DIR, account_id, "v2")
        temp_dir = os.path.join(OUTPUTS_DIR, account_id, "onboarding_temp")

        if not os.path.exists(f"{v1_dir}/account_memo.json"):
            log.warning(f"No v1 found for {account_id}, skipping")
            continue

        # IDEMPOTENT: skip v2 if already exists
        if os.path.exists(f"{v2_dir}/account_memo.json") and not force:
            log.info(f"SKIP (v2 already exists): {account_id}")
            continue

        log.info(f"Updating: {fname} -> account: {account_id}")
        try:
            extract_memo(os.path.join(ONBOARDING_DIR, fname), temp_dir, force)
            apply_onboarding(f"{v1_dir}/account_memo.json", f"{temp_dir}/account_memo.json", v2_dir)
            generate_agent_spec(f"{v2_dir}/account_memo.json", v2_dir, "v2")
            log.info(f"v2 complete: {account_id}")
            results.append({"account": account_id, "status": "success", "version": "v2"})
        except Exception as e:
            log.error(f"FAILED {account_id}: {e}")
            results.append({"account": account_id, "status": "failed", "error": str(e)})

    return results

if __name__ == "__main__":
    log.info("Pipeline started")
    a_results = run_pipeline_a()
    b_results = run_pipeline_b()

    summary = {
        "run_at": datetime.now().isoformat(),
        "pipeline_a": a_results,
        "pipeline_b": b_results,
        "total": len(a_results) + len(b_results),
        "succeeded": sum(1 for r in a_results + b_results if r["status"] == "success"),
        "failed": sum(1 for r in a_results + b_results if r["status"] == "failed"),
        "skipped": sum(1 for r in a_results + b_results if r.get("status") == "skipped"),
    }

    summary_path = f"../logs/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    log.info(f"Done. {summary['succeeded']} succeeded, {summary['failed']} failed.")
    log.info(f"Summary saved: {summary_path}")