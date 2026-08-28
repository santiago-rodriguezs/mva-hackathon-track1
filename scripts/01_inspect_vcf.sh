#!/usr/bin/env bash
# Primera mirada al VCF. Responde las preguntas de notes/00-open-questions.md
set -euo pipefail
VCF="${1:?uso: $0 data/WGS_EX2312012_HGWCNDSX7.vcf.gz}"

echo "=== MUESTRAS (si hay mas de una es un trio y cambia toda la estrategia) ==="
bcftools query -l "$VCF"

echo; echo "=== CALLER Y REFERENCIA (header) ==="
bcftools view -h "$VCF" | grep -E '^##(source|reference|GATKCommandLine|DRAGENCommandLine|bcftools)' || echo "  (sin lineas de source)"

echo; echo "=== CONTEO TOTAL ==="
# 'index -n' es instantaneo pero miente (devuelve 0) si el .tbi esta desactualizado
# respecto al .vcf.gz -- pasa al bajar el indice de HF por separado. Refrescamos.
bcftools index -t -f "$VCF" 2>/dev/null || true
bcftools index -n "$VCF" 2>/dev/null || bcftools view -H "$VCF" | wc -l

echo; echo "=== SNV vs INDEL, TI/TV ==="
bcftools stats "$VCF" | grep -E '^SN|^TSTV' | cut -f2-

echo; echo "=== CAMPOS INFO (nos dice si ya viene anotado con gnomAD/ClinVar) ==="
bcftools view -h "$VCF" | grep '^##INFO' | sed -E 's/.*ID=([^,]+).*Description="([^"]*)".*/  \1\t\2/'

echo; echo "=== CAMPOS FORMAT ==="
bcftools view -h "$VCF" | grep '^##FORMAT' | sed -E 's/.*ID=([^,]+).*Description="([^"]*)".*/  \1\t\2/'
