# MVA Hackathon 2026 — Track 1 methods report

**Team:** IAN-SANTIAGO-MVA
**Members (Hugging Face / GitHub):** santiago-rodriguezs, ianghitarroni
**Submission:** #1 (probe)
**Date:** 2026-08-30
**Code:** https://github.com/santiago-rodriguezs/mva-hackathon-track1
**Proband:** WGS_EX2312012

---

## 1. Summary of the prediction

We predict the proband's condition is **autosomal-recessive Mosaic Variegated
Aneuploidy type 1 (MVA1)** caused by **compound-heterozygous variants in
`BUB1B` (NM_001211.6 / ENST00000287598, MANE Select):**

| | Variant | Consequence | Key evidence |
|---|---|---|---|
| Allele 1 | `chr15:40209701 T>G` · c.2210T>G · p.Leu737Ter | stop_gained, exon 17/23 | **ClinVar Pathogenic/Likely_pathogenic for "Mosaic variegated aneuploidy syndrome 1"** (multiple submitters, no conflicts); LOFTEE high-confidence LoF; gnomAD ~3×10⁻⁵; CADD 36; literature-cited (Mastermind) |
| Allele 2 | `chr15:40220612 T>G` · c.3006T>G · p.Asn1002Lys | missense, exon 23/23 (last) | Absent from gnomAD (genomes + exomes); **AlphaMissense 0.92 → likely pathogenic**; CADD 24.5; last-exon (NMD-escape → altered protein, compatible with a hypomorphic second allele). Caveat: the amino-acid substitution is listed in ClinVar as **Uncertain significance** (single submitter). |

EPCR assigned to the pair: **0.8**. Allele 1 alone would merit ~0.95; the pair is
discounted for the residual uncertainty on allele 2 (ClinVar VUS) and because
**phase (cis vs trans) is not experimentally confirmed** — the two variants are
10.9 kb apart and are not physically phased in the GATK VCF. Trans is inferred
from the fact that the child is affected.

This is a **probe submission**: the live leaderboard score tells us whether
allele 2 is the true second hit or whether the second causal allele is cryptic
(deep-intronic, mobile-element insertion, or structural) and must be recovered
from the FASTQ in a second phase.

---

## 2. Data handling

The dataset is the whole genome of a living child under controlled access. No
genome-derived file (FASTQ, BAM, VCF, or any table of individual genotypes) is
committed to the repository; `data/`, `ref/`, `results/` and working notes with
genotype-level detail are git-ignored and verified with `git check-ignore` before
every commit. For this phase only the VCF (+ index) and the clinical phenotype
document were downloaded; the ~85 GB of FASTQ were not. Each team member has
their own dataset access and downloads their own copy — no data is shared between
members.

---

## 3. Pipeline

All steps are scripted and numbered in `scripts/`. Tools: bcftools 1.24,
samtools 1.24, bedtools 2.31.1; annotation via Ensembl VEP REST and a local
ClinVar VCF (GRCh38, 2026-08-22).

### 3.1 Input characterisation (`01_inspect_vcf.sh`)

- **1 sample** (`WGS_EX2312012`) — proband only, **not a trio**. Compound-het
  phasing therefore cannot use parental transmission.
- **5,012,204 variants**. Caller: **GATK HaplotypeCaller 4.2.4.0** with
  `VariantFiltration` hard filters (QD2/MQ40/RPRS-8/FS60/MQRankSum-12.5), run on
  DNAnexus. Reference: GRCh38 no-alt analysis set + hs38d1, contigs **without**
  the `chr` prefix.
- **Not pre-annotated** — INFO carries only native GATK fields (no gnomAD, no
  ClinVar). Annotation was performed from scratch.
- FORMAT includes GATK physical-phasing tags (`PGT`/`PID`), used opportunistically
  for phasing.

### 3.2 Gene panel

Curated MVA panel of 14 genes (9 established MVA genes + 5 related
mitotic/SAC genes) in `config/mva_genes.tsv`. Two BED files are generated from
Ensembl (`make_panel_bed.py`, `make_panel_cds_bed.py`):

- **gene body ± 10 kb** — for this phase and for phase-2 intronic/SV work;
- **canonical CDS + 8 bp splice padding** (259 regions) — to separate coding
  signal from intronic noise.

### 3.3 Panel triage (`02_panel_triage.sh`)

1. **Contig-name reconciliation** — the panel BED is UCSC-style (`chr15`), the
   VCF is numeric (`15`); the script detects the VCF style and rewrites the BED
   accordingly (without this, region extraction silently returns nothing).
2. Subset to the panel, then `bcftools norm -m -any -f <ref>` (split
   multiallelics, left-align indels).
3. **Quality filter:** `FILTER=PASS && FMT/DP>=10 && FMT/GQ>=20`.

Result: 1,814 raw panel sites → **1,778 after quality filtering**.

Reference: `03_get_reference.sh` downloads the NCBI GRCh38 no-alt analysis set
and strips the `chr` prefix so contig names match the VCF exactly.

### 3.4 Population frequency + consequence (`04_annotate_panel.py`)

Ensembl VEP REST (batches of 200), pulling `most_severe_consequence` and gnomAD
allele frequencies; each variant flagged for CDS/splice overlap.
Rare threshold: **gnomAD AF < 0.001 or absent → 341 / 1,778 rare variants**.

### 3.5 Deep annotation of candidates (`05_deep_annotate.sh` + `05_vep_candidates.py`)

- `bcftools annotate` against local ClinVar (CLNSIG/CLNREVSTAT/CLNDN/CLNHGVS) for
  the whole panel.
- VEP REST with HGVS, MANE, exon/intron numbering, AlphaMissense, CADD, LOFTEE,
  Mastermind, dbscSNV on the rare CDS/splice candidates.

### 3.6 Phenotype prioritisation

HPO terms extracted from the clinical document: HP:0002859 Rhabdomyosarcoma,
HP:0000121 Nephrocalcinosis, HP:0004322 Short stature, HP:0001508 Failure to
thrive, HP:0003202 Skeletal muscle atrophy, HP:0001622 Premature birth,
HP:0001518 Small for gestational age, HP:0200067 Recurrent spontaneous abortion
(parental).

Phen2Gene (API) on this HPO set ranks **BUB1B #1 among the panel** and in the
top ~0.2 % genome-wide; the rest of the core SAC (BUB3, BUB1, CEP57) and ESCO2
follow. Note: the parental recurrent-pregnancy-loss term biases the global
ranking toward thrombophilia genes (F2, F5, ANXA5) — consistent with the
clinical document's guidance to read that term as a signal of chromosomal
instability rather than a coagulation phenotype. A full Exomiser/LIRICAL run
(variant + phenotype + ACMG scoring) is pending environment setup (Java + hg38
data bundle).

---

## 4. Why BUB1B and not another panel gene

- After quality + rarity filtering, **BUB1B is the only panel gene carrying rare
  coding variants of impact** (one nonsense + one missense). No panel gene
  carries a homozygous loss-of-function variant (no consanguinity signal).
- Cross-referencing the proband's panel variants against ClinVar: **the only
  pathogenic/likely-pathogenic hit anywhere in the panel is the BUB1B nonsense
  allele**. Every other panel variant present in ClinVar is Benign/Likely benign.
- The phenotype constellation (childhood rhabdomyosarcoma, severe IUGR, short
  stature, nephrocalcinosis, parental recurrent pregnancy loss) is the classic
  BUB1B/MVA1 presentation; Wilms tumour and rhabdomyosarcoma are the cancers
  reported in MVA1.

---

## 5. Limitations and planned phase 2

1. **Phase of the two BUB1B alleles is unconfirmed.** Next: read-backed phasing
   from the FASTQ; long-read if needed.
2. **Allele 2 (p.Asn1002Lys) is not independently established as pathogenic**
   (ClinVar VUS; evidence rests on AlphaMissense + gnomAD absence + phenotype +
   being in trans with a pathogenic LoF). If the leaderboard indicates only one
   correct allele, the true second hit is cryptic — planned work: SpliceAI /
   Pangolin over BUB1B introns, MELT / xTea for mobile-element insertions, and
   structural-variant calling, all from realigned FASTQ.
3. **No formal ACMG classification yet** (Exomiser/LIRICAL pending).
4. Secondary/incidental findings not yet systematically screened.

---

## 6. Reproducibility

```bash
./scripts/setup_env.sh
./scripts/00_download_vcf.sh
python3 scripts/make_panel_bed.py
python3 scripts/make_panel_cds_bed.py
./scripts/01_inspect_vcf.sh   data/WGS_EX2312012_HGWCNDSX7.vcf.gz
./scripts/03_get_reference.sh
./scripts/02_panel_triage.sh  data/WGS_EX2312012_HGWCNDSX7.vcf.gz
python3 scripts/04_annotate_panel.py
./scripts/05_deep_annotate.sh
```

The repository is private during the Hackathon and will be made public at close
for judging.

---

## 7. AI assistant disclosure

The analysis pipeline and this report were developed with **Anthropic Claude
(Claude Code CLI)** running locally on the analyst's machine, which orchestrated
the command-line tools above.

- **Provider / model:** Anthropic — Claude (Claude Code CLI).
- **Plan / tier:** _[SANTIAGO — completar con el real: "Claude Max plan" / "Claude Pro" / "Anthropic API (commercial terms)"]_.
- **Data-handling setting:** _[SANTIAGO — completar con el real, p. ej. "consumer
  terms; entrenamiento con datos del usuario deshabilitado en Privacy settings" o
  "Anthropic API, commercial terms, no training on customer content"]_.

What the model received: shell-command outputs from the local pipeline (bcftools
/ VEP / ClinVar), including per-variant genotype, depth and quality fields for the
~15 panel variants examined in detail, plus aggregate counts and the candidate
variant coordinates (which are the submission itself). The raw FASTQ, the full
VCF, and the clinical phenotype document were **not** uploaded to any external
service; all heavy processing ran locally.
