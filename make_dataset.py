import json, random
random.seed(42)

SUPPLIERS = ["ACME Kft.", "Zöld Híd Bt.", "Duna Logisztika Zrt.", "Nova Studio Kft.", "Pannon Print Kft."]
MONTHS = ["January","February","March","April","May","June","July","August","September"]

def money(n, style):
    if style == 0: return f"{n:,}".replace(",", " ") + " HUF"
    if style == 1: return f"{n:,}".replace(",", ".") + " Ft"
    return f"HUF {n:,}"

def make(i):
    net = random.randrange(20000, 900000, 1000)
    rate = random.choice([27, 18, 5, 0])
    vat = round(net * rate / 100)
    gross = net + vat
    broken = i % 8 == 0                      # every 8th invoice has a wrong total
    printed_gross = gross + 1000 if broken else gross
    m, d = random.randint(1, 9), random.randint(1, 28)
    iso = f"2026-{m:02d}-{d:02d}"
    date_txt = random.choice([iso, f"{d:02d}.{m:02d}.2026", f"{MONTHS[m-1]} {d}, 2026"])
    s = random.choice(SUPPLIERS)
    no = f"2026/{random.randint(100, 999)}"
    st = random.randint(0, 2)
    if random.random() < 0.5:
        text = f"{s}\nInvoice no. {no}\nDate: {date_txt}\nNet: {money(net, st)}\nVAT {rate}%: {money(vat, st)}\nTotal: {money(printed_gross, st)}"
    else:
        text = f"SZÁMLA / {s}\nSzámlaszám: {no}\nKelt: {date_txt}\nNettó: {money(net, st)}\nÁFA ({rate}%): {money(vat, st)}\nBruttó végösszeg: {money(printed_gross, st)}"
    truth = dict(supplier=s, invoice_number=no, date=iso, net=net, vat_rate=rate, vat_amount=vat, gross=printed_gross)
    return dict(id=i, text=text, truth=truth, arithmetic_ok=not broken)

json.dump([make(i) for i in range(1, 41)], open("dataset.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

