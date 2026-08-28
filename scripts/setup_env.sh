#!/usr/bin/env bash
# Dependencias de la fase 1. Correr una vez, desde la Mac.
set -euo pipefail

if ! command -v brew >/dev/null; then
  echo "Falta Homebrew. Instalalo desde https://brew.sh y volve a correr esto."
  exit 1
fi

echo "== htslib toolkit =="
brew install bcftools samtools bedtools

echo "== cliente de Hugging Face =="
python3 -m pip install --upgrade "huggingface_hub[cli]"

echo
echo "Ahora autenticate:  hf auth login"
echo "El token lo sacas de https://huggingface.co/settings/tokens (permiso de lectura alcanza)"
