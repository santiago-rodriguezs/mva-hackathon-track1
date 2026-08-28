#!/usr/bin/env python3
"""Anota las variantes del panel con Ensembl VEP REST y rankea las raras.

Entrada : results/panel_pass.vcf.gz   (salida de 02_panel_triage.sh)
Config  : config/mva_panel_grch38.bed, config/mva_panel_cds_grch38.bed
Salida  : results/panel_rare.tsv  + resumen de genotipos por gen en consola

VEP REST (https://rest.ensembl.org) devuelve, por variante:
  - most_severe_consequence
  - colocated_variants[].frequencies[alt].gnomadg / gnomade  (AF gnomAD)
Se considera RARA: AF gnomAD (genomas, si no exomas) < 0.001, o ausente.
"""
import gzip, json, subprocess, sys, time, urllib.request

REST = "https://rest.ensembl.org/vep/homo_sapiens/region"
BATCH = 200
RARE_MAX = 0.001

IMPACT = {  # consecuencias codificantes / splice que nos interesan
    "transcript_ablation", "splice_acceptor_variant", "splice_donor_variant",
    "stop_gained", "frameshift_variant", "stop_lost", "start_lost",
    "transcript_amplification", "feature_elongation", "feature_truncation",
    "inframe_insertion", "inframe_deletion", "missense_variant",
    "protein_altering_variant", "splice_region_variant",
    "splice_donor_5th_base_variant", "splice_donor_region_variant",
    "splice_polypyrimidine_tract_variant", "start_retained_variant",
    "stop_retained_variant", "coding_sequence_variant", "incomplete_terminal_codon_variant",
}


def load_bed(path):
    out = []
    with open(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            c, s, e, name = line.split("\t")[:4]
            out.append((c[3:] if c.startswith("chr") else c, int(s), int(e), name.strip()))
    return out


def gene_for(chrom, pos, gene_bed):
    for c, s, e, name in gene_bed:
        if c == chrom and s < pos <= e:
            return name.split("|")[0]
    return "?"


def in_cds(chrom, pos, cds_bed):
    for c, s, e, _ in cds_bed:
        if c == chrom and s < pos <= e:
            return True
    return False


def read_variants(vcf_gz):
    """Devuelve lista de dicts con la info del proband por variante (ya bi-alélica)."""
    vs = []
    op = gzip.open(vcf_gz, "rt")
    for line in op:
        if line.startswith("#"):
            continue
        f = line.rstrip("\n").split("\t")
        chrom, pos, _id, ref, alt = f[0], int(f[1]), f[2], f[3], f[4]
        fmt = f[8].split(":")
        smp = dict(zip(fmt, f[9].split(":")))
        vs.append({
            "chrom": chrom, "pos": pos, "ref": ref, "alt": alt,
            "gt": smp.get("GT", "."), "dp": smp.get("DP", "."),
            "gq": smp.get("GQ", "."), "filter": f[6],
        })
    op.close()
    return vs


def vep_post(batch):
    body = json.dumps({
        "variants": [f'{v["chrom"]} {v["pos"]} . {v["ref"]} {v["alt"]} . . .' for v in batch],
        "canonical": 1,
    }).encode()
    url = REST + "?AF=1&af_gnomadg=1&af_gnomade=1"
    req = urllib.request.Request(url, data=body,
                                headers={"Content-Type": "application/json",
                                         "Accept": "application/json"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except Exception as e:
            wait = 2 ** attempt
            print(f"  VEP retry {attempt + 1}/5 en {wait}s ({e})", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("VEP REST no respondio tras 5 intentos")


def gnomad_af(rec, alt):
    """Mejor AF gnomAD disponible (genomas > exomas) para el alelo alt."""
    best = None
    for cv in rec.get("colocated_variants", []) or []:
        fr = (cv.get("frequencies") or {}).get(alt)
        if not fr:
            continue
        for key in ("gnomadg", "gnomade", "gnomad"):
            if key in fr:
                v = fr[key]
                best = v if best is None else max(best, v)
    return best


def main():
    gene_bed = load_bed("config/mva_panel_grch38.bed")
    cds_bed = load_bed("config/mva_panel_cds_grch38.bed")
    variants = read_variants("results/panel_pass.vcf.gz")
    print(f"variantes que pasan calidad en el panel: {len(variants)}")

    annotated = []
    for i in range(0, len(variants), BATCH):
        batch = variants[i:i + BATCH]
        res = vep_post(batch)
        # VEP indexa la respuesta por 'input'; armamos un dict
        by_input = {r["input"]: r for r in res}
        for v in batch:
            key = f'{v["chrom"]} {v["pos"]} . {v["ref"]} {v["alt"]} . . .'
            rec = by_input.get(key, {})
            v["csq"] = rec.get("most_severe_consequence", "?")
            v["af"] = gnomad_af(rec, v["alt"])
            v["gene"] = gene_for(v["chrom"], v["pos"], gene_bed)
            v["cds"] = in_cds(v["chrom"], v["pos"], cds_bed)
            annotated.append(v)
        print(f"  anotado {min(i + BATCH, len(variants))}/{len(variants)}")
        time.sleep(1)

    rare = [v for v in annotated if (v["af"] is None or v["af"] < RARE_MAX)]
    print(f"\nvariantes RARAS (gnomAD < {RARE_MAX} o ausente): {len(rare)}")

    with open("results/panel_rare.tsv", "w") as fh:
        fh.write("GENE\tCHROM\tPOS\tREF\tALT\tGT\tDP\tGQ\tgnomAD_AF\tCONSEQUENCE\tCDS\tFILTER\n")
        for v in sorted(rare, key=lambda x: (x["gene"], x["chrom"], x["pos"])):
            fh.write("\t".join(str(x) for x in [
                v["gene"], v["chrom"], v["pos"], v["ref"], v["alt"], v["gt"],
                v["dp"], v["gq"],
                "NA" if v["af"] is None else f'{v["af"]:.2e}',
                v["csq"], "Y" if v["cds"] else "n", v["filter"],
            ]) + "\n")
    print("-> results/panel_rare.tsv")

    # resumen por gen
    genes = {}
    for v in rare:
        g = genes.setdefault(v["gene"], {"het": 0, "hom": 0, "het_cds": 0, "hom_cds": 0,
                                         "het_impact": 0, "hom_impact": 0})
        gt = v["gt"].replace("|", "/")
        impact = v["cds"] and v["csq"] in IMPACT
        if gt in ("0/1", "1/0"):
            g["het"] += 1
            g["het_cds"] += v["cds"]
            g["het_impact"] += impact
        elif gt == "1/1":
            g["hom"] += 1
            g["hom_cds"] += v["cds"]
            g["hom_impact"] += impact

    print("\n=== GENOTIPOS POR GEN (solo variantes RARAS) ===")
    print(f"  {'GEN':<10} {'0/1 (CDS/impacto)':<20} {'1/1 (CDS/impacto)':<20}")
    for g in sorted(genes):
        d = genes[g]
        print(f"  {g:<10} "
              f"{str(d['het'])+' ('+str(d['het_cds'])+'/'+str(d['het_impact'])+')':<20} "
              f"{str(d['hom'])+' ('+str(d['hom_cds'])+'/'+str(d['hom_impact'])+')':<20}")

    print("\n=== VARIANTES RARAS EN CDS/SPLICE CON IMPACTO (candidatas envio #1) ===")
    hits = [v for v in rare if v["cds"] and v["csq"] in IMPACT]
    if not hits:
        print("  (ninguna)")
    for v in sorted(hits, key=lambda x: (x["gene"], x["pos"])):
        af = "NA" if v["af"] is None else f'{v["af"]:.2e}'
        print(f"  {v['gene']:<9} {v['chrom']}:{v['pos']} {v['ref']}>{v['alt']}  "
              f"{v['gt']}  gnomAD={af}  {v['csq']}  "
              f"DP={v['dp']} GQ={v['gq']}  FILTER={v['filter']}")

    print("\nLectura: gen con  1/1 de impacto  o  >=2  0/1 de impacto  = senal fuerte.")
    print("Gen con exactamente una 0/1 de impacto = 2do alelo oculto -> fase 2.")


if __name__ == "__main__":
    main()
