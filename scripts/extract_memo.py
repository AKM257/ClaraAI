import json, os, re, sys
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_memo(transcript_path, output_dir):
    with open("prompts/extract_demo.txt") as f:
        prompt_template = f.read()

    with open(transcript_path) as f:
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
    with open(f"{output_dir}/account_memo.json", "w") as f:
        json.dump(memo, f, indent=2)

    print(f"✅ Memo saved to {output_dir}/account_memo.json")
    return memo

if __name__ == "__main__":
    transcript_path = sys.argv[1]
    output_dir = sys.argv[2]
    extract_memo(transcript_path, output_dir)