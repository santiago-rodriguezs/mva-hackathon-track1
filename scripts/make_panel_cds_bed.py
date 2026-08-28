#!/usr/bin/env python3
"""BED GRCh38 de regiones CODIFICANTES + splice del panel de MVA (Ensembl REST).

Complementa a make_panel_bed.py (que da el cuerpo del gen +-10kb para la fase 2
de SV/intrones). Este da exones traducidos (CDS) + UTRs de la transcripcion
canonica de cada gen, con un padding de splice, para el triage de variantes
codificantes de la fase 1.
"""
import csv, json, sys, time, urllib.request

SPLICE_PAD = 8   # bp a cada lado de cada exon (cubre sitios canonicos +-2 y algo mas)
SERVER = "https://rest.ensembl.org"


def get(url):
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def canonical_transcript(symbol):
    g = get(f"{SERVER}/lookup/symbol/homo_sapiens/{symbol}?expand=1")
    assert g["assembly_name"] == "GRCh38", (symbol, g["assembly_name"])
    for t in g["Transcript"]:
        if t.get("is_canonical"):
            return g, t
    # fallback: transcripcion mas larga
    return g, max(g["Transcript"], key=lambda t: t["length"])


def main(panel="config/mva_genes.tsv",
         out="config/mva_panel_cds_grch38.bed",
         tiers=("core", "extended")):
    rows = []
    with open(panel) as fh:
        for line in fh:
            if line.startswith("#") or line.startswith("symbol"):
                continue
            symbol, alias, tier, note = line.rstrip("\n").split("\t")
            if tier not in tiers:
                continue
            try:
                g, t = canonical_transcript(symbol)
            except Exception as e:
                print(f"  !! {symbol}: {e}", file=sys.stderr)
                continue
            chrom = f"chr{g['seq_region_name']}"
            exons = t.get("Exon", [])
            for ex in exons:
                s = max(0, ex["start"] - 1 - SPLICE_PAD)
                e = ex["end"] + SPLICE_PAD
                rows.append((chrom, s, e, f"{symbol}|{tier}|{t['id']}"))
            print(f"  {symbol:10s} {t['id']}  {len(exons)} exones  {chrom}")
            time.sleep(0.2)

    rows.sort(key=lambda r: (r[0], r[1]))
    with open(out, "w") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerows(rows)
    print(f"\nescritas {len(rows)} regiones exonicas -> {out}  (splice pad={SPLICE_PAD} bp)")


if __name__ == "__main__":
    main()
