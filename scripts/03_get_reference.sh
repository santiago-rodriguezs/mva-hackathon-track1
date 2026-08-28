#!/usr/bin/env bash
# Baja el genoma de referencia GRCh38 para el left-align de indels del paso 02.
#
# El VCF del hackathon fue llamado por GATK contra
#   GCA_000001405.15_GRCh38_no_alt_analysis_set_plus_hs38d1_masked..._no_chr.fasta
# es decir el "NCBI analysis set" con los nombres de contig SIN prefijo "chr"
# ("1".."22","X","Y","M","1_KI270706v1_random", ...).
#
# Bajamos el analysis set de NCBI (nombres con "chr") y le sacamos el prefijo,
# con lo que los nombres quedan identicos a los del VCF. Las secuencias de los
# cromosomas primarios son las mismas; el "masked exclusions v2" solo enmascara
# un punado de regiones GRC marcadas como falsas duplicaciones, ninguna en los
# genes del panel de MVA.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p ref

URL="https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gz"
GZ="ref/GRCh38.analysis_set.chr.fna.gz"
OUT="ref/GRCh38.fa"

if [ ! -s "$GZ" ]; then
  echo "== bajando analysis set de NCBI (~900 MB) =="
  curl -fSL --retry 3 -o "$GZ" "$URL"
fi

echo "== quitando prefijo 'chr' de los nombres de contig -> $OUT =="
gzcat "$GZ" | sed -E 's/^>chr/>/' > "$OUT"

echo "== indexando (samtools faidx) =="
samtools faidx "$OUT"

echo
echo "contigs (primeros): $(cut -f1 "${OUT}.fai" | head -5 | tr '\n' ' ')"
echo "listo -> $OUT"
