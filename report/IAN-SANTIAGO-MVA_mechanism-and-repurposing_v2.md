# Mechanism and candidate therapeutic strategy for BUB1B-related mosaic variegated aneuploidy syndrome (MVA1)

**Team:** IAN-SANTIAGO-MVA · **Version:** 2 · **Date:** 2026-08-30
**Companion to:** Track 1 methods description (`IAN-SANTIAGO-MVA_track1_report.md`)

> Scope: this document characterises the disease mechanism implied by the two
> BUB1B variants identified in Track 1 and sets out drug-repurposing hypotheses
> for Track 2. Every therapeutic statement is a hypothesis for follow-up, not a
> treatment recommendation. Citations are listed in §9 and should be
> re-verified against primary sources before final submission.

---

## 1. Genetic findings (from Track 1)

Compound-heterozygous **BUB1B** (NM_001211.6 / ENST00000287598, MANE Select):

| Allele | Variant | Consequence | Supporting evidence |
|---|---|---|---|
| 1 | c.2210T>G, p.Leu737Ter | nonsense, exon 17/23 | ClinVar Pathogenic/Likely_pathogenic for "Mosaic variegated aneuploidy syndrome 1" (multiple submitters, no conflicts); LOFTEE high-confidence LoF; gnomAD ~3×10⁻⁵; CADD 36 |
| 2 | c.3006T>G, p.Asn1002Lys | missense, exon 23/23 (terminal) | absent from gnomAD (genomes + exomes); AlphaMissense 0.92 (likely pathogenic); CADD 24.5. The amino-acid change (also reachable via c.3006T>A) is listed in ClinVar as **Uncertain significance**, single submitter — i.e. novel/under-characterised, not independently classified pathogenic |

The two variants are **10.9 kb apart and are not physically phased** in the
short-read GATK VCF. The mechanistic model below assumes they are **in trans**;
this is biologically expected for an affected child (see §4) but is **not yet
experimentally confirmed** and is a stated limitation (§7). Read-backed phasing
from the FASTQ over the BUB1B locus is planned.

---

## 2. Pathway context: the spindle assembly checkpoint

BUB1B encodes **BUBR1**, a core subunit of the **mitotic checkpoint complex
(MCC)** together with BUB3, MAD2 and CDC20 [1,2]. During mitosis, kinetochores
that are unattached or not under tension catalyse MCC assembly; the MCC binds and
inhibits the **APC/C–CDC20** ubiquitin ligase, blocking degradation of **securin**
and **cyclin B1** and thereby delaying anaphase onset until every chromosome is
bi-oriented [1,2]. BUBR1 contributes to the checkpoint both as a structural MCC
component and, via its **KARD motif (~aa 665–685)**, by recruiting **PP2A–B56** to
kinetochores to balance Aurora B activity and stabilise correct
kinetochore–microtubule attachments [3].

Reduced BUBR1 function weakens this checkpoint: cells enter anaphase before
biorientation is complete, mis-segregate chromosomes, and accumulate the
cell-to-cell variable gains and losses ("variegated aneuploidy") that define
**MVA1** [4,5]. Constitutional aneuploidy in turn drives the growth failure,
microcephaly/short stature, renal anomalies and childhood cancer predisposition
(notably Wilms tumour and rhabdomyosarcoma) seen in this syndrome [4].

---

## 3. Predicted effect of each allele

### 3.1 c.2210T>G, p.Leu737Ter — null allele

At the codon level the reference leucine codon **TTA** becomes **TGA**, i.e. a
**UGA (opal)** premature termination codon. Consequences:

- The PTC lies in exon 17 of 23, **well upstream (>50–55 nt) of the final
  exon–exon junction**, so the transcript is predicted to be a substrate for
  **nonsense-mediated mRNA decay (NMD)** [6]. Expected output from this allele:
  little or no protein.
- Even any NMD-escaping transcript would encode a protein **truncated before the
  entire C-terminal kinase(-like) domain (~aa 766–1050)** and everything distal,
  removing regions required for checkpoint signalling. This allele is therefore
  treated as **effectively null**, consistent with its ClinVar classification and
  with the general finding that one MVA1 allele is typically a truncating/null
  mutation [4,5].

### 3.2 c.3006T>G, p.Asn1002Lys — candidate hypomorphic allele

- Residue 1002 lies within the **C-terminal kinase/pseudokinase domain** of
  BUBR1. In vertebrates this domain is widely regarded as a **pseudokinase**
  (degenerate catalytic motifs; its essential role appears structural/scaffolding
  rather than catalytic) [7], so we refer to it as the kinase(-like) domain.
- MVA1-associated **missense** alleles cluster in or near this domain, and
  functional work has shown that such substitutions frequently act as
  **hypomorphs that lower BUBR1 protein abundance by increasing turnover**,
  rather than abolishing a specific biochemical activity [5].
- We therefore **hypothesise** that p.Asn1002Lys (a non-conservative Asn→Lys
  change at a position absent from population databases) **destabilises the
  kinase(-like) domain fold and reduces the amount of BUBR1 produced from the
  second allele**, leaving partial checkpoint function. This is a hypothesis: it
  is supported by analogy and by the variant's absence from gnomAD and high
  AlphaMissense score, but p.Asn1002Lys itself has not been functionally studied
  and is a ClinVar VUS. Testing is proposed in §8.

---

## 4. Genotype model

If the alleles are **in trans**, the proband combines an **essentially null**
nonsense allele with a **partially functional but likely unstable** missense
allele. Complete biallelic loss of BUB1B is embryonic-lethal in mouse [8];
viable MVA1 patients characteristically retain **residual BUBR1 function**,
usually through a hypomorphic second allele [4,5]. The predicted net effect here
— a substantial but incomplete reduction in BUBR1 level/activity — matches the
level of checkpoint impairment required to produce variegated aneuploidy without
being lethal.

**Corollary for therapy:** the two alleles create **two mechanistically distinct
intervention points** — (i) partial rescue of the null allele by suppressing NMD
and/or reading through its UGA PTC, and (ii) stabilisation of the residual
(missense) BUBR1 protein. Either would raise functional BUBR1 toward the level
needed to restore checkpoint activity.

---

## 5. Candidate strategy A — translational rescue of the p.Leu737Ter (UGA) allele

**Rationale.** Restoring even a modest fraction of full-length BUBR1 from the
null allele could push total BUBR1 across the functional threshold. Success
requires **both** (a) preventing NMD from destroying the mutant transcript and
(b) achieving ribosomal readthrough of the PTC. UGA is the **most permissive** of
the three stop codons for readthrough [9], which is favourable here.

**Primary candidate — amlexanox.** An approved small molecule (topical, for
aphthous ulcers) reported to have **dual activity**: partial NMD inhibition and
promotion of PTC readthrough in human cells across several disease genes [10].
The dual mechanism maps directly onto the two requirements above, which is why we
rank it first. It is well characterised and orally bioavailable in other
repurposing contexts (e.g. TBK1/IKKε inhibition) [11]. **No data exist for BUB1B
p.Leu737Ter specifically** — this is a repurposing hypothesis.

**Comparators / experimental options (not recommendations):**
- **Ataluren (PTC124):** designed for PTC readthrough, with greatest activity at
  UGA. Clinical efficacy has been inconsistent (phase 3 primary endpoints not
  met [12]) and its EMA conditional authorisation for nonsense-mutation DMD was
  **not renewed in 2025**; the FDA has not approved it. Best used as a
  mechanistic comparator, not a therapeutic.
- **Aminoglycoside-derived readthrough agents:** gentamicin/G418 (toxicity-
  limited) and the designer compound **ELX-02**, which is in clinical development
  for nonsense-mutation genetic disease and is less ototoxic/nephrotoxic than
  classical aminoglycosides [13].
- **Dedicated NMD inhibitors** (e.g. SMG1 kinase inhibitors) as an add-on to a
  pure readthrough agent, to reproduce amlexanox's dual effect with two tool
  compounds.

**Key limitation of this strategy.** Readthrough of a UGA codon inserts a
**near-cognate amino acid — predominantly Trp, Arg or Cys — not the original
Leu** [14]. The rescued product is therefore full-length BUBR1 carrying a
**single substitution at position 737** (in the linker between the KARD motif and
the kinase domain). Whether p.737 tolerates these substitutions functionally is
unknown and must be tested (§8); it cannot be assumed that readthrough restores
wild-type protein.

---

## 6. Candidate strategy B — stabilisation of residual BUBR1 (NAD⁺/SIRT2 axis)

**Rationale.** If p.Asn1002Lys acts mainly by **destabilising** BUBR1 (§3.2),
then slowing BUBR1 degradation should raise the abundance of the partially
functional protein from the second allele.

**Mechanism and precedent.** BUBR1 stability is regulated by acetylation:
acetylation (e.g. by PCAF) opposes its degradation, and **SIRT2-dependent
deacetylation protects BUBR1 from ubiquitination and proteasomal turnover** [15].
In **BubR1-hypomorphic (BubR1^H/H) mice** — a direct model of BUBR1 insufficiency
— **raising NAD⁺ (via nicotinamide riboside) increases BubR1 abundance and
extends lifespan through the SIRT2–BubR1 axis**, and SIRT2 overexpression
partially rescues BubR1-insufficiency phenotypes [15]. This is the closest
published in vivo analogue of the patient's situation.

**Candidate interventions (hypotheses):** NAD⁺ precursors already used in humans
as supplements / in trials — **nicotinamide riboside (NR)** or **nicotinamide
mononucleotide (NMN)** — with SIRT2-selective activators as a research-stage
alternative. Advantages: mechanism-matched to the hypomorphic allele, oral,
low-toxicity, human safety data exist. This strategy is **conditional** on the
destabilisation hypothesis for p.Asn1002Lys being borne out by §8.

---

## 7. Limitations

1. **Phase (trans) not confirmed** — the entire compound-het model depends on it;
   read-backed phasing is pending.
2. **p.Asn1002Lys is novel/under-characterised** (ClinVar VUS; no functional
   data). Its classification as a destabilising hypomorph is a hypothesis.
3. **BUBR1 dosage is sensitive in both directions.** BubR1 *insufficiency* causes
   aneuploidy and progeroid phenotypes [8,16], but *increased* BubR1 also has
   phenotypes and is protective against aneuploidy/cancer only within a range
   [16]. Any intervention that raises BUBR1 must aim for a **therapeutic window**,
   not maximal expression.
4. **Readthrough product is not wild-type** (§5) — a substituted BUBR1 at p.737.
5. **Pseudokinase uncertainty** [7] — mechanistic claims about the "kinase
   domain" should be read as about a structural domain of debated catalytic
   status.
6. **Delivery / target tissue.** MVA1 is constitutional and multi-system; there
   is no single target organ. See §9.
7. **All drug claims are repurposing hypotheses**; none has been tested against
   BUB1B alleles.

---

## 8. Proposed validation

1. **Phasing:** read-backed phasing (WhatsHap) over BUB1B from the provided FASTQ;
   long-read if short reads are insufficient at 10.9 kb.
2. **Structure / dynamics:** homology or AlphaFold model of the BUBR1 kinase(-like)
   domain; molecular-dynamics comparison of wild-type vs N1002K (fold stability,
   local unfolding, ΔΔG estimates).
3. **Protein-level assays** (patient fibroblasts / iPSC, or heterologous
   expression): steady-state BUBR1 by immunoblot; cycloheximide-chase half-life;
   proteasome-dependence (MG132); rescue by NAD⁺ precursors / SIRT2 modulation.
4. **Transcript-level:** allele-specific expression and NMD sensitivity of the
   c.2210T>G allele (± NMD inhibition); readthrough assay (dual-luciferase with
   the patient UGA context) ± amlexanox / ataluren / ELX-02, with mass-spec
   identification of the inserted residue at position 737.
5. **Functional endpoints — the primary readouts:** nocodazole-challenge mitotic
   arrest (checkpoint competence); mitotic timing by live imaging;
   **chromosome mis-segregation and aneuploidy** by micronucleus assay,
   anaphase-bridge scoring and single-cell karyotyping/scDNA-seq, before and
   after each intervention. Success = increased functional BUBR1 **and** a
   measurable reduction in aneuploidy, not protein level alone.

---

## 9. Clinical framing and scalability

There is **no approved disease-modifying therapy** for BUB1B-related MVA1; current
care is symptom management and intensive **cancer surveillance**. A realistic
near-term goal for any of the strategies above is **reduction of ongoing
chromosomal instability**, which could plausibly lower cancer incidence and slow
progression of growth/organ phenotypes; it would not reverse established
aneuploidy in post-mitotic tissue. The most tractable initial context is
**ex vivo / cellular** proof-of-concept in patient-derived cells, followed by the
BubR1^H/H mouse for the stabilisation arm.

**Scalability.** The two mechanisms generalise beyond this patient:
readthrough/NMD-modulation applies to the substantial fraction of MVA1 (and other
recessive) patients carrying a nonsense allele — enrichment for **UGA** PTCs
would prioritise candidates; the NAD⁺/SIRT2 stabilisation arm applies to any
**destabilising hypomorphic** BUBR1 (or, more broadly, MCC-component) allele. A
simple decision rule — "nonsense allele → readthrough arm; destabilising missense
allele → stabilisation arm; compound-het → both" — is directly reusable for other
undiagnosed individuals.

---

## 10. References (verify against primary sources before submission)

1. Musacchio A, Salmon ED. The spindle-assembly checkpoint in space and time.
   *Nat Rev Mol Cell Biol* 2007;8:379–393.
2. Musacchio A. The molecular biology of spindle assembly checkpoint signaling
   dynamics. *Curr Biol* 2015;25:R1002–R1018.
3. Suijkerbuijk SJE, Vleugel M, Teixeira A, Kops GJPL. Integration of kinase and
   phosphatase activities by BUBR1 ensures formation of stable
   kinetochore–microtubule attachments. *Dev Cell* 2012;23:745–755.
4. Hanks S, Coleman K, Reid S, et al. Constitutional aneuploidy and cancer
   predisposition caused by biallelic mutations in BUB1B. *Nat Genet*
   2004;36:1159–1161.
5. Suijkerbuijk SJE, van Osch MHJ, Bos FL, Hanks S, Rahman N, Kops GJPL.
   Molecular causes for BUBR1 dysfunction in the human cancer predisposition
   syndrome mosaic variegated aneuploidy. *Cancer Res* 2010;70:4891–4900.
6. Kurosaki T, Popp MW, Maquat LE. Quality and quantity control of gene
   expression by nonsense-mediated mRNA decay. *Nat Rev Mol Cell Biol*
   2019;20:406–420.
7. Suijkerbuijk SJE, et al. The vertebrate mitotic checkpoint protein BUBR1 is an
   unusual pseudokinase. *Dev Cell* 2012 / Bolanos-Garcia VM, Blundell TL.
   BUB1 and BUBR1: multifaceted kinases of the cell cycle. *Trends Biochem Sci*
   2011;36:141–150.
8. Baker DJ, Jeganathan KB, Cameron JD, et al. BubR1 insufficiency causes early
   onset of aging-associated phenotypes and infertility in mice. *Nat Genet*
   2004;36:744–749.
9. Manuvakhova M, Keeling K, Bedwell DM. Aminoglycoside antibiotics mediate
   context-dependent suppression of termination codons in a mammalian
   translation system. *RNA* 2000;6:1044–1055.
10. Gonzalez-Hilarion S, Beghyn T, Jia J, et al. Rescue of nonsense mutations by
    amlexanox in human cells. *Orphanet J Rare Dis* 2012;7:58.
11. Reilly SM, Chiang S-H, Decker SJ, et al. An inhibitor of the protein kinases
    TBK1 and IKK-ε improves obesity-related metabolic dysfunctions in mice.
    *Nat Med* 2013;19:313–321.
12. McDonald CM, Campbell C, Torricelli RE, et al. Ataluren in patients with
    nonsense mutation Duchenne muscular dystrophy (ACT DMD): a phase 3 trial.
    *Lancet* 2017;390:1489–1498. (See also EMA CHMP opinion, 2025.)
13. Leubitz A, Frydman-Marom A, Sharpe N, et al. Safety, tolerability, and
    pharmacokinetics of single escalating doses of ELX-02. *Clin Pharmacol Drug
    Dev* 2019;8:984–994.
14. Blanchet S, Cornu D, Argentini M, Namy O. New insights into the incorporation
    of natural suppressor tRNAs at stop codons in Saccharomyces cerevisiae.
    *Nucleic Acids Res* 2014;42:10061–10072. (near-cognate insertion at UGA:
    Trp/Arg/Cys)
15. North BJ, Rosenberg MA, Jeganathan KB, et al. SIRT2 induces the checkpoint
    kinase BubR1 to increase lifespan. *EMBO J* 2014;33:1438–1453.
16. Baker DJ, Dawlaty MM, Wijshake T, et al. Increased expression of BubR1
    protects against aneuploidy and cancer and extends healthy lifespan.
    *Nat Cell Biol* 2013;15:96–102.
