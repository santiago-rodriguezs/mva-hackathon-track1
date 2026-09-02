# MVA Hackathon 2026 — Track 1 methods description

**Team name:** IAN-SANTIAGO-MVA
**Members (Hugging Face / GitHub):** santiago-rodriguezs, ianghitarroni
**Model / approach:** panel-triage + VEP/ClinVar/AlphaMissense annotation (`panel-vep-clinvar`)
**Submission:** #1 (probe)
**Date:** 2026-08-30
**Code:** https://github.com/santiago-rodriguezs/mva-hackathon-track1
**Proband:** PROBAND01 (VCF sample name: WGS_EX2312012)

Structured to answer the official *Methods description* form (Track 1).

---

## Q1 (required) — Generative AI disclosure

Anthropic Claude (Claude Code CLI), model Claude Sonnet, **Claude Pro** plan
(consumer, USD 20/month). Model-training on chats and coding sessions:
**disabled**. Heavy processing (bcftools, VEP, ClinVar) ran locally; the raw
FASTQ and the complete VCF were not sent to any external service.

---

## Q2 — Approach in detail

Autosomal-recessive disease with a confirmed clinical diagnosis of MVA, so the
strategy is: (a) restrict to a curated MVA gene panel, (b) recover the expected
**two** causal alleles in one gene, (c) rank by evidence.

**Pipeline (all scripted, `scripts/`, numbered by run order):**

1. **Input characterisation** (`01_inspect_vcf.sh`) — 1 sample (proband only, not
   a trio); 5,012,204 variants; GATK HaplotypeCaller 4.2.4.0 + VariantFiltration
   hard filters; reference GRCh38 no-alt + hs38d1 with numeric contig names; not
   pre-annotated (native GATK INFO only); FORMAT carries GATK physical-phasing
   tags.
2. **Panel definition** — 14 genes (9 established MVA genes + 5 related
   mitotic/SAC genes), `config/mva_genes.tsv`. Two BEDs from Ensembl: gene body
   ± 10 kb, and canonical CDS + 8 bp splice padding (`make_panel_bed.py`,
   `make_panel_cds_bed.py`).
3. **Reference** (`03_get_reference.sh`) — NCBI GRCh38 no-alt analysis set, `chr`
   prefix stripped to match the VCF contig names exactly.
4. **Panel triage** (`02_panel_triage.sh`) — contig-name reconciliation
   (UCSC vs numeric), subset to panel, `bcftools norm -m -any -f <ref>`, then
   quality filter `FILTER=PASS && FMT/DP>=10 && FMT/GQ>=20`.
   1,814 raw panel sites → **1,778 after quality filtering**.
5. **Frequency + consequence** (`04_annotate_panel.py`) — Ensembl VEP REST
   (batches of 200): `most_severe_consequence` + gnomAD allele frequencies; CDS/
   splice overlap flag. Rare = gnomAD AF < 0.001 or absent → **341 / 1,778**.
6. **Deep annotation of candidates** (`05_deep_annotate.sh`,
   `05_vep_candidates.py`) — local ClinVar (GRCh38, 2026-08-22) via
   `bcftools annotate`; VEP REST with HGVS, MANE, exon/intron numbering,
   AlphaMissense, CADD, LOFTEE, Mastermind, dbscSNV on the rare CDS/splice set.
7. **Phenotype prioritisation** — 8 HPO terms from the clinical description;
   Phen2Gene (API) ranks the panel; BUB1B is #1 in the panel and top ~0.2 %
   genome-wide.

**Result / prediction:** compound-heterozygous **BUB1B** (NM_001211.6):

| | Variant | Consequence | Evidence |
|---|---|---|---|
| Allele 1 | chr15:40209701 T>G · c.2210T>G · p.Leu737Ter | stop_gained (exon 17/23) | **ClinVar Pathogenic/Likely_pathogenic for "Mosaic variegated aneuploidy syndrome 1"** (multiple submitters, no conflicts); LOFTEE HC; gnomAD ~3×10⁻⁵; CADD 36; Mastermind-cited |
| Allele 2 | chr15:40220612 T>G · c.3006T>G · p.Asn1002Lys | missense (last exon 23/23) | absent from gnomAD; **AlphaMissense 0.92 (likely pathogenic)**; CADD 24.5; ClinVar lists the aa change as VUS |

Both are clean heterozygous calls (allele balance 0.54 / 0.46, GQ 99, PASS).
Phase (cis/trans) is not resolved — the variants are 10.9 kb apart and are not
physically phased in the GATK VCF; trans is inferred from the child being
affected. **EPCR 0.80** for the pair (allele 1 alone would merit ~0.95; the pair
is discounted for the residual uncertainty on allele 2 and the unconfirmed phase).

---

## Q3 — Automated output or manually curated?

**Partly curated.** The pipeline produces ranked annotation tables
automatically (`results/panel_rare.tsv`, deep-annotation output); the final CSV
row and the EPCR value were assembled by the analysts from those tables. It is
not a single end-to-end automated call.

## Q4 — Downstream manual review

For each rare panel candidate we manually inspected: ClinVar classification and
review status, AlphaMissense / CADD / LOFTEE, gnomAD frequency, allele balance
and GQ, transcript context (MANE, exon vs last exon), and consistency with the
HPO profile. Non-BUB1B rare hits were all UTR / low-impact and were dropped. No
variant calls were edited; review only affected selection and ranking.

## Q5 — Public data only?

**Only publicly available data.** No proprietary data.

## Q6 — Public data used

- Ensembl VEP REST + Ensembl gene models / MANE Select transcripts (GRCh38).
- gnomAD v4 allele frequencies (via VEP).
- ClinVar GRCh38 VCF, release 2026-08-22 (NCBI).
- AlphaMissense, CADD, LOFTEE, dbscSNV, Mastermind identifiers (via VEP).
- HPO / Phen2Gene API for phenotype-based gene ranking.
- NCBI GRCh38 no-alt analysis set (reference FASTA).
- Gene panel curated from the published MVA literature (BUB1B/CEP57/TRIP13 etc.).

## Q7 — Proprietary data used

None.

## Q8 — Compound-het pairs or single variants?

The approach outputs **compound-heterozygous pairs** (and single variants when
applicable). The primary prediction for this case is a pair.

## Q9 — Secondary / incidental findings

None submitted in this probe submission. A systematic secondary-findings screen
(e.g. ACMG SF gene list) has not yet been run; it is planned for a later
submission and would be flagged `finding_type=secondary` (which does not affect
the automated score).

## Q10 — Run time and cost

Laptop, no cloud. bcftools panel triage: seconds. VEP REST annotation of 1,778
variants: ~1 min. ClinVar download: ~1 min (~180 MB). One-time GRCh38 reference
download: ~10 min (~830 MB). Deep annotation of candidates: ~30 s. Total compute
cost: **USD 0**. Analyst time: ~1 day for pipeline + this write-up. LLM
assistance: Claude Pro subscription (USD 20/month), no per-run cost.

---

## Q11 — Method abstract (≤500 words)

We treated the case as recessive disease with a known clinical diagnosis (MVA),
so gene discovery reduces to recovering the two causal alleles within a curated
14-gene MVA panel. Starting from the organiser-provided GATK VCF (single proband,
no parents, GRCh38, unannotated), we reconciled contig naming, restricted to the
panel (gene body ± 10 kb), normalised and split multiallelics, and applied a
quality filter (PASS, DP ≥ 10, GQ ≥ 20), leaving 1,778 panel variants. We
annotated these with population frequency and consequence via Ensembl VEP REST
and kept the 341 rare (gnomAD < 0.1 % or absent). Deep annotation of the rare
coding/splice subset used a local ClinVar release, AlphaMissense, CADD, LOFTEE
and Mastermind. Phenotype prioritisation with Phen2Gene on eight HPO terms placed
BUB1B first in the panel and in the top ~0.2 % genome-wide.

BUB1B was the only panel gene carrying rare coding variants of impact, and the
only panel gene with a pathogenic ClinVar entry in the proband. We predict
compound-heterozygous BUB1B (NM_001211.6): allele 1, c.2210T>G p.Leu737Ter, a
nonsense variant classified Pathogenic/Likely_pathogenic in ClinVar specifically
for "Mosaic variegated aneuploidy syndrome 1" (LOFTEE high-confidence,
gnomAD ~3×10⁻⁵); allele 2, c.3006T>G p.Asn1002Lys, a last-exon missense absent
from gnomAD with AlphaMissense 0.92. This matches the canonical BUB1B/MVA1
pattern of one truncating plus one hypomorphic allele, and the phenotype
(childhood rhabdomyosarcoma, severe IUGR, short stature, nephrocalcinosis,
parental recurrent pregnancy loss).

**Strengths:** fully reproducible, public-data-only, fast (minutes, zero cloud
cost); allele 1 is independently confirmed in ClinVar for the exact disease;
convergent lines of evidence (frequency, consequence, ClinVar, AlphaMissense,
phenotype ranking).

**Limitations:** (1) phase of the two alleles is not experimentally confirmed —
they are 10.9 kb apart and not read-phased in the short-read VCF; (2) allele 2 is
not independently established as pathogenic (ClinVar lists the amino-acid change
as VUS); its support rests on AlphaMissense, gnomAD absence, phenotype fit and
being in trans with a pathogenic loss-of-function allele; (3) no formal ACMG
classification yet (Exomiser/LIRICAL pending an environment with Java + the hg38
data bundle); (4) if the true second allele is cryptic (deep-intronic,
mobile-element insertion, or structural), it is not recoverable from the VCF and
requires realignment of the FASTQ with SpliceAI/Pangolin, MELT/xTea and SV
calling — planned as phase 2, informed by this probe submission's leaderboard
score.

---

## Reproducibility

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

Repository is private during the Hackathon and will be made public at close for
judging. No genome-derived file (FASTQ/BAM/VCF/genotype tables) is committed;
`data/`, `ref/`, `results/`, `notes/private/` are git-ignored.
