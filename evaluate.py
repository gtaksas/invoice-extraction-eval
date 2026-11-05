import json, hashlib, os, sys
import anthropic

MODEL = sys.argv[1] if len(sys.argv) > 1 else "claude-haiku-5-5"
PROMPT_VERSION = sys.argv[2] if len(sys.argv) > 2 else "v1"
PROMPTS = {
    "v1": "Extract invoice data as JSON only.",
    "v2": ("You extract data from invoices (English or Hungarian). Reply with ONE JSON object, no prose. "
           "Keys: supplier, invoice_number, date (ISO YYYY-MM-DD), net, vat_rate, vat_amount, gross. "
           "Numbers are plain integers in HUF with no separators. Extract exactly what is printed; never correct or recalculate. "
           "If a field is missing, use null."),
}
FIELDS = ["supplier", "invoice_number", "date", "net", "vat_rate", "vat_amount", "gross"]
client = anthropic.Anthropic()
os.makedirs(".cache", exist_ok=True)
THINKING = sys.argv[3] if len(sys.argv) > 3 else "off"   # "off" or "on"

def extract(text):
    key = hashlib.md5(f"{MODEL}|{PROMPT_VERSION}|{THINKING}|{text}".encode()).hexdigest()
    path = f".cache/{key}.json"
    if os.path.exists(path):
        return json.load(open(path))
    extra = {"thinking": {"type": "disabled"}} if THINKING == "off" else {}
    r = client.messages.create(model=MODEL, max_tokens=1500, system=PROMPTS[PROMPT_VERSION],
                               messages=[{"role": "user", "content": text}], **extra)
    raw = "".join(b.text for b in r.content if b.type == "text")
    think = "".join(getattr(b, "thinking", "") or "" for b in r.content if b.type == "thinking")
    start, end = raw.find("{"), raw.rfind("}")
    try: out = json.loads(raw[start:end + 1])
    except Exception: out = {}
    res = {"out": out, "in_tok": r.usage.input_tokens, "out_tok": r.usage.output_tokens,
           "think_chars": len(think)}
    if out:
        json.dump(res, open(path, "w"))
    return res

data = json.load(open("dataset.json", encoding="utf-8"))
hits = {f: 0 for f in FIELDS}; exact = 0; in_t = out_t = 0; flagged = 0; failures = []
for item in data:
    res = extract(item["text"]); o = res["out"]
    in_t += res["in_tok"]; out_t += res["out_tok"]
    ok_all = True
    for f in FIELDS:
        if o.get(f) == item["truth"][f]: hits[f] += 1
        else: ok_all = False; failures.append((item["id"], f, item["truth"][f], o.get(f)))
    exact += ok_all
    # the arithmetic check lives in CODE, not in the model
    try: arithmetic_ok = o["net"] + o["vat_amount"] == o["gross"]
    except Exception: arithmetic_ok = False
    if arithmetic_ok == item["arithmetic_ok"]: flagged += 1

n = len(data)
print(f"model={MODEL} prompt={PROMPT_VERSION}")
for f in FIELDS: print(f"{f:15} {hits[f]/n:.0%}")
print(f"exact match (all fields): {exact/n:.0%}")
print(f"arithmetic check correct: {flagged/n:.0%}")
print(f"tokens in/out total: {in_t}/{out_t}  -> per invoice: {in_t/n:.0f}/{out_t/n:.0f}")
print("first failures:", failures[:10])

PRICE_IN, PRICE_OUT = 0.10, 0.50   # USD per million tokens, Haiku 5.5, prompts up to 100k, from the pricing page (https://platform.claude.com/docs/en/about-claude/pricing)
cost = (in_t * PRICE_IN + out_t * PRICE_OUT) / 1_000_000
print(f"cost per 1,000 invoices: ${cost / n * 1000:.4f}")
