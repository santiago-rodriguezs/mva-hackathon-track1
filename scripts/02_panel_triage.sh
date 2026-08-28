#!/usr/bin/env bash
# Primer filtro: variantes raras dentro del panel de MVA.
# Corre en minutos y es el 80% del envio #1.
set -euo pipefail
cd "$(dirname "$0")/.."

VCF="${1:?uso: $0 data/WGS_EX2312012_HGWCNDSX7.vcf.gz}"
BED="${2:-config/mva_panel_grch38.bed}"
REF="${3:-ref/GRCh38.fa}"

mkdir -p results

# --- reconciliacion de nombres de contig -------------------------------------
# El VCF del hackathon viene de GATK sobre GCA_000001405.15..._no_chr.fasta:
# los contigs son "1","2",...,"X","M" SIN prefijo "chr". El panel BED se genera
# con estilo UCSC ("chr15"). Detectamos el estilo del VCF y adaptamos el BED.
if bcftools view -h "$VCF" | grep -m1 -q '^##contig=<ID=chr'; then
  vcf_style="chr"
else
  vcf_style="nochr"
fi
WORKBED="results/panel.work.bed"
if [ "$vcf_style" = "nochr" ]; then
  sed -E 's/^chr//' "$BED" | sort -k1,1 -k2,2n > "$WORKBED"
else
  sort -k1,1 -k2,2n "$BED" > "$WORKBED"
fi
echo "estilo de contig del VCF: $vcf_style  ->  BED de trabajo: $WORKBED"

if [ ! -s "$REF" ]; then
  echo "!! falta la referencia en $REF (necesaria para left-align de indels)." >&2
  echo "   corre scripts/03_get_reference.sh o pasa la ruta como 3er argumento." >&2
  exit 1
fi

echo
echo "[1/5] subset al panel (gen completo + flanco del BED) y luego normalizar"
# Subset PRIMERO (5M -> cientos de registros), despues normalizar: mismo
# resultado que normalizar todo el VCF pero en segundos en vez de minutos.
# -m -any descompone multialelicos (SNP e indel); -f left-alinea indels.
bcftools view -R "$WORKBED" "$VCF" -Ou \
  | bcftools norm -m -any -f "$REF" -Oz -o results/panel.vcf.gz
bcftools index -t -f results/panel.vcf.gz
echo "      variantes en el panel (crudo, post-split): $(bcftools view -H results/panel.vcf.gz | wc -l | tr -d ' ')"

echo
echo "[2/5] filtro de calidad (FILTER=PASS, DP>=10, GQ>=20)"
bcftools view -i 'FILTER="PASS" && FMT/DP>=10 && FMT/GQ>=20' \
  results/panel.vcf.gz -Oz -o results/panel_pass.vcf.gz
bcftools index -t -f results/panel_pass.vcf.gz
echo "      tras filtro de calidad: $(bcftools view -H results/panel_pass.vcf.gz | wc -l | tr -d ' ')"

echo
echo "[3/5] tabla legible (variantes que pasan calidad)"
{
  printf 'GENE\tCHROM\tPOS\tREF\tALT\tQUAL\tFILTER\tGT\tDP\tGQ\tAD\n'
  while IFS=$'\t' read -r c s e name _; do
    gene="${name%%|*}"
    bcftools query -r "${c}:$((s + 1))-${e}" \
      -f "${gene}"'\t%CHROM\t%POS\t%REF\t%ALT\t%QUAL\t%FILTER\t[%GT\t%DP\t%GQ\t%AD]\n' \
      results/panel_pass.vcf.gz || true
  done < "$WORKBED"
} > results/panel_candidates.tsv
echo "      -> results/panel_candidates.tsv"

echo
echo "[4/5] MISMA tabla pero SIN filtro de calidad (por si el 2do alelo quedo"
echo "      afuera por DP/GQ bajo: insercion, borde de indel, zona repetitiva)"
{
  printf 'GENE\tCHROM\tPOS\tREF\tALT\tQUAL\tFILTER\tGT\tDP\tGQ\tAD\n'
  while IFS=$'\t' read -r c s e name _; do
    gene="${name%%|*}"
    bcftools query -r "${c}:$((s + 1))-${e}" \
      -f "${gene}"'\t%CHROM\t%POS\t%REF\t%ALT\t%QUAL\t%FILTER\t[%GT\t%DP\t%GQ\t%AD]\n' \
      results/panel.vcf.gz || true
  done < "$WORKBED"
} > results/panel_all_variants.tsv
echo "      -> results/panel_all_variants.tsv"

echo
echo "[5/5] genotipos por gen"
echo "      buscamos, en un MISMO gen:"
echo "        (a) una variante 1/1  -> homocigota (consanguinidad / delocion en trans)"
echo "        (b) DOS o mas 0/1     -> candidata a heterocigosis compuesta"
echo
# Resumen sobre las variantes que pasan calidad. Normalizamos el separador de GT
# (| o /) y contamos clases de genotipo alternativo por gen.
awk -F'\t' 'NR>1 {
    gt=$8; gsub(/\|/,"/",gt);
    if (gt=="0/1"||gt=="1/0") het[$1]++;
    else if (gt=="1/1") hom[$1]++;
    else other[$1]=other[$1] gt ",";
    genes[$1]=1
  }
  END {
    printf "  %-10s %6s %6s   %s\n","GEN","0/1","1/1","(otros GT)";
    for (g in genes)
      printf "  %-10s %6d %6d   %s\n", g, het[g]+0, hom[g]+0, other[g];
  }' results/panel_candidates.tsv | sort

echo
echo "NOTA: si un gen muestra 0/1 == 1 y nada mas, es la senal esperada: el"
echo "segundo alelo esta escondido -> fase 2 (SV / MEI / splicing intronico)."
