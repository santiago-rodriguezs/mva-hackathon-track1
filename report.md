# Mechanism-conditioned drug repurposing for BUB1B-associated chromosome instability

<b>A comparative structural analysis and phase-aware treatment hypothesis for p.Asn1002Lys and p.Leu737Ter</b>

<b>Participants</b><br/>Ian Franco Ghitarroni<br/>Santiago Rodriguez Salinas<br/>Bioinformatics, Universidad Argentina de la Empresa (UADE)<br/>Academic research proposal | 22 October 2026

### Abstract

The reported case carries heterozygous BUB1B c.2210T&gt;G (p.Leu737Ter) and c.3006T&gt;G (p.Asn1002Lys; N1002K). Allele phase and functional measurements are unavailable. We combined a targeted literature review, reference-sequence verification, batch analysis of a public wild-type BUBR1 model, and explicit therapeutic decision rules. N1002K was compared with seven experimentally studied substitutions spanning abundance-related defects, a specific functional defect and assay-tolerated changes. An additional R727C run tested pipeline extension.

N1002 had pLDDT 91.06, solvent-accessible surface area (SASA) 27.46 Å² and selected polar contacts of 2.83–2.95 Å. Its SASA exceeded that at the instability-comparator sites I909 and L1012. A large full-model/domain discrepancy at Q921, but not N1002, exposed sensitivity to modeled domain placement. These findings support a local perturbation hypothesis without establishing mutant destabilization. Twelve stipulated phase/mechanism/transcript scenarios showed that the proposed N1002K-stabilization route depends on the trans configuration and an instability defect with useful residual function.

<b>We propose sodium phenylbutyrate (4-PBA) as the lead repurposed treatment candidate within that stability-rescue branch.</b> NMN is the BUBR1-pathway comparator, TUDCA an alternative proteostasis intervention, and amlexanox a separate premature-stop strategy. No candidate has demonstrated efficacy for this genotype in the evidence reviewed. The decisive endpoint is fewer segregation errors per division, supported by a coherent mechanism at feasible, non-toxic exposure. The contribution is a reproducible method for exposing the assumptions that determine a therapeutic proposal and the experiments that could overturn it.

### Case inputs and scope


| Input | Status |
| --- | --- |
| p.Leu737Ter; reported VAF 0.5435 | Expected premature-termination loss of function; NMD unmeasured. |
| N1002K; reported VAF 0.4643 | Functional effect unresolved; partial loss of function is a working hypothesis. |
| Phase, functional assays and treatment response | Unavailable. Neither compound heterozygosity nor clinical rescue is asserted. |


## 1. Mechanism and competing genetic explanations

### 1.1 The causal mechanism to be tested

BUB1B encodes BUBR1. BUBR1 contributes to mitotic checkpoint complex (MCC) restraint of APC/C–CDC20 and to kinetochore attachment regulation. The C-terminal pseudokinase supports KARD phosphorylation and PP2A-B56 recruitment; defects can impair alignment and checkpoint silencing. Consequently, a regulatory defect may prolong mitosis, while a deficient checkpoint may permit premature progression. Mitotic duration alone cannot identify rescue. [1,2]

<b>p.Leu737Ter:</b> c.2210T&gt;G changes TTA to TGA. Translation terminating at residue 737 would yield 736 residues and remove 314 residues, including N1002. Reduced transcript through nonsense-mediated decay (NMD) is plausible but unmeasured; neither complete null behavior nor dominant-negative activity is assumed.

<b>N1002K:</b> c.3006T&gt;G changes AAT to AAG. Replacing asparagine with lysine changes side-chain length, charge and donor/acceptor chemistry. Candidate mechanisms are impaired stability, a specific regulatory defect, or a tolerated substitution. The proposed disease-relevant mechanism is partial loss of function; reviewed evidence does not establish gain of function or variant pathogenicity.

If functional BUBR1 is insufficient, impaired chromosome segregation could increase aneuploidy and micronuclei, with downstream cell loss, senescence or tissue dysfunction. The treatment objective is to reduce ongoing segregation errors, rather than merely increase protein or suppress cell death.

### 1.2 Phase changes the biological substrate


| Configuration | Implication for the hypothesis |
| --- | --- |
| Trans: p.Leu737Ter / N1002K | A full-length N1002K product can be the stabilization target if expressed. The stop allele provides a distinct readthrough target. |
| Cis: [p.Leu737Ter; N1002K] / other allele | Ordinary translation stops before N1002. N1002K is not expressed from that allele unless translation bypasses the stop. The other allele and alternative genetic explanations require evaluation. |
| N1002K is tolerated | Its proposed contribution to disease and the N1002K-directed rescue rationale must be reconsidered. |
| N1002K has a stable but functionally defective product | An abundance-directed intervention is insufficient unless function improves independently. |

Both phase configurations are retained throughout. Classical BUB1B-associated MVA follows a recessive model; these calls alone do not establish a biallelic molecular diagnosis. [1] Similar heterozygous variant allele fractions do not determine phase. No probabilities are assigned to these scenarios.


## 2. Materials and completed computational methods

### 2.1 Evidence selection and comparison design

A targeted, non-systematic review used PubMed-indexed primary studies, public reference databases and official drug information. Search terms included “BUB1B N1002K”, “BUBR1 I909T L1012P”, “BUBR1 Y155C Q921H”, “SIRT2 BubR1 NMN” and candidate-specific terms. Comparator selection sought contrasting experimental phenotypes, not a representative clinical cohort. Seven comparators were chosen from a functional study; its assay context was retained rather than converted to clinical benign/pathogenic labels. [1]

### 2.2 Reference and model validation

The 3,153-nucleotide RefSeq NM_001211.6 CDS was translated and matched exactly to the 1,050-residue UniProt O60566 sequence plus terminal stop. Reported codons and comparator reference residues were checked. The AlphaFold AF-O60566-F1 v6 model had complete Cα coverage. Sequence checks validate annotation consistency, not the individual sequencing calls. Inputs and SHA-256 hashes are supplied. [7–9]

### 2.3 Reusable structural measurements

For each submitted position, Python calculated WT Cα pLDDT, total and side-chain SASA, and numbers of Cα neighbors within 8 and 10 Å. SASA used a deterministic Shrake–Rupley-style algorithm with 960 and 1,920 Fibonacci sphere points per atom, a 1.4 Å probe, and radii C=1.70, N=1.55, O=1.52 and S=1.80 Å. The C-terminal sites were recalculated with only residues 740–1050 as occluders to test sensitivity to full-model domain placement. [10]

Absolute SASA depends on residue chemistry and is not a standardized relative accessibility score. Neighbor counts describe packing, not interaction strength. N1002 OD1/ND2 distances to non-self N/O/S atoms within 4 Å were measured; proximity without hydrogen orientation does not establish hydrogen bonding. pLDDT assesses local WT model confidence, not pathogenicity or mutant stability.

### 2.4 Scenario sensitivity and software verification

The decision module enumerated 2 phases × 3 assumed missense mechanisms × 2 stop-transcript states = 12 scenarios. The mechanisms were instability with useful residual function, a specific functional defect, and tolerance. Transcript availability is a hypothetical experimental finding. Rules assign experimental roles to candidates; they do not estimate efficacy or score drugs. All scenarios are deliberately unweighted.

The completed run used Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0. Cached-input analysis of eight sites and the scenario grid took 0.338 seconds on the available CPU environment. Retrieval, review and document production are excluded. No GPU, mutant relaxation, ΔΔG, docking, molecular dynamics or biological rescue experiment was used.


## 3. Comparative structural results

![Comparative structural measurements](../analysis/results/comparison.png)

<b>Figure 1. WT structural context across the comparison panel.</b> Filled points use the full model; open points use residues 740–1050 only. Colors identify the case (ochre), instability/low abundance (red), specific functional defect (purple), and assay-tolerated comparators (teal). These are literature contexts, not predicted classes. R550 has low local model confidence. SASA is on a logarithmic axis.


| Variant | WT pLDDT | Full SASA, Å² | Domain SASA, Å² | Cα neighbors ≤8 Å |
| --- | --- | --- | --- | --- |
| N1002K | 91.06 | 27.46 | 27.46 | 8 |
| I909T | 87.00 | 7.26 | 7.26 | 8 |
| L1012P | 95.31 | 0.76 | 0.76 | 12 |
| R814H | 90.25 | 44.19 | 44.19 | 7 |
| L844F | 85.88 | 1.13 | 1.13 | 11 |
| Y155C | 96.31 | 1.88 | Not applicable | 13 |
| R550Q | 35.31 | 220.73 | Not applicable | 4 |
| Q921H | 83.25 | 3.64 | 69.36 | 9 |

### 3.1 What the comparison supports

N1002 SASA was 27.46 Å², compared with 7.26 Å² at I909 and 0.76 Å² at L1012. N1002 therefore does not reproduce the burial of these two instability-comparator sites. Its measured side-chain SASA was 16.31 Å². The local chemistry remains relevant, but burial alone cannot establish that N1002K is unstable.

N1002 OD1–W978 backbone N, ND2–V998 backbone O and ND2–W978 backbone O distances were 2.825, 2.827 and 2.948 Å. These are atomic distances, not Cα distances. The modeled polar environment motivates testing altered local interactions; lysine accommodation remains possible.


## 4. Comparator evidence and model sensitivity


| Comparator | Published assay context [1] | Role in this analysis |
| --- | --- | --- |
| I909T; L1012P | Instability; abundance-matched checkpoint rescue. | Positive mechanistic comparators for a residual-function hypothesis. |
| R814H; L844F | Reduced abundance in replacement assays. | Additional abundance-related comparators. |
| Y155C | Stable expression; checkpoint-selective defect. | Counterexample to treating abundance as equivalent to function. |
| R550Q; Q921H | WT-like tested functions under the reported conditions. | Assay-tolerated comparators; not clinical benign controls. |

### 4.1 A useful counterexample

Q921H provides a within-domain comparator whose experimental context contrasts with instability. Its WT site is poorly exposed in the full model (3.64 Å²), so low SASA cannot be treated as a sufficient instability classifier. The small, selected panel is an interpretive comparison, not a validated predictive benchmark; no accuracy, AUC or significance claim is made.

### 4.2 Domain-placement sensitivity changes interpretation

Q921 SASA increased from 3.64 to 69.36 Å² when regions outside 740–1050 were removed, a difference of 65.72 Å². That result flags dependence on inter-region occlusion in the full model. It does not prove which geometry is biologically correct. Long-range packing in a monomer prediction requires additional evidence, such as inter-domain confidence and experimental context, before mechanistic use.

N1002 remained 27.46 Å² in both contexts. Increasing sphere sampling from 960 to 1,920 points changed its SASA by 0.27 Å². Across the eight-site panel, the largest absolute sampling difference was 0.84 Å². These checks establish numerical and selected-context consistency, not stability across conformational ensembles.

### 4.3 Consequence for candidate selection

<b>The added comparison does not establish a stability defect in N1002K.</b> It narrows the proposal to a conditional rescue experiment and prevents us from presenting structural similarity as proof. The strongest next discriminator is a direct comparison of mutant abundance, turnover and function at matched expression.

Published allelic models also caution against extrapolating outcome from protein quantity alone. In mice, the counterpart of human L1012P is L1002P; it is not human N1002K. Allelic context affected phenotype, supporting genotype-matched validation rather than transfer of a treatment claim between similarly numbered residues. [3]


## 5. Mechanism-to-candidate treatment proposal

<b>Primary hypothesis:</b> if full-length N1002K is expressed and retains mitotic activity but is depleted by impaired proteostasis, 4-PBA can increase the available functional pool and reduce chromosome-segregation errors. This is the lead approved-drug repurposing hypothesis for that branch, rather than a mechanism-independent ranking.


| Candidate / role | Evidence proximity and rationale | Decisive test / limitation |
| --- | --- | --- |
| 4-PBA: conditional lead | Medicinal use in urea-cycle disorders; indirect proteostasis rationale. [5,6] | Mutant turnover/solubility and segregation must improve at feasible exposure. No BUBR1-specific rescue demonstrated. |
| NMN: pathway comparator | NAD+/SIRT2 intervention increased BubR1 abundance in published experiments. [4] | Test SIRT2 dependence and mitotic function. Greater pathway proximity does not establish N1002K efficacy or approved-drug status. |
| TUDCA: alternative | Proteostasis/stress effects in non-BUBR1 systems. [5] | Test independently; effects cannot be assumed equivalent to PBA or direct binding. |
| Amlexanox: separate stop-allele branch | Nonsense suppression/NMD modulation in other human-cell systems. [11] | Require endogenous full-length product and functional rescue; outcome depends on context and the recovered amino acid. |

### 5.1 Why the evidence does not produce a universal winner

NMN has closer BUBR1-pathway evidence; 4-PBA offers a medicinal starting point for an instability-specific repurposing experiment. These are different advantages. We retain 4-PBA as a conditional lead because of the proposed intervention mechanism, not because it has a stronger demonstrated BUBR1 effect. No quantitative efficacy ranking is justified.

Evidence from stress/aggregation systems shows different behavior of TUDCA and PBA. It supplies a reason to test substrate dependence and argues against a blanket chaperone-rescue claim. 4-PBA may also alter expression through pleiotropic actions; BUB1B RNA and protein turnover must be measured separately. [5]

### 5.2 Prediction and falsification

The predicted treatment response is improved segregation fidelity accompanied by recovery of a functional BUBR1 pool. Increased protein without improved function, rescue confined to toxic or implausible exposure, or apparent benefit explained by slowed division or cell death would reject advancement. Existing medicinal use supplies feasibility context, not efficacy or a dose for this indication. [6]


## 6. Sensitivity of the proposal to missing information

The completed scenario analysis exposes dependencies rather than filling missing data with favorable assumptions. Two transcript states were applied to each of the six phase/mechanism combinations below; the full 12-row output is in the supplement.


| Phase / assumed mechanism | N1002K-directed proteostasis route | Premature-stop route if transcript is detectable |
| --- | --- | --- |
| Trans / instability with residual function | 4-PBA lead; NMN and TUDCA comparators. | Amlexanox exploratory. |
| Trans / specific functional defect | Stabilization rationale not established. | Amlexanox exploratory; recovery must bypass the defective missense allele functionally. |
| Trans / tolerated missense | N1002K-directed route unsupported; reconsider genetic explanation. | Readthrough remains exploratory, not proof that the pair explains disease. |
| Cis / instability hypothesis | No ordinary full-length N1002K substrate from the stop-bearing allele. | Readthrough could yield N1002K-containing protein; function unresolved. |
| Cis / specific functional defect | No justified standalone stabilization route. | Length recovery may leave a functional defect. |
| Cis / tolerated missense | No N1002K-specific rescue rationale. | Recovered product still requires functional validation. |

If no stop transcript is detected, the readthrough branch is deprioritized pending evaluation of assay sensitivity, RNA expression and whether NMD modulation creates a usable substrate. A negative baseline RNA assay does not prove permanent biological absence of a substrate.

### 6.1 What the enumeration means

The specified 4-PBA route appears in 2 of 12 scenarios: both transcript states under trans plus instability with useful residual function. This fraction is not a response probability, a confidence estimate or a frequency in MVA. The number depends on how scenarios are defined. The current case cannot be assigned to a successful branch because the required measurements are absent.

### 6.2 Evidence-ablation interpretation

Removing the instability assumption eliminates the defined 4-PBA route. Changing trans to cis removes its ordinary full-length substrate. Changing stop-transcript availability affects the amlexanox branch. Removing WT contact geometry weakens structural motivation but cannot, by itself, overturn a measured cellular defect. This sensitivity makes the proposal auditable rather than pretending that one drug remains optimal under every explanation.


## 7. Proposed functional validation and advancement rules

### 7.1 Models and controls — proposed, not performed

Start with available case-derived cells and matched controls if access becomes possible. Build endogenous isogenic genotypes to compare WT/WT, p.Leu737Ter/WT, N1002K/WT, trans p.Leu737Ter/N1002K and cis [p.Leu737Ter; N1002K]/WT. These are model scenarios, not claims about this child. Include corrected lines or controlled WT complementation, multiple independent clones and vehicle controls. Endogenous models are needed to preserve transcript processing and NMD; cDNA overexpression alone cannot test those mechanisms.

### 7.2 Distinguish abundance, function and general cytoprotection


| Question | Proposed measurement | Interpretation |
| --- | --- | --- |
| Is the defect a depleted pool? | Allele-specific RNA; total/soluble full-length BUBR1; protein turnover. | Distinguishes transcript changes from protein stabilization. |
| Is regulation impaired? | Kinetochore localization; KARD phosphorylation; PP2A-B56 recruitment; checkpoint response. | Tests mechanism beyond protein quantity. |
| Does treatment restore fidelity? | Live-cell scoring of lagging chromosomes, bridges and failed divisions; primary rate per observed anaphase. | Analyze complete cell trajectories and attempted divisions to avoid survivor-only bias. |
| Is apparent benefit misleading? | Mitotic entry, duration, proliferation, apoptosis, micronuclei and ploidy over time. | Excludes cytostasis, selective death or expansion of unstable survivors. |

Test each candidate separately across concentration and exposure windows, with blinded image scoring. A pilot with multiple independent clones and culture-day replicates should estimate variability for power planning. Cells within one culture are nested observations, not independent biological replicates. Report absolute risk differences or risk ratios and uncertainty using a model that accounts for experiment and clone clustering.

### 7.3 Advance, revise or stop

<b>Advance:</b> reproducible improvement in the primary functional endpoint with coherent supporting biology, plausible unbound exposure and no harmful WT effect. <b>Revise:</b> protein increases without functional rescue or only stress/viability improves. <b>Stop/deprioritize:</b> no reproducible genotype-associated defect, benefit only at toxic exposure, increased polyploidy/unstable-cell expansion, or an effect limited to one clone. Meaningful effect thresholds must be set before confirmatory experiments using pilot variance and biological relevance, not invented from the current computation.


## 8. Potential impact and methodological contribution

### 8.1 Value for this case

The immediate value is to prioritize the observations that change action: allele phase, full-length transcript/protein availability, and whether low abundance or impaired regulation drives the defect. If an instability phenotype with residual function is validated, the study supplies a focused 4-PBA experiment with functional success criteria. If N1002K is tolerated, it redirects the genetic explanation rather than preserving a drug hypothesis at all costs.

### 8.2 Value for other individuals with MVA

The transferable unit is a mechanism-defined subgroup: expressed, function-retaining but unstable BUBR1. A validated rescue in one genotype would motivate testing other members of that subgroup; it would not establish efficacy across BUB1B-MVA, let alone MVA caused by other genes. The comparator panel makes explicit why similar protein abundance or domain location need not imply the same phenotype or response.

The framework could help choose functional tests for uncertain variants and interpret negative therapeutic experiments. It does not itself provide a formal clinical variant classification. Diagnostic benefit would require independent validation against clinical and functional evidence; a model-derived contact or SASA value is not diagnostic proof.

### 8.3 Innovation delivered in this submission

The contribution is an integrated, reproducible workflow combining comparator-aware structural interpretation, full-model/domain sensitivity and phase-conditioned candidate routing. Its creative feature is treating uncertainty as a variable that changes the proposed experiment. It uses assay-tolerated and functional-defect comparators to challenge, rather than merely reinforce, the lead hypothesis.

The analysis adds a concrete counterexample to burial-based reasoning and identifies context-sensitive structural exposure. The innovation is methodological integration and decision transparency, not a new SASA algorithm, a trained drug-response model or discovery of a proven therapy. A selected eight-site panel cannot validate predictive generalization.

### 8.4 Value of a negative result

If 4-PBA raises BUBR1 but not segregation fidelity, the result discriminates abundance rescue from functional rescue. If no genotype-associated defect is reproduced, the N1002K mechanism must be reconsidered. Either outcome can improve subsequent diagnosis-oriented experiments and prevent a resource-intensive drug program from advancing on an insufficient surrogate.


## 9. Scalability, limitations and final proposal

### 9.1 Demonstrated reuse and realistic scale

The supplied CLI accepts a variant CSV, validates reference residues and emits measurement tables, atomic contacts, a scenario table and a provenance summary. The main run processed N1002K plus seven comparators. A separate, previously unlisted R727C input completed successfully without changing the analysis code. This demonstrates input extension, not independent biological validation. A deliberately incorrect reference residue was rejected, and decision-rule boundary cases were checked.

The PDB is parsed once per run and geometry is reused. More individuals sharing a variant can reuse those measurements while retaining separate genotype and phase records; literature curation and biological assays remain the bottlenecks. The observed sub-second runtime is a small cached CPU workload, not a benchmark for population-scale analysis. Source retrieval, parallel deployment and large-dataset throughput were not measured.

Applying this to another gene requires a verified reference transcript, model and domain boundaries, experimentally grounded comparators and new gene-specific intervention rules. Current code is deliberately BUB1B-specific. The reusable data structure and computational components are portable; the therapeutic logic is not automatically transferable.

### 9.2 Material limitations

No phase, raw sequencing reads, functional assays or patient treatment outcomes are available. The static WT model omits partners, conformational ensembles and mutant side-chain accommodation. Domain removal tests one source of uncertainty, not all structural uncertainty. The selected comparison panel lacks an independent test set and does not support clinical classification, causal attribution or drug-response prediction.

Translation would require endogenous functional rescue, exposure/toxicity assessment and appropriate clinical review. Existing developmental effects and established aneuploid cell populations may persist even if new errors decrease. Increasing survival of genomically unstable cells would not meet the therapeutic objective. No human dose or drug combination is proposed.

### Final treatment hypothesis

<b>We propose 4-PBA as the lead repurposed treatment experiment for an expressed, stability-impaired N1002K allele with useful residual function.</b> The current evidence supports testing that mechanism, not asserting it. NMN is the closest pathway comparator, TUDCA tests alternative proteostasis modulation, and amlexanox independently addresses the premature-stop branch. The next decisive result is recovery of segregation fidelity in the relevant genotype at feasible, non-toxic exposure. The phase-aware analysis specifies when to advance this proposal and when to change it.


## References and reproducibility

<b>[1]</b> Suijkerbuijk SJE et al. Molecular causes for BUBR1 dysfunction in the human cancer predisposition syndrome mosaic variegated aneuploidy. Cancer Res. 2010;70:4891–4900. [Source](https://doi.org/10.1158/0008-5472.CAN-09-4319).

<b>[2]</b> Gama Braga L et al. BUBR1 pseudokinase domain promotes kinetochore PP2A-B56 recruitment, spindle checkpoint silencing, and chromosome alignment. Cell Rep. 2020;33:108397. [Source](https://doi.org/10.1016/j.celrep.2020.108397).

<b>[3]</b> Sieben CJ et al. BubR1 allelic effects drive phenotypic heterogeneity in mosaic-variegated aneuploidy progeria syndrome. J Clin Invest. 2020;130:171–188. [Source](https://doi.org/10.1172/JCI126863).

<b>[4]</b> North BJ et al. SIRT2 induces the checkpoint kinase BubR1 to increase lifespan. EMBO J. 2014;33:1438–1453. [Source](https://doi.org/10.15252/embj.201386907).

<b>[5]</b> Uppala JK et al. Chemical chaperone, TUDCA unlike PBA, mitigates protein aggregation efficiently and resists ER and non-ER stress induced HepG2 cell death. Sci Rep. 2017;7:3831. [Source](https://doi.org/10.1038/s41598-017-03940-1).

<b>[6]</b> DailyMed. Sodium phenylbutyrate tablets: official prescribing information. Existing indication and exposure/safety context. [Source](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d08fd548-7eb8-4f6f-b664-b0fff6f30065).

<b>[7]</b> UniProt. O60566, BUB1B_HUMAN canonical sequence. [Source](https://rest.uniprot.org/uniprotkb/O60566.fasta).

<b>[8]</b> NCBI RefSeq. NM_001211.6 / NP_001202.5, BUB1B coding sequence and protein. [Source](https://www.ncbi.nlm.nih.gov/nuccore/NM_001211.6).

<b>[9]</b> AlphaFold Protein Structure Database. O60566; analyzed file AF-O60566-F1-model_v6.pdb. [Source](https://alphafold.ebi.ac.uk/entry/O60566).

<b>[10]</b> Shrake A, Rupley JA. Environment and exposure to solvent of protein atoms. Lysozyme and insulin. J Mol Biol. 1973;79:351–371. [Source](https://pubmed.ncbi.nlm.nih.gov/4760134/).

<b>[11]</b> Gonzalez-Hilarion S et al. Rescue of nonsense mutations by amlexanox in human cells. Orphanet J Rare Dis. 2012;7:58. [Source](https://doi.org/10.1186/1750-1172-7-58).

### Reproduction and status of work

The computational supplement includes input FASTA/CDS/PDB files, comparator annotations, executable Python analysis, CSV/JSON results, plotting code and instructions. Sources were accessed on 22 October 2026. The methods workbook records completed computational procedures separately from proposed biological work. No raw patient reads or identifiable clinical records are included.

<b>AI assistance:</b> OpenAI ChatGPT was used for retrieval, synthesis, programming and drafting. Scripts produced the numerical results. This does not constitute independent human expert or clinical validation. No unperformed simulation or biological experiment is reported.
