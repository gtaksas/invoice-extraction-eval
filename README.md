# Invoice Extraction with Claude: Accuracy-Tested

**Problem:** Accounting teams retype invoice data by hand, which is slow and error-prone.

**Approach:** Claude extracts structured fields from English and Hungarian invoices.
Arithmetic validation (net + VAT = gross) runs in plain code, not in the model, so errors can never be "talked away".

**Test set:** 40 synthetic invoices (EN/HU, 3 money formats, 3 date formats, 5 with deliberately wrong totals).

## Results

|   Prompt       | Thinking | Exact match | Arithmetic check | Tokens in/out per invoice | Cost per 1,000 invoices |
|----------------|----------|-------------|------------------|---------------------------|-------------------------|
| v1 (vague)	 |   on     |      0%     |       12%        |      104 / 283            |        $0.152           |
| v2 (specified) |   on     |    100%     |      100%        |      219 / 134            |        $0.089           |
| v2 (specified) |   off    |    100%     |      100%        |      218 / 80             |        $0.062           |

Haiku 5.5 model was used in every case.

**What I learned:** Vague instructions caused 0% exact match even though the model understood the invoices: it chose its own key names and formats. Specifying the schema, number format, date format and “never recalculate” took exact match to 100% and cut cost by ~40%. Disabling thinking for this simple task cut cost another 30% with no accuracy loss. Arithmetic validation runs in code, so it’s deterministic and also catches the 5 deliberately wrong totals.

## Limitations
Synthetic, clean, template-based data only; 40 invoices; no scans, no handwriting, no noisy OCR text yet; two languages. 
100% on this set does not predict 100% on real invoices. A harder test set is the next step.

## Next steps
PDF/image input, VAT-rate validation, ledger reconciliation agent.

## Run it
pip install anthropic · python make_dataset.py · python evaluate.py claude-haiku-5-5 v2
