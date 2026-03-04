import json, os, sys
from dotenv import load_dotenv

load_dotenv()

def generate_agent_spec(memo_path, output_dir, version="v1"):
    with open(memo_path) as f:
        memo = json.load(f)

    with open("prompts/agent_prompt_template.txt") as f:
        template = f.read()

    # Build business hours description
    bh = memo.get("business_hours", {})
    days = ", ".join(bh.get("days", [])) if bh.get("days") else "hours not confirmed"
    start = bh.get("start", "TBD")
    end = bh.get("end", "TBD")
    tz = bh.get("timezone", "TBD")
    bh_desc = f"{days}, {start}–{end} {tz}" if days != "hours not confirmed" else "Business hours not yet confirmed — await onboarding"

    # Build emergency routing description
    er = memo.get("emergency_routing_rules", {})
    emergency_routing = er.get("primary_contact") or "on-call team (routing TBD)"

    # Build emergency definition
    ed = memo.get("emergency_definition", [])
    emergency_def = ", ".join(ed) if ed else "as defined by client (TBD)"

    # Fill template
    prompt = template\
        .replace("{{company_name}}", memo.get("company_name", "the company"))\
        .replace("{{business_hours_description}}", bh_desc)\
        .replace("{{transfer_timeout}}", str(memo.get("call_transfer_rules", {}).get("timeout_seconds") or 30))\
        .replace("{{emergency_definition}}", emergency_def)\
        .replace("{{emergency_routing}}", emergency_routing)

    agent_spec = {
        "agent_name": f"Clara - {memo.get('company_name', 'Unknown')}",
        "version": version,
        "voice_style": "professional, warm, concise",
        "system_prompt": prompt,
        "key_variables": {
            "timezone": bh.get("timezone"),
            "business_hours": bh_desc,
            "emergency_routing": emergency_routing,
            "transfer_timeout_seconds": memo.get("call_transfer_rules", {}).get("timeout_seconds")
        },
        "call_transfer_protocol": memo.get("call_transfer_rules"),
        "fallback_protocol": memo.get("call_transfer_rules", {}).get("fail_message") or "Apologize and assure callback",
        "tool_invocation_placeholders": [
            "transfer_call(number)",
            "log_callback(name, number, issue)",
            "check_business_hours()"
        ]
    }

    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/agent_spec.json", "w") as f:
        json.dump(agent_spec, f, indent=2)

    print(f"✅ Agent spec saved to {output_dir}/agent_spec.json")
    return agent_spec

if __name__ == "__main__":
    memo_path = sys.argv[1]
    output_dir = sys.argv[2]
    version = sys.argv[3] if len(sys.argv) > 3 else "v1"
    generate_agent_spec(memo_path, output_dir, version)