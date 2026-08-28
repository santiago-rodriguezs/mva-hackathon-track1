# Método — Día 1 (setup + triage del panel)

Versión publicable. Genotipos, coordenadas de candidatas, profundidades y
fenotipo textual → `notes/private/01-bitacora-2026-08-26.md` (gitignored).

## 1. Dependencias

Homebrew ya presente (v6.0.7). Instalado: **bcftools 1.24**, **samtools 1.24**,
**bedtools 2.31.1** (brew); **hf CLI 1.28.0** (`huggingface_hub[cli]`, Python
3.13 de miniconda). Auth: `hf auth login` lo hace el usuario (tokens no se tipean
en automático).

## 2. Descarga (solo lo mínimo)

Dataset `SageBio/mva-hackathon-2026-data` (acceso controlado): **11 archivos** =
doc clínico + VCF + `.tbi` + 8 FASTQ (~85 GB). **No hay BAM/CRAM.**
Bajado a `data/` (gitignored): solo VCF + `.tbi` + `.docx`. Los FASTQ **no**.
`git status` verificado: nada de `data/` trackeado.

## 3. Panel BED

`scripts/make_panel_bed.py` → `config/mva_panel_grch38.bed`: 14 genes
(9 core + 5 extended de `config/mva_genes.tsv`), cuerpo del gen ± 10 kb,
coordenadas GRCh38 desde Ensembl (assembly confirmado por gen). Estilo UCSC
(`chr15`). Es commiteable (deriva de Ensembl, no del genoma del proband).

`scripts/make_panel_cds_bed.py` (nuevo) → `config/mva_panel_cds_grch38.bed`:
exones de la transcripción canónica Ensembl ± 8 bp de splice, 259 regiones.
Sirve para separar señal codificante del ruido intrónico en el triage.

## 4. Inspección del VCF (agregados)

`scripts/01_inspect_vcf.sh`. **5.012.204 variantes** (4.086.641 SNP · 930.181
indel · 66.860 multialélicos; Ti/Tv 1,94). **1 muestra**, solo el proband.
Caller **GATK HaplotypeCaller 4.2.4.0** + VariantFiltration, en DNAnexus.
Ref GRCh38 `no_alt` + hs38d1, contigs **sin** `chr`. INFO: solo campos nativos
de GATK — **sin gnomAD/ClinVar/VEP**. FORMAT incluye `PGT`/`PID` (phasing
físico de GATK).

## 5. Referencia GRCh38

`scripts/03_get_reference.sh` (nuevo): baja el NCBI `no_alt` analysis set
(`GCA_000001405.15`, ~832 MB gz) y le quita el prefijo `chr` → nombres de contig
idénticos a los del VCF. Salida `ref/GRCh38.fa` (+ `.fai`), gitignored.
Cross-check: nombres y longitudes de contig coinciden con el header del VCF.

## 6. Triage sobre el panel (agregados)

`scripts/02_panel_triage.sh`: subset al panel → `bcftools norm -m -any -f ref` →
filtro de calidad (`FILTER=PASS && DP≥10 && GQ≥20`).

| Paso | Variantes (sitios) |
|---|---|
| En el panel (tras split de multialélicos) | 1814 |
| **Tras filtro de calidad** | **1778** |

1778 es casi todo polimorfismo común (el panel son ~2–3 Mb). Hizo falta filtrar
por rareza + impacto.

## 6b. Anotación gnomAD + consecuencia

Intento descartado: slice remoto de gnomAD v4.1 por tabix
(`scripts/_04_annotate_panel_gnomad-slice.sh.bak`) — correcto pero demasiado
lento (minutos por región, se colgaba en reintentos de libcurl).

Enfoque adoptado: `scripts/04_annotate_panel.py` — **Ensembl VEP REST**, lotes de
200 variantes (~9 llamadas, ~1 min). Trae `most_severe_consequence` + frecuencias
gnomAD. Marca CDS/splice con `config/mva_panel_cds_grch38.bed`.

- Umbral de raro: gnomAD AF < 0,001 o ausente → **341 / 1778** raras.
- Salida: `results/panel_rare.tsv` (gitignored).

## 7. Anotación profunda de candidatas (`scripts/05_deep_annotate.sh`)

Base ClinVar GRCh38 (2026-08-22) descargada a `ref/db/` (gitignored).
`scripts/05_deep_annotate.sh`: anota todo el panel con ClinVar
(`bcftools annotate`), lista el paisaje P/LP conocido por gen, y corre
`scripts/05_vep_candidates.py` (VEP REST con HGVS/MANE/exón, AlphaMissense, CADD,
LOFTEE, Mastermind, dbscSNV) sobre las candidatas raras en CDS/splice.

## 8. Priorización por fenotipo (proxy liviano)

Sin Java en la Mac → Exomiser/LIRICAL reales pendientes de setup (~20 GB hg38).
Proxy con **Phen2Gene** (API REST): con los HPO del caso, **BUB1B es el gen #1
del panel** y top ~0,2 % genoma-wide; el resto del core SAC (BUB3, BUB1, CEP57)
y ESCO2 caen justo detrás. El término de aborto recurrente parental sesga el
ranking global hacia trombofilia (F2, F5, ANXA5…) — hay que curar el HPO o
apoyarse en el panel.

## Resultado (nivel gen)

- **Ningún gen del panel con LoF homocigota** — sin señal de consanguinidad.
- **BUB1B** es el candidato: lleva el par esperado por el README (un alelo
  truncante + uno missense). El truncante está en **ClinVar como P/LP para
  "Mosaic variegated aneuploidy syndrome 1"**; el missense tiene **AlphaMissense
  0,92** y está ausente de gnomAD, pero figura como VUS en ClinVar y falta
  confirmar la fase. Coordenadas, genotipos y profundidades: `notes/private/`.
- Ninguna otra variante patogénica de ClinVar en el resto del panel (los hits
  del proband en otros genes del panel son Benign/Likely benign).

## Cambios a los scripts (respecto del punto de partida)

| Script | Cambio | Por qué |
|---|---|---|
| `01_inspect_vcf.sh` | Refresca el `.tbi` antes de contar | El índice bajado de HF venía con fecha anterior al `.vcf.gz`; `bcftools index -n` devolvía 0. |
| `02_panel_triage.sh` | Reconciliación de nombres de contig `chr` ↔ sin-`chr` | BED es UCSC, VCF es numérico; sin esto `view -R` daba 0 variantes. |
| `02_panel_triage.sh` | Subset al panel **antes** de normalizar | Normalizar 5 M de registros tarda minutos; solo el panel, segundos. |
| `02_panel_triage.sh` | `norm -m -any` en vez de `-m -both` | `-both` deprecado en bcftools 1.24. |
| `02_panel_triage.sh` | Emite además `panel_all_variants.tsv` sin filtro de calidad | El 2º alelo puede caer por `DP`/`GQ`. |
| `02_panel_triage.sh` | Resumen de genotipos por gen dentro del script | Responde la pregunta clave del envío #1. |
| `03_get_reference.sh` | **Nuevo** | Descarga + normalización de nombres de contig de la referencia. |
| `make_panel_cds_bed.py` | **Nuevo** | BED de exones+splice para separar señal codificante. |
| `04_annotate_panel.py` | **Nuevo** | Anotación gnomAD+consecuencia vía VEP REST y ranking de raras. |
| `_04_annotate_panel_gnomad-slice.sh.bak` | Archivado (no usar) | Slice remoto de gnomAD: correcto pero lento. |

## Manejo de datos

`data/`, `ref/`, `results/`, `notes/private/` → gitignored (verificado con
`git check-ignore`). Nada derivado del genoma del proband se commitea.
`git status` antes de cada commit. FASTQ (85 GB) no descargados.
