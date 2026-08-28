#!/usr/bin/env python3
"""VEP REST rico sobre las candidatas raras del panel (CDS/splice).

Lee results/panel_rare.tsv, se queda con las CDS=Y, y por cada una pide a VEP
REST: HGVSc/p, transcripcion MANE/canonica, numero de exon/intron, AlphaMissense,
CADD, Conservation, LOFTEE, Mastermind, dbscSNV, SpliceAI (mejor esfuerzo), y
clin_sig de los colocated (ClinVar via Ensembl).
"""
import csv, json, sys, time, urllib.request

REST = "https://rest.ensembl.org/vep/homo_sapiens/region"
# flags que rest.ensembl.org acepta; SpliceAI/MaxEntScan se prueban aparte
BASE_FLAGS = ("hgvs=1&canonical=1&mane=1&numbers=1&variant_class=1"
              "&AlphaMissense=1&CADD=1&Conservation=1&Blosum62=1"
              "&Mastermind=1&dbscSNV=1&LoF=1"
              "&AF=1&af_gnomadg=1&af_gnomade=1")


def post(variants, flags):
    body = json.dumps({
        "variants": [f'{c} {p} . {r} {a} . . .' for (c, p, r, a) in variants]
    }).encode()
    req = urllib.request.Request(f"{REST}?{flags}", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Accept": "application/json"})
    for i in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 400:
                return {"_http400": e.read().decode()[:400]}
            time.sleep(2 ** i)
        except Exception:
            time.sleep(2 ** i)
    return {"_failed": True}


def load_candidates(path="results/panel_rare.tsv"):
    out = []
    with open(path) as fh:
        r = csv.DictReader(fh, delimiter="\t")
        for row in r:
            if row["CDS"] == "Y":
                out.append(row)
    return out


def pick_tx(rec):
    """transcript_consequence MANE Select > canonica > la mas severa."""
    tcs = rec.get("transcript_consequences", []) or []
    if not tcs:
        return {}
    for t in tcs:
        if t.get("mane_select"):
            return t
    for t in tcs:
        if t.get("canonical"):
            return t
    return tcs[0]


def fmt(v):
    return "." if v is None else v


def main():
    cands = load_candidates()
    if not cands:
        print("  (sin candidatas CDS=Y en results/panel_rare.tsv)")
        return
    variants = [(c["CHROM"], int(c["POS"]), c["REF"], c["ALT"]) for c in cands]

    res = post(variants, BASE_FLAGS)
    if isinstance(res, dict):
        print("  VEP fallo:", res)
        return
    by_in = {r["input"]: r for r in res}

    # intento aparte con SpliceAI/MaxEntScan (puede dar 400 si no estan)
    spliceai = {}
    r2 = post(variants, "SpliceAI=1&MaxEntScan=1")
    if isinstance(r2, list):
        for r in r2:
            spliceai[r["input"]] = r

    for (c, p, r_, a) in variants:
        key = f'{c} {p} . {r_} {a} . . .'
        rec = by_in.get(key, {})
        tx = pick_tx(rec)
        cvs = []
        for cv in rec.get("colocated_variants", []) or []:
            for s in (cv.get("clin_sig") or []):
                cvs.append(f'{cv.get("id","?")}:{s}')
        am = tx.get("alphamissense") or {}
        sa = (spliceai.get(key, {}) or {})
        sa_tc = (sa.get("transcript_consequences") or [{}])
        sa0 = sa_tc[0] if sa_tc else {}

        print(f"\n=== {c}:{p} {r_}>{a} ===")
        print(f"  consecuencia   : {rec.get('most_severe_consequence','?')}")
        print(f"  transcripcion  : {fmt(tx.get('transcript_id'))}"
              f"  MANE={fmt(tx.get('mane_select'))}  canonica={fmt(tx.get('canonical'))}")
        print(f"  HGVSc / HGVSp  : {fmt(tx.get('hgvsc'))}  |  {fmt(tx.get('hgvsp'))}")
        print(f"  exon / intron  : exon={fmt(tx.get('exon'))}  intron={fmt(tx.get('intron'))}")
        print(f"  gnomAD genomas : {fmt(rec.get('colocated_variants',[{}])[0].get('frequencies',{}) if rec.get('colocated_variants') else '.')}")
        print(f"  AlphaMissense  : score={fmt(am.get('am_pathogenicity'))}  class={fmt(am.get('am_class'))}")
        print(f"  CADD phred     : {fmt(tx.get('cadd_phred'))}")
        print(f"  Conservation   : {fmt(rec.get('conservation'))}")
        print(f"  LOFTEE (LoF)   : {fmt(tx.get('lof'))} {fmt(tx.get('lof_filter'))} {fmt(tx.get('lof_flags'))}")
        print(f"  dbscSNV        : ada={fmt(tx.get('ada_score'))}  rf={fmt(tx.get('rf_score'))}")
        print(f"  SpliceAI       : DS_AG={fmt(sa0.get('spliceai_pred_ds_ag'))}"
              f" DS_AL={fmt(sa0.get('spliceai_pred_ds_al'))}"
              f" DS_DG={fmt(sa0.get('spliceai_pred_ds_dg'))}"
              f" DS_DL={fmt(sa0.get('spliceai_pred_ds_dl'))}")
        print(f"  MaxEntScan     : ref={fmt(sa0.get('maxentscan_ref'))} alt={fmt(sa0.get('maxentscan_alt'))}")
        print(f"  Mastermind     : {fmt(tx.get('mastermind_mmid3'))}  count={fmt(tx.get('mastermind_counts'))}")
        print(f"  ClinVar (Ensembl colocated): {', '.join(cvs) if cvs else '(sin match)'}")


if __name__ == "__main__":
    main()
