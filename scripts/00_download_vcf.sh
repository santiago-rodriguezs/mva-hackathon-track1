#!/usr/bin/env bash
# Baja SOLO el VCF (no los 85 GB) y lista que mas hay en el dataset.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== los 11 archivos del dataset ==="
python3 - <<'PY'
from huggingface_hub import list_repo_files
for f in sorted(list_repo_files("SageBio/mva-hackathon-2026-data", repo_type="dataset")):
    print(" ", f)
PY

echo
echo "=== bajando el VCF a ./data ==="
hf download SageBio/mva-hackathon-2026-data \
  WGS_EX2312012_HGWCNDSX7.vcf.gz \
  --repo-type dataset --local-dir ./data

ls -lh data/
