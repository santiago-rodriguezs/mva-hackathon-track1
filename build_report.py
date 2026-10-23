from pathlib import Path
import csv,json
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import argparse
ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description='Rebuild the 11-page analysis report (not the separately submitted team addendum).')
parser.add_argument('--output-dir', type=Path, default=ROOT/'rebuilt')
args = parser.parse_args()
R = args.output_dir.resolve(); R.mkdir(parents=True, exist_ok=True)
SROOT = ROOT.parent/'analysis'
rows=list(csv.DictReader((SROOT/'results/variant_context.csv').open()))
summary=json.loads((SROOT/'results/summary.json').read_text())
pdfmetrics.registerFont(TTFont('DV',str(ROOT/'fonts/DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DVB',str(ROOT/'fonts/DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DVB',italic='DV',boldItalic='DVB')
st=getSampleStyleSheet()
for name,size,lead,extra in [('Body',9.2,13.5,{'spaceAfter':8}),('TitleX',22,27,{'fontName':'DVB','spaceAfter':16,'textColor':colors.HexColor('#18354b')}),('H1X',16,21,{'fontName':'DVB','spaceAfter':12,'textColor':colors.HexColor('#18354b')}),('H2X',10.5,14,{'fontName':'DVB','spaceBefore':8,'spaceAfter':6}),('SmallX',7.8,10.8,{'spaceAfter':6}),('CellX',7.8,10.7,{})]:
 st.add(ParagraphStyle(name=name,fontName=extra.pop('fontName','DV'),fontSize=size,leading=lead,**extra))
flow=[];md=[]
def p(t):flow.append(Paragraph(t,st['Body']));md.append(t+'\n')
def h(t):flow.append(Paragraph(t,st['H2X']));md.append('### '+t+'\n')
def page(t):
 if flow:flow.append(PageBreak())
 flow.append(Paragraph(t,st['H1X']));md.append('\n## '+t+'\n')
def table(data,widths):
 t=Table([[Paragraph(escape(str(c)),st['CellX']) for c in row] for row in data],colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#7993a7')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d6dfe5')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));flow.append(t);flow.append(Spacer(1,5))
 md.append('\n'+'\n'.join('| '+' | '.join(str(x) for x in row)+' |' for row in [data[0],['---']*len(data[0])]+data[1:])+'\n')
def small(t):flow.append(Paragraph(t,st['SmallX']));md.append(t+'\n')
flow.append(Paragraph('Mechanism-conditioned drug repurposing for BUB1B-associated chromosome instability',st['TitleX']))
p('<b>A comparative structural analysis and phase-aware treatment hypothesis for p.Asn1002Lys and p.Leu737Ter</b>')
p('<b>Participants</b><br/>Ian Franco Ghitarroni<br/>Santiago Rodriguez Salinas<br/>Bioinformatics, Universidad Argentina de la Empresa (UADE)<br/>Academic research proposal | 22 October 2026')
h('Abstract')
p('The reported case carries heterozygous BUB1B c.2210T&gt;G (p.Leu737Ter) and c.3006T&gt;G (p.Asn1002Lys; N1002K). Allele phase and functional measurements are unavailable. We combined a targeted literature review, reference-sequence verification, batch analysis of a public wild-type BUBR1 model, and explicit therapeutic decision rules. N1002K was compared with seven experimentally studied substitutions spanning abundance-related defects, a specific functional defect and assay-tolerated changes. An additional R727C run tested pipeline extension.')
p('N1002 had pLDDT 91.06, solvent-accessible surface area (SASA) 27.46 Å² and selected polar contacts of 2.83–2.95 Å. Its SASA exceeded that at the instability-comparator sites I909 and L1012. A large full-model/domain discrepancy at Q921, but not N1002, exposed sensitivity to modeled domain placement. These findings support a local perturbation hypothesis without establishing mutant destabilization. Twelve stipulated phase/mechanism/transcript scenarios showed that the proposed N1002K-stabilization route depends on the trans configuration and an instability defect with useful residual function.')
p('<b>We propose sodium phenylbutyrate (4-PBA) as the lead repurposed treatment candidate within that stability-rescue branch.</b> NMN is the BUBR1-pathway comparator, TUDCA an alternative proteostasis intervention, and amlexanox a separate premature-stop strategy. No candidate has demonstrated efficacy for this genotype in the evidence reviewed. The decisive endpoint is fewer segregation errors per division, supported by a coherent mechanism at feasible, non-toxic exposure. The contribution is a reproducible method for exposing the assumptions that determine a therapeutic proposal and the experiments that could overturn it.')
h('Case inputs and scope')
table([['Input','Status'],['p.Leu737Ter; reported VAF 0.5435','Expected premature-termination loss of function; NMD unmeasured.'],['N1002K; reported VAF 0.4643','Functional effect unresolved; partial loss of function is a working hypothesis.'],['Phase, functional assays and treatment response','Unavailable. Neither compound heterozygosity nor clinical rescue is asserted.']],[220,263])

page('1. Mechanism and competing genetic explanations')
h('1.1 The causal mechanism to be tested')
p('BUB1B encodes BUBR1. BUBR1 contributes to mitotic checkpoint complex (MCC) restraint of APC/C–CDC20 and to kinetochore attachment regulation. The C-terminal pseudokinase supports KARD phosphorylation and PP2A-B56 recruitment; defects can impair alignment and checkpoint silencing. Consequently, a regulatory defect may prolong mitosis, while a deficient checkpoint may permit premature progression. Mitotic duration alone cannot identify rescue. [1,2]')
p('<b>p.Leu737Ter:</b> c.2210T&gt;G changes TTA to TGA. Translation terminating at residue 737 would yield 736 residues and remove 314 residues, including N1002. Reduced transcript through nonsense-mediated decay (NMD) is plausible but unmeasured; neither complete null behavior nor dominant-negative activity is assumed.')
p('<b>N1002K:</b> c.3006T&gt;G changes AAT to AAG. Replacing asparagine with lysine changes side-chain length, charge and donor/acceptor chemistry. Candidate mechanisms are impaired stability, a specific regulatory defect, or a tolerated substitution. The proposed disease-relevant mechanism is partial loss of function; reviewed evidence does not establish gain of function or variant pathogenicity.')
p('If functional BUBR1 is insufficient, impaired chromosome segregation could increase aneuploidy and micronuclei, with downstream cell loss, senescence or tissue dysfunction. The treatment objective is to reduce ongoing segregation errors, rather than merely increase protein or suppress cell death.')
h('1.2 Phase changes the biological substrate')
table([['Configuration','Implication for the hypothesis'],['Trans: p.Leu737Ter / N1002K','A full-length N1002K product can be the stabilization target if expressed. The stop allele provides a distinct readthrough target.'],['Cis: [p.Leu737Ter; N1002K] / other allele','Ordinary translation stops before N1002. N1002K is not expressed from that allele unless translation bypasses the stop. The other allele and alternative genetic explanations require evaluation.'],['N1002K is tolerated','Its proposed contribution to disease and the N1002K-directed rescue rationale must be reconsidered.'],['N1002K has a stable but functionally defective product','An abundance-directed intervention is insufficient unless function improves independently.']],[163,320])
p('Both phase configurations are retained throughout. Classical BUB1B-associated MVA follows a recessive model; these calls alone do not establish a biallelic molecular diagnosis. [1] Similar heterozygous variant allele fractions do not determine phase. No probabilities are assigned to these scenarios.')

page('2. Materials and completed computational methods')
h('2.1 Evidence selection and comparison design')
p('A targeted, non-systematic review used PubMed-indexed primary studies, public reference databases and official drug information. Search terms included “BUB1B N1002K”, “BUBR1 I909T L1012P”, “BUBR1 Y155C Q921H”, “SIRT2 BubR1 NMN” and candidate-specific terms. Comparator selection sought contrasting experimental phenotypes, not a representative clinical cohort. Seven comparators were chosen from a functional study; its assay context was retained rather than converted to clinical benign/pathogenic labels. [1]')
h('2.2 Reference and model validation')
p('The 3,153-nucleotide RefSeq NM_001211.6 CDS was translated and matched exactly to the 1,050-residue UniProt O60566 sequence plus terminal stop. Reported codons and comparator reference residues were checked. The AlphaFold AF-O60566-F1 v6 model had complete Cα coverage. Sequence checks validate annotation consistency, not the individual sequencing calls. Inputs and SHA-256 hashes are supplied. [7–9]')
h('2.3 Reusable structural measurements')
p('For each submitted position, Python calculated WT Cα pLDDT, total and side-chain SASA, and numbers of Cα neighbors within 8 and 10 Å. SASA used a deterministic Shrake–Rupley-style algorithm with 960 and 1,920 Fibonacci sphere points per atom, a 1.4 Å probe, and radii C=1.70, N=1.55, O=1.52 and S=1.80 Å. The C-terminal sites were recalculated with only residues 740–1050 as occluders to test sensitivity to full-model domain placement. [10]')
p('Absolute SASA depends on residue chemistry and is not a standardized relative accessibility score. Neighbor counts describe packing, not interaction strength. N1002 OD1/ND2 distances to non-self N/O/S atoms within 4 Å were measured; proximity without hydrogen orientation does not establish hydrogen bonding. pLDDT assesses local WT model confidence, not pathogenicity or mutant stability.')
h('2.4 Scenario sensitivity and software verification')
p('The decision module enumerated 2 phases × 3 assumed missense mechanisms × 2 stop-transcript states = 12 scenarios. The mechanisms were instability with useful residual function, a specific functional defect, and tolerance. Transcript availability is a hypothetical experimental finding. Rules assign experimental roles to candidates; they do not estimate efficacy or score drugs. All scenarios are deliberately unweighted.')
p('The completed run used Python '+summary['python']+', NumPy '+summary['numpy']+' and SciPy '+summary['scipy']+'. Cached-input analysis of eight sites and the scenario grid took '+f"{summary['runtime_seconds']:.3f}"+' seconds on the available CPU environment. Retrieval, review and document production are excluded. No GPU, mutant relaxation, ΔΔG, docking, molecular dynamics or biological rescue experiment was used.')

page('3. Comparative structural results')
flow.append(Image(str(SROOT/'results/comparison.png'),width=483,height=212))
small('<b>Figure 1. WT structural context across the comparison panel.</b> Filled points use the full model; open points use residues 740–1050 only. Colors identify the case (ochre), instability/low abundance (red), specific functional defect (purple), and assay-tolerated comparators (teal). These are literature contexts, not predicted classes. R550 has low local model confidence. SASA is on a logarithmic axis.')
data=[['Variant','WT pLDDT','Full SASA, Å²','Domain SASA, Å²','Cα neighbors ≤8 Å']]
for r in rows:
 data.append([r['variant'],f"{float(r['plddt']):.2f}",f"{float(r['sasa_1920_A2']):.2f}",f"{float(r['domain_sasa_A2']):.2f}" if r['domain_sasa_A2'] else 'Not applicable',r['CA_neighbors_8A']])
table(data,[85,87,100,111,100])
h('3.1 What the comparison supports')
p('N1002 SASA was 27.46 Å², compared with 7.26 Å² at I909 and 0.76 Å² at L1012. N1002 therefore does not reproduce the burial of these two instability-comparator sites. Its measured side-chain SASA was 16.31 Å². The local chemistry remains relevant, but burial alone cannot establish that N1002K is unstable.')
p('N1002 OD1–W978 backbone N, ND2–V998 backbone O and ND2–W978 backbone O distances were 2.825, 2.827 and 2.948 Å. These are atomic distances, not Cα distances. The modeled polar environment motivates testing altered local interactions; lysine accommodation remains possible.')

page('4. Comparator evidence and model sensitivity')
table([['Comparator','Published assay context [1]','Role in this analysis'],['I909T; L1012P','Instability; abundance-matched checkpoint rescue.','Positive mechanistic comparators for a residual-function hypothesis.'],['R814H; L844F','Reduced abundance in replacement assays.','Additional abundance-related comparators.'],['Y155C','Stable expression; checkpoint-selective defect.','Counterexample to treating abundance as equivalent to function.'],['R550Q; Q921H','WT-like tested functions under the reported conditions.','Assay-tolerated comparators; not clinical benign controls.']],[110,193,180])
h('4.1 A useful counterexample')
p('Q921H provides a within-domain comparator whose experimental context contrasts with instability. Its WT site is poorly exposed in the full model (3.64 Å²), so low SASA cannot be treated as a sufficient instability classifier. The small, selected panel is an interpretive comparison, not a validated predictive benchmark; no accuracy, AUC or significance claim is made.')
h('4.2 Domain-placement sensitivity changes interpretation')
p('Q921 SASA increased from 3.64 to 69.36 Å² when regions outside 740–1050 were removed, a difference of 65.72 Å². That result flags dependence on inter-region occlusion in the full model. It does not prove which geometry is biologically correct. Long-range packing in a monomer prediction requires additional evidence, such as inter-domain confidence and experimental context, before mechanistic use.')
p('N1002 remained 27.46 Å² in both contexts. Increasing sphere sampling from 960 to 1,920 points changed its SASA by 0.27 Å². Across the eight-site panel, the largest absolute sampling difference was 0.84 Å². These checks establish numerical and selected-context consistency, not stability across conformational ensembles.')
h('4.3 Consequence for candidate selection')
p('<b>The added comparison does not establish a stability defect in N1002K.</b> It narrows the proposal to a conditional rescue experiment and prevents us from presenting structural similarity as proof. The strongest next discriminator is a direct comparison of mutant abundance, turnover and function at matched expression.')
p('Published allelic models also caution against extrapolating outcome from protein quantity alone. In mice, the counterpart of human L1012P is L1002P; it is not human N1002K. Allelic context affected phenotype, supporting genotype-matched validation rather than transfer of a treatment claim between similarly numbered residues. [3]')

page('5. Mechanism-to-candidate treatment proposal')
p('<b>Primary hypothesis:</b> if full-length N1002K is expressed and retains mitotic activity but is depleted by impaired proteostasis, 4-PBA can increase the available functional pool and reduce chromosome-segregation errors. This is the lead approved-drug repurposing hypothesis for that branch, rather than a mechanism-independent ranking.')
table([['Candidate / role','Evidence proximity and rationale','Decisive test / limitation'],['4-PBA: conditional lead','Medicinal use in urea-cycle disorders; indirect proteostasis rationale. [5,6]','Mutant turnover/solubility and segregation must improve at feasible exposure. No BUBR1-specific rescue demonstrated.'],['NMN: pathway comparator','NAD+/SIRT2 intervention increased BubR1 abundance in published experiments. [4]','Test SIRT2 dependence and mitotic function. Greater pathway proximity does not establish N1002K efficacy or approved-drug status.'],['TUDCA: alternative','Proteostasis/stress effects in non-BUBR1 systems. [5]','Test independently; effects cannot be assumed equivalent to PBA or direct binding.'],['Amlexanox: separate stop-allele branch','Nonsense suppression/NMD modulation in other human-cell systems. [11]','Require endogenous full-length product and functional rescue; outcome depends on context and the recovered amino acid.']],[112,187,184])
h('5.1 Why the evidence does not produce a universal winner')
p('NMN has closer BUBR1-pathway evidence; 4-PBA offers a medicinal starting point for an instability-specific repurposing experiment. These are different advantages. We retain 4-PBA as a conditional lead because of the proposed intervention mechanism, not because it has a stronger demonstrated BUBR1 effect. No quantitative efficacy ranking is justified.')
p('Evidence from stress/aggregation systems shows different behavior of TUDCA and PBA. It supplies a reason to test substrate dependence and argues against a blanket chaperone-rescue claim. 4-PBA may also alter expression through pleiotropic actions; BUB1B RNA and protein turnover must be measured separately. [5]')
h('5.2 Prediction and falsification')
p('The predicted treatment response is improved segregation fidelity accompanied by recovery of a functional BUBR1 pool. Increased protein without improved function, rescue confined to toxic or implausible exposure, or apparent benefit explained by slowed division or cell death would reject advancement. Existing medicinal use supplies feasibility context, not efficacy or a dose for this indication. [6]')

page('6. Sensitivity of the proposal to missing information')
p('The completed scenario analysis exposes dependencies rather than filling missing data with favorable assumptions. Two transcript states were applied to each of the six phase/mechanism combinations below; the full 12-row output is in the supplement.')
table([['Phase / assumed mechanism','N1002K-directed proteostasis route','Premature-stop route if transcript is detectable'],['Trans / instability with residual function','4-PBA lead; NMN and TUDCA comparators.','Amlexanox exploratory.'],['Trans / specific functional defect','Stabilization rationale not established.','Amlexanox exploratory; recovery must bypass the defective missense allele functionally.'],['Trans / tolerated missense','N1002K-directed route unsupported; reconsider genetic explanation.','Readthrough remains exploratory, not proof that the pair explains disease.'],['Cis / instability hypothesis','No ordinary full-length N1002K substrate from the stop-bearing allele.','Readthrough could yield N1002K-containing protein; function unresolved.'],['Cis / specific functional defect','No justified standalone stabilization route.','Length recovery may leave a functional defect.'],['Cis / tolerated missense','No N1002K-specific rescue rationale.','Recovered product still requires functional validation.']],[133,177,173])
p('If no stop transcript is detected, the readthrough branch is deprioritized pending evaluation of assay sensitivity, RNA expression and whether NMD modulation creates a usable substrate. A negative baseline RNA assay does not prove permanent biological absence of a substrate.')
h('6.1 What the enumeration means')
p('The specified 4-PBA route appears in 2 of 12 scenarios: both transcript states under trans plus instability with useful residual function. This fraction is not a response probability, a confidence estimate or a frequency in MVA. The number depends on how scenarios are defined. The current case cannot be assigned to a successful branch because the required measurements are absent.')
h('6.2 Evidence-ablation interpretation')
p('Removing the instability assumption eliminates the defined 4-PBA route. Changing trans to cis removes its ordinary full-length substrate. Changing stop-transcript availability affects the amlexanox branch. Removing WT contact geometry weakens structural motivation but cannot, by itself, overturn a measured cellular defect. This sensitivity makes the proposal auditable rather than pretending that one drug remains optimal under every explanation.')

page('7. Proposed functional validation and advancement rules')
h('7.1 Models and controls — proposed, not performed')
p('Start with available case-derived cells and matched controls if access becomes possible. Build endogenous isogenic genotypes to compare WT/WT, p.Leu737Ter/WT, N1002K/WT, trans p.Leu737Ter/N1002K and cis [p.Leu737Ter; N1002K]/WT. These are model scenarios, not claims about this child. Include corrected lines or controlled WT complementation, multiple independent clones and vehicle controls. Endogenous models are needed to preserve transcript processing and NMD; cDNA overexpression alone cannot test those mechanisms.')
h('7.2 Distinguish abundance, function and general cytoprotection')
table([['Question','Proposed measurement','Interpretation'],['Is the defect a depleted pool?','Allele-specific RNA; total/soluble full-length BUBR1; protein turnover.','Distinguishes transcript changes from protein stabilization.'],['Is regulation impaired?','Kinetochore localization; KARD phosphorylation; PP2A-B56 recruitment; checkpoint response.','Tests mechanism beyond protein quantity.'],['Does treatment restore fidelity?','Live-cell scoring of lagging chromosomes, bridges and failed divisions; primary rate per observed anaphase.','Analyze complete cell trajectories and attempted divisions to avoid survivor-only bias.'],['Is apparent benefit misleading?','Mitotic entry, duration, proliferation, apoptosis, micronuclei and ploidy over time.','Excludes cytostasis, selective death or expansion of unstable survivors.']],[121,185,177])
p('Test each candidate separately across concentration and exposure windows, with blinded image scoring. A pilot with multiple independent clones and culture-day replicates should estimate variability for power planning. Cells within one culture are nested observations, not independent biological replicates. Report absolute risk differences or risk ratios and uncertainty using a model that accounts for experiment and clone clustering.')
h('7.3 Advance, revise or stop')
p('<b>Advance:</b> reproducible improvement in the primary functional endpoint with coherent supporting biology, plausible unbound exposure and no harmful WT effect. <b>Revise:</b> protein increases without functional rescue or only stress/viability improves. <b>Stop/deprioritize:</b> no reproducible genotype-associated defect, benefit only at toxic exposure, increased polyploidy/unstable-cell expansion, or an effect limited to one clone. Meaningful effect thresholds must be set before confirmatory experiments using pilot variance and biological relevance, not invented from the current computation.')

page('8. Potential impact and methodological contribution')
h('8.1 Value for this case')
p('The immediate value is to prioritize the observations that change action: allele phase, full-length transcript/protein availability, and whether low abundance or impaired regulation drives the defect. If an instability phenotype with residual function is validated, the study supplies a focused 4-PBA experiment with functional success criteria. If N1002K is tolerated, it redirects the genetic explanation rather than preserving a drug hypothesis at all costs.')
h('8.2 Value for other individuals with MVA')
p('The transferable unit is a mechanism-defined subgroup: expressed, function-retaining but unstable BUBR1. A validated rescue in one genotype would motivate testing other members of that subgroup; it would not establish efficacy across BUB1B-MVA, let alone MVA caused by other genes. The comparator panel makes explicit why similar protein abundance or domain location need not imply the same phenotype or response.')
p('The framework could help choose functional tests for uncertain variants and interpret negative therapeutic experiments. It does not itself provide a formal clinical variant classification. Diagnostic benefit would require independent validation against clinical and functional evidence; a model-derived contact or SASA value is not diagnostic proof.')
h('8.3 Innovation delivered in this submission')
p('The contribution is an integrated, reproducible workflow combining comparator-aware structural interpretation, full-model/domain sensitivity and phase-conditioned candidate routing. Its creative feature is treating uncertainty as a variable that changes the proposed experiment. It uses assay-tolerated and functional-defect comparators to challenge, rather than merely reinforce, the lead hypothesis.')
p('The analysis adds a concrete counterexample to burial-based reasoning and identifies context-sensitive structural exposure. The innovation is methodological integration and decision transparency, not a new SASA algorithm, a trained drug-response model or discovery of a proven therapy. A selected eight-site panel cannot validate predictive generalization.')
h('8.4 Value of a negative result')
p('If 4-PBA raises BUBR1 but not segregation fidelity, the result discriminates abundance rescue from functional rescue. If no genotype-associated defect is reproduced, the N1002K mechanism must be reconsidered. Either outcome can improve subsequent diagnosis-oriented experiments and prevent a resource-intensive drug program from advancing on an insufficient surrogate.')

page('9. Scalability, limitations and final proposal')
h('9.1 Demonstrated reuse and realistic scale')
p('The supplied CLI accepts a variant CSV, validates reference residues and emits measurement tables, atomic contacts, a scenario table and a provenance summary. The main run processed N1002K plus seven comparators. A separate, previously unlisted R727C input completed successfully without changing the analysis code. This demonstrates input extension, not independent biological validation. A deliberately incorrect reference residue was rejected, and decision-rule boundary cases were checked.')
p('The PDB is parsed once per run and geometry is reused. More individuals sharing a variant can reuse those measurements while retaining separate genotype and phase records; literature curation and biological assays remain the bottlenecks. The observed sub-second runtime is a small cached CPU workload, not a benchmark for population-scale analysis. Source retrieval, parallel deployment and large-dataset throughput were not measured.')
p('Applying this to another gene requires a verified reference transcript, model and domain boundaries, experimentally grounded comparators and new gene-specific intervention rules. Current code is deliberately BUB1B-specific. The reusable data structure and computational components are portable; the therapeutic logic is not automatically transferable.')
h('9.2 Material limitations')
p('No phase, raw sequencing reads, functional assays or patient treatment outcomes are available. The static WT model omits partners, conformational ensembles and mutant side-chain accommodation. Domain removal tests one source of uncertainty, not all structural uncertainty. The selected comparison panel lacks an independent test set and does not support clinical classification, causal attribution or drug-response prediction.')
p('Translation would require endogenous functional rescue, exposure/toxicity assessment and appropriate clinical review. Existing developmental effects and established aneuploid cell populations may persist even if new errors decrease. Increasing survival of genomically unstable cells would not meet the therapeutic objective. No human dose or drug combination is proposed.')
h('Final treatment hypothesis')
p('<b>We propose 4-PBA as the lead repurposed treatment experiment for an expressed, stability-impaired N1002K allele with useful residual function.</b> The current evidence supports testing that mechanism, not asserting it. NMN is the closest pathway comparator, TUDCA tests alternative proteostasis modulation, and amlexanox independently addresses the premature-stop branch. The next decisive result is recovery of segregation fidelity in the relevant genotype at feasible, non-toxic exposure. The phase-aware analysis specifies when to advance this proposal and when to change it.')

page('References and reproducibility')
refs=[
('1','Suijkerbuijk SJE et al. Molecular causes for BUBR1 dysfunction in the human cancer predisposition syndrome mosaic variegated aneuploidy. Cancer Res. 2010;70:4891–4900.','https://doi.org/10.1158/0008-5472.CAN-09-4319'),
('2','Gama Braga L et al. BUBR1 pseudokinase domain promotes kinetochore PP2A-B56 recruitment, spindle checkpoint silencing, and chromosome alignment. Cell Rep. 2020;33:108397.','https://doi.org/10.1016/j.celrep.2020.108397'),
('3','Sieben CJ et al. BubR1 allelic effects drive phenotypic heterogeneity in mosaic-variegated aneuploidy progeria syndrome. J Clin Invest. 2020;130:171–188.','https://doi.org/10.1172/JCI126863'),
('4','North BJ et al. SIRT2 induces the checkpoint kinase BubR1 to increase lifespan. EMBO J. 2014;33:1438–1453.','https://doi.org/10.15252/embj.201386907'),
('5','Uppala JK et al. Chemical chaperone, TUDCA unlike PBA, mitigates protein aggregation efficiently and resists ER and non-ER stress induced HepG2 cell death. Sci Rep. 2017;7:3831.','https://doi.org/10.1038/s41598-017-03940-1'),
('6','DailyMed. Sodium phenylbutyrate tablets: official prescribing information. Existing indication and exposure/safety context.','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d08fd548-7eb8-4f6f-b664-b0fff6f30065'),
('7','UniProt. O60566, BUB1B_HUMAN canonical sequence.','https://rest.uniprot.org/uniprotkb/O60566.fasta'),
('8','NCBI RefSeq. NM_001211.6 / NP_001202.5, BUB1B coding sequence and protein.','https://www.ncbi.nlm.nih.gov/nuccore/NM_001211.6'),
('9','AlphaFold Protein Structure Database. O60566; analyzed file AF-O60566-F1-model_v6.pdb.','https://alphafold.ebi.ac.uk/entry/O60566'),
('10','Shrake A, Rupley JA. Environment and exposure to solvent of protein atoms. Lysozyme and insulin. J Mol Biol. 1973;79:351–371.','https://pubmed.ncbi.nlm.nih.gov/4760134/'),
('11','Gonzalez-Hilarion S et al. Rescue of nonsense mutations by amlexanox in human cells. Orphanet J Rare Dis. 2012;7:58.','https://doi.org/10.1186/1750-1172-7-58')]
for n,t,u in refs:small(f'<b>[{n}]</b> {t} <link href="{u}" color="#235b83">Source</link>.')
h('Reproduction and status of work')
p('The computational supplement includes input FASTA/CDS/PDB files, comparator annotations, executable Python analysis, CSV/JSON results, plotting code and instructions. Sources were accessed on 22 October 2026. The methods workbook records completed computational procedures separately from proposed biological work. No raw patient reads or identifiable clinical records are included.')
small('<b>AI assistance:</b> OpenAI ChatGPT was used for retrieval, synthesis, programming and drafting. Scripts produced the numerical results. This does not constitute independent human expert or clinical validation. No unperformed simulation or biological experiment is reported.')
def footer(c,doc):
 c.saveState();c.setStrokeColor(colors.HexColor('#c6d2db'));c.line(56,43,A4[0]-56,43);c.setFont('DV',7);c.setFillColor(colors.HexColor('#536777'));c.drawString(56,29,'BUB1B | I. F. Ghitarroni & S. Rodriguez Salinas');c.drawRightString(A4[0]-56,29,str(doc.page));c.restoreState()
SimpleDocTemplate(str(R/'BUB1B_Therapeutic_Hypothesis.pdf'),pagesize=A4,leftMargin=56,rightMargin=56,topMargin=48,bottomMargin=59,title='Mechanism-conditioned drug repurposing for BUB1B',author='Ian Franco Ghitarroni; Santiago Rodriguez Salinas').build(flow,onFirstPage=footer,onLaterPages=footer)
(R/'report.md').write_text('\n'.join(md))
print(R/'BUB1B_Therapeutic_Hypothesis.pdf')
