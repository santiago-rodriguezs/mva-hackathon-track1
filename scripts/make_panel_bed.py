#!/usr/bin/env python3
"""Construye un BED GRCh38 del panel de genes de MVA desde Ensembl REST.

El padding importa: en BUB1B hay segundos alelos reportados en intrones
profundos, asi que tomamos el cuerpo completo del gen mas flancos, no solo exones.
"""
import csv, json, sys, time, urllib.request

PAD = 10_000  # bp a cada lado del cuerpo del gen
SERVER = "https://rest.ensembl.org"


def lookup(symbol):
    url = f"{SERVER}/lookup/symbol/homo_sapiens/{symbol}?expand=0"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main(panel="config/mva_genes.tsv",
         out="config/mva_panel_grch38.bed",
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
                g = lookup(symbol)
            except Exception as e:
                print(f"  !! {symbol}: {e}", file=sys.stderr)
                continue
            chrom, start, end = g["seq_region_name"], g["start"], g["end"]
            rows.append((f"chr{chrom}", max(0, start - 1 - PAD), end + PAD, symbol, tier))
            print(f"  {symbol:10s} chr{chrom}:{start}-{end}  ({g['assembly_name']})")
            time.sleep(0.2)

    rows.sort(key=lambda r: (r[0], r[1]))
    with open(out, "w") as fh:
        w = csv.writer(fh, delimiter="\t")
        for chrom, s, e, sym, tier in rows:
            w.writerow([chrom, s, e, f"{sym}|{tier}"])
    print(f"\nescritas {len(rows)} regiones -> {out}  (pad={PAD:,} bp por lado)")


if __name__ == "__main__":
    main()
