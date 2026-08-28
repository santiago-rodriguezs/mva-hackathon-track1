#!/usr/bin/env bash
# Anotacion profunda de las candidatas del panel:
#   - ClinVar (bcftools annotate, base local en ref/db/)
#   - VEP REST con flags ricos: HGVS, MANE, exon/intron, AlphaMissense, CADD,
#     Conservation, LOFTEE, Mastermind, dbscSNV, SpliceAI (mejor esfuerzo)
# y ademas lista el paisaje ClinVar completo de cada gen del panel con hit raro,
# para ver si hay alelos patogenicos conocidos (p.ej. intronicos profundos) que
# convenga cazar en la fase 2.
#
# Requiere: 02_panel_triage.sh + 04_annotate_panel.py corridos;
#           ref/db/clinvar_grch38.vcf.gz (+ .tbi).
set -euo pipefail
cd "$(dirname "$0")/.."

PANEL_ALL="${1:-results/panel.vcf.gz}"          # todas las del panel (post-norm)
RARE_TSV="${2:-results/panel_rare.tsv}"
CLINVAR="${3:-ref/db/clinvar_grch38.vcf.gz}"
GENE_BED="${4:-config/mva_panel_grch38.bed}"

[ -s "$CLINVAR" ] || { echo "!! falta $CLINVAR"; exit 1; }
[ -s "$PANEL_ALL" ] || { echo "!! falta $PANEL_ALL (corré 02_panel_triage.sh)"; exit 1; }
mkdir -p results

echo "[1/3] anotando TODO el panel con ClinVar"
bcftools annotate -a "$CLINVAR" \
  -c 'INFO/CLNSIG,INFO/CLNREVSTAT,INFO/CLNDN,INFO/CLNHGVS,INFO/CLNVC,INFO/GENEINFO' \
  "$PANEL_ALL" -Oz -o results/panel_clinvar.vcf.gz
bcftools index -t -f results/panel_clinvar.vcf.gz

echo
echo "=== variantes del PROBAND que estan en ClinVar (cualquier CLNSIG) ==="
{
  printf 'GENE\tCHROM\tPOS\tREF\tALT\tGT\tDP\tGQ\tCLNSIG\tCLNREVSTAT\tCLNDN\n'
  while IFS=$'\t' read -r c s e name _; do
    g="${name%%|*}"; nc="${c#chr}"
    bcftools query -r "${nc}:$((s + 1))-${e}" -i 'CLNSIG!="."' \
      -f "${g}"'\t%CHROM\t%POS\t%REF\t%ALT\t[%GT\t%DP\t%GQ]\t%INFO/CLNSIG\t%INFO/CLNREVSTAT\t%INFO/CLNDN\n' \
      results/panel_clinvar.vcf.gz || true
  done < "$GENE_BED"
} | tee results/proband_in_clinvar.tsv | column -t -s$'\t'

echo
echo "[2/3] paisaje ClinVar P/LP de los genes con hit raro (aunque el proband NO las tenga)"
genes_hit=$(awk -F'\t' 'NR>1{print $1}' "$RARE_TSV" | sort -u | grep -v '^?$' || true)
: > results/clinvar_landscape.tsv
printf 'GENE\tCHROM\tPOS\tREF\tALT\tCLNSIG\tCLNREVSTAT\tCLNDN\tCLNHGVS\n' >> results/clinvar_landscape.tsv
while IFS=$'\t' read -r c s e name _; do
  g="${name%%|*}"
  echo "$genes_hit" | grep -qx "$g" || continue
  nc="${c#chr}"
  bcftools view -r "${nc}:$((s + 1))-${e}" "$CLINVAR" 2>/dev/null \
    | bcftools query -i 'CLNSIG ~ "athogenic"' \
        -f "${g}"'\t%CHROM\t%POS\t%REF\t%ALT\t%INFO/CLNSIG\t%INFO/CLNREVSTAT\t%INFO/CLNDN\t%INFO/CLNHGVS\n' \
    >> results/clinvar_landscape.tsv || true
done < "$GENE_BED"
echo "  -> results/clinvar_landscape.tsv  ($(($(wc -l < results/clinvar_landscape.tsv) - 1)) variantes P/LP)"
echo "  por gen:"
awk -F'\t' 'NR>1{n[$1]++} END{for(g in n) printf "    %-10s %d\n",g,n[g]}' results/clinvar_landscape.tsv | sort

echo
echo "[3/3] VEP REST rico sobre las candidatas raras en CDS/splice"
python3 scripts/05_vep_candidates.py
