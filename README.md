# BUB1B — reproducible Track 2 support

**Team:** IAN-SANTIAGO-MVA  
**Participants:** Ian Franco Ghitarroni and Santiago Rodriguez Salinas  
**Analysis/report date:** 22 October 2026  
**Repository packaging and verification:** 23 October 2026

This directory contains the completed computational work and sources behind the mechanism-conditioned BUB1B drug-repurposing proposal discussed in the 22 October session. Start with [the evidence map](EVIDENCE_MAP.md): it connects each reported result to its inputs, code and output.

## Read the report

- [Session analysis report, 11 pages](report/BUB1B_Therapeutic_Hypothesis.pdf), in English and plural team voice.
- [Markdown text of that report](report/report.md).
- [Session methods workbook](report/methods_description_form.xlsx) and [extracted answers](report/methods_answers.json).
- The **official submitted report and methods form** remain at [`../../IAN-SANTIAGO-MVA_track2_report.pdf`](../../IAN-SANTIAGO-MVA_track2_report.pdf) and [`../../IAN-SANTIAGO-MVA_methods_description.xlsx`](../../IAN-SANTIAGO-MVA_methods_description.xlsx). The official PDF includes the team's additional disclosure page. Those existing files are not replaced by this supplement.

## Reproduce the analysis

Use Python 3.12. From this directory:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python analysis/analyze.py --out rebuilt/analysis
python analysis/analyze.py --variants analysis/inputs/extension_R727C.csv --out rebuilt/extension
python analysis/plot_results.py
python validation/verify.py
```

The analysis needs no network once dependencies are installed: all public reference inputs are frozen here. `--out rebuilt/...` preserves the original archived outputs and runtime. The plotting script reads archived measurements and refreshes only `analysis/results/comparison.png`.

Expected headline results are N1002 pLDDT **91.06**, SASA **27.457 Å²**, selected contacts **2.825/2.827/2.948 Å**, and **12 unweighted scenarios**. The standalone R727C run must work without editing the analysis code. Numerical CSV outputs should match the archived files exactly. Runtime and environment metadata may differ.

## Rebuild the session PDF

```bash
python report/build_report.py --output-dir rebuilt/report
python report/extract_methods.py --output rebuilt/methods_answers.json
```

Bundled DejaVu fonts make report generation independent of OS font paths. The builder uses the recorded comparison results and runtime so its text remains aligned with the archived report. PDF timestamps can differ. It does not generate the separately added official team-disclosure page.

## Render the animation

```bash
python animation/animate.py --quality preview --start 45 --end 46 --width 480 --fps 12 --output rebuilt/animation_test.mp4
python animation/animate.py --quality final --output rebuilt/BUB1B_explainer.mp4
```

The full source retains 180 seconds, English captions, Latin Modern fonts and the supplied C-alpha JSON. Cairo is optional; without it geometry uses at least 4× supersampling. No synthesized narration is included. Large MP4s are reproducible outputs and are not included in Git. See [animation instructions](animation/README.md).

## What is demonstrated

- Exact reference translation/codon consistency and seven literature-grounded comparison contexts.
- WT structural metrics with sampling and domain-isolation sensitivity.
- An explicit, phase-aware experimental decision grid.
- A separate additional-variant run, invalid-reference rejection, source hashes and result reproduction.

The analysis **does not establish N1002K instability or drug efficacy**. 4-PBA is a conditional lead for an expressed, stability-impaired allele with useful residual function. NMN/TUDCA are comparators; amlexanox targets a separate stop-allele branch. Unknown phase is retained. Animation morphs are not molecular dynamics. The prospective functional assays in the report have not been performed.

## Provenance and data scope

The support package contains public protein/CDS/model references, curated candidate/comparator annotations, and the candidate details already discussed in the report. It contains no raw proband sequencing, raw genotype call tables, patient identifiers, clinical records, credentials or chat transcripts. Candidate calls are supplied inputs, not independently re-called or phased here. Read the repository's [data-handling policy](../../../DATA_HANDLING.md).

[references.json](references.json) documents scientific sources. [MANIFEST.sha256](MANIFEST.sha256) fingerprints the files as uploaded. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) documents included fonts and reference data. No broad repository license is introduced by this upload.
