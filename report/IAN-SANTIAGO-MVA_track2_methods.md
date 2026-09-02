# MVA Hackathon 2026 — Track 2 methods description (Drug Repurposing)

**Team name:** IAN-SANTIAGO-MVA
**Members (HF / GitHub):** santiago-rodriguezs, ianghitarroni
**Code:** https://github.com/santiago-rodriguezs/mva-hackathon-track1
**Detailed report:** `report/IAN-SANTIAGO-MVA_mechanism-and-repurposing_v2.md` (this
document answers the Track 2 methods form; the companion report has the full
mechanism, the candidate strategies, limitations, validation plan and the 16
verified references).

---

## Q1 (required) — Generative AI disclosure

Anthropic Claude (Claude Code CLI), model Claude Sonnet, **Claude Pro** plan
(consumer, USD 20/month). Model-training on chats and coding sessions:
**disabled**. Used for: literature retrieval, drafting, citation verification and
pipeline code. Reasoning about drug/target relationships used only public
sources; no proband genomic data beyond MVA-panel variant coordinates/genotypes
was provided to the model.

## Q2 — Approach, from variant/mechanism to candidate medication(s)

Starting from the Track 1 result — compound-heterozygous **BUB1B**:
c.2210T>G p.Leu737Ter (nonsense) + c.3006T>G p.Asn1002Lys (missense) — we
characterised the mechanism as **loss of function of BUBR1 and of the spindle
assembly checkpoint (SAC)** (Q8). We then mapped **each allele to a distinct
druggable liability**:

- **Nonsense allele → a UGA premature termination codon (PTC).** Addressable by
  promoting translational **readthrough** and inhibiting **nonsense-mediated
  mRNA decay (NMD)** so that some full-length BUBR1 is produced from this allele.
- **Missense allele → a candidate destabilising hypomorph** in the C-terminal
  kinase domain. Addressable by **slowing BUBR1 protein degradation**, raising the
  abundance of the partially functional protein.

For each liability we searched for **approved or clinically-advanced compounds
with a mechanism-of-action match**, then ranked by (a) demonstrated relevant
activity in human cells or in vivo, (b) existing human safety data, (c)
plausibility of acting on dividing cells / the relevant tissue. Selected
candidates (all framed as follow-up hypotheses, not treatments):

| Liability | Primary candidate | Comparators / complementary |
|---|---|---|
| UGA nonsense allele | **Amlexanox** (approved; dual PTC readthrough + NMD inhibition in human cells) | Ataluren (inconsistent efficacy, EMA authorisation not renewed 2025); ELX-02 (designer aminoglycoside, in clinical development); dedicated SMG1/NMD inhibitors as add-on |
| Destabilising missense allele | **NAD⁺ precursors (nicotinamide riboside / NMN)** — raise BUBR1 via the SIRT2–BubR1(K668) axis; in vivo rescue precedent in BubR1^H/H mice | SIRT2-selective activators (research stage) |

Predicted therapeutic readout for any candidate: **increased functional BUBR1
AND a measurable reduction in chromosome mis-segregation / aneuploidy**, not
protein level alone.

## Q3 — Automated or manual candidate identification?

**Primarily manual, literature-driven**, assisted by an LLM for retrieval and
drafting. No automated drug–target database pipeline was executed; candidates
were reasoned from the mechanism and confirmed by targeted literature search,
with every factual claim traced to a primary reference.

## Q4 — Manual literature review / curation

For each mechanistic node we ran targeted PubMed searches (BUB1B/BUBR1 + MVA;
nonsense readthrough + UGA codon identity; amlexanox; ataluren nmDMD phase 3 +
EMA status; ELX-02 safety; SIRT2 + BubR1 + NAD⁺; BubR1 dosage vs aneuploidy),
read the primary papers, and extracted the specific findings cited (e.g.
amlexanox's dual NMD-inhibition + readthrough; SIRT2 deacetylation of BUBR1-K668
opposing CBP; near-cognate insertion of Trp/Cys/Arg at UGA; BubR1 over-expression
also being protective only within a range). **All 16 citations were checked
against PubMed/publisher records** (authors, journal, year, volume/pages, PMID,
DOI) on 2026-08-30. Weak or contradictory evidence is reported explicitly
(ataluren).

## Q5 — Public vs proprietary data

**Only publicly available data.** No proprietary databases or data sources.

## Q6 — Public data sources used

- **PubMed / primary literature** — 16 references (companion report §10).
- **Regulatory records** — EMA/FDA public statements on ataluren (Translarna).
- **Variant annotation reused from Track 1** — Ensembl VEP, gnomAD v4, ClinVar
  (release 2026-08-22), AlphaMissense, LOFTEE, CADD.
- DrugBank / ChEMBL / ClinicalTrials.gov were **not** queried: the mechanism-first
  approach produced a small, well-characterised candidate set. They are the
  natural tools to scale the method (Q10).

## Q7 — Proprietary data sources

None.

## Q8 — How the variant mechanism was characterised

- **Direction:** **loss of function** of BUBR1.
- **Pathway disrupted:** the spindle assembly checkpoint / mitotic checkpoint
  complex (BUBR1–BUB3–MAD2–CDC20 inhibiting APC/C–CDC20 to delay anaphase until
  bi-orientation), plus BUBR1's KARD-mediated recruitment of PP2A–B56 to
  stabilise kinetochore–microtubule attachments.
- **Allele level:**
  - c.2210T>G p.Leu737Ter — reference codon TTA → **TGA (UGA)**; PTC in exon
    17/23, >50–55 nt upstream of the final exon–exon junction → **predicted NMD
    substrate**; any escaping transcript encodes a protein truncated before the
    entire C-terminal domain. Treated as **effectively null**. (ClinVar
    Pathogenic/Likely_pathogenic for MVA syndrome 1; LOFTEE HC; gnomAD ~3×10⁻⁵.)
  - c.3006T>G p.Asn1002Lys — non-conservative substitution in the C-terminal
    kinase domain, **absent from gnomAD**, **AlphaMissense 0.92**. Hypothesised
    **destabilising hypomorph** by analogy to other MVA BUBR1 missense alleles
    that lower protein abundance by increasing turnover. ClinVar VUS — not
    independently established as pathogenic.
- **Downstream biological consequence:** partial SAC failure → premature anaphase
  → chromosome mis-segregation → constitutional **variegated aneuploidy** →
  growth failure, microcephaly/short stature, renal anomaly, and childhood cancer
  predisposition (Wilms tumour, rhabdomyosarcoma).
- **Genotype model:** essentially null allele **in trans** with a partially
  functional but unstable allele (complete biallelic BUB1B loss is
  embryonic-lethal). Phase is **inferred, not yet experimentally confirmed**.

## Q9 — Time / effort

~1 day of literature review and writing for the mechanism + repurposing analysis,
on top of the Track 1 pipeline. **Zero compute cost.** The proposed validation
experiments (structural modelling / molecular dynamics of N1002K; protein
stability and readthrough assays; SAC-function and aneuploidy readouts) have
**not been run**.

## Q10 — Method abstract (≤500 words)

We derived a drug-repurposing hypothesis directly from the Track 1 genetic
result. The proband carries compound-heterozygous BUB1B variants: a nonsense
allele (c.2210T>G, p.Leu737Ter) and a missense allele (c.3006T>G, p.Asn1002Lys).
BUB1B encodes BUBR1, a core component of the mitotic checkpoint complex; reduced
BUBR1 weakens the spindle assembly checkpoint, causing premature anaphase,
chromosome mis-segregation and the constitutional variegated aneuploidy that
defines MVA1, which in turn drives growth failure, renal anomalies and childhood
cancer predisposition. At the codon level the nonsense variant converts a leucine
codon (TTA) to a UGA premature termination codon and is predicted to trigger
nonsense-mediated decay, making this allele effectively null. The missense
variant lies in the C-terminal kinase domain, is absent from population
databases, and scores 0.92 by AlphaMissense; by analogy to other MVA-associated
BUBR1 missense alleles that act as hypomorphs by lowering protein abundance, we
hypothesise it destabilises the domain and reduces the amount of BUBR1 made from
the second allele. Assuming the alleles are in trans, the genotype combines a
null allele with a partially functional, unstable allele — the residual-function
window typical of viable MVA1.

This creates two mechanistically distinct intervention points. First, partial
rescue of the null allele by promoting ribosomal readthrough of its UGA codon
together with NMD inhibition: amlexanox, an approved drug with documented dual
readthrough and NMD-inhibitory activity in human cells, is our primary candidate;
ataluren (efficacy inconsistent; EMA authorisation for nonsense-mutation DMD not
renewed in 2025) and the designer aminoglycoside ELX-02 are comparators, and a
dedicated NMD inhibitor could be paired with a pure readthrough agent. Second,
stabilisation of the residual (missense) BUBR1 by enhancing the NAD⁺/SIRT2 axis:
SIRT2 deacetylates BUBR1 at Lys668 and protects it from proteasomal degradation,
and raising NAD⁺ with nicotinamide riboside increases BubR1 and rescues
phenotypes in BubR1-hypomorphic mice — the closest published in vivo analogue of
this patient.

Strengths: the hypothesis is derived transparently from the genetics; both drug
arms are mechanism-matched, supported by primary literature (16 verified
references) and have human safety data; the framework generalises via a simple
rule (nonsense allele → readthrough arm; destabilising missense → stabilisation
arm; compound-het → both), reusable for other recessive patients and MCC genes.

Limitations: phase (trans) is not confirmed; p.Asn1002Lys is novel and its
destabilising effect is a hypothesis (ClinVar VUS); UGA readthrough inserts a
near-cognate residue (Trp/Cys/Arg), so the rescued protein is a p.737 point
mutant of unknown function; BUBR1 dosage is sensitive in both directions, so any
intervention must target a therapeutic window; MVA1 is multi-system with no
single target tissue, so the realistic near-term goal is reducing ongoing
chromosomal instability (and cancer risk), not reversing established aneuploidy.
No experimental validation has been performed; proposed assays are described in
the companion report.
