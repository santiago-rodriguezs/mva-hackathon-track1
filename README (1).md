# BUB1B mechanism-conditioned repurposing: computational supplement

## Reproduce

Python 3.12 was used. No GPU, paid server or network access is needed after installation. Extract the ZIP and open a terminal in the directory containing `analyze.py`.

```bash
python -m pip install -r requirements.txt
python analyze.py
python plot_results.py
python analyze.py --variants inputs/extension_R727C.csv --out extension_results
```

The main run measures eight residue sites (N1002K plus seven experimental comparators) in a single public WT model. The extension adds R727C through a separate input, without code changes. This demonstrates software reuse; it is not a held-out predictive validation. The experimental labels are comparison contexts, not clinical classifications. The pipeline is BUB1B-specific; cross-gene transfer requires new references, domain boundaries and mechanistic rules.

## Inputs and sources

- `inputs/bubr1.fasta`: UniProt O60566 canonical sequence, https://rest.uniprot.org/uniprotkb/O60566.fasta
- `inputs/bubr1_cds.fasta`: NCBI RefSeq NM_001211.6 / NP_001202.5 CDS, https://www.ncbi.nlm.nih.gov/nuccore/NM_001211.6
- `inputs/AF-O60566-F1-model_v6.pdb`: frozen WT AlphaFold model, https://alphafold.ebi.ac.uk/files/AF-O60566-F1-model_v6.pdb
- `inputs/af_metadata.json`: accompanying public AlphaFold metadata.
- `inputs/variants.csv`: comparison panel curated from Suijkerbuijk et al. 2010, https://doi.org/10.1158/0008-5472.CAN-09-4319. Figure/assay pointers accompany each row. N1002K is a supplied case input without a functional label.

The case also contains reported p.Leu737Ter. Its TTA>TGA codon and the AAT>AAG missense codon are checked against the CDS. The case calls themselves, phase and disease causality were not independently verified.

## Outputs

- `results/variant_context.csv`: WT pLDDT, total/side-chain SASA, sampling and domain-context sensitivity, C-alpha packing counts.
- `results/polar_contacts.csv`: N1002 side-chain polar atoms within 4 A of other N/O/S atoms. These are geometric contacts, not confirmed hydrogen bonds.
- `results/scenarios.csv`: 12 unweighted phase/mechanism/transcript combinations and explicit experimental eligibility rules.
- `results/summary.json`: versions, cached runtime, source hashes and scope.
- `results/comparison.png`: model-confidence and solvent-exposure figure.
- `extension_results/`: separate R727C run.
- `validation.json`: executed software checks and explicit absence of biological validation.

SASA uses a 1.4 A probe, atomic radii C=1.70, N=1.55, O=1.52, S=1.80 A, and 960/1920 Fibonacci points/atom. Domain sensitivity uses residues 740–1050. Total SASA is an absolute area; it is not a standardized relative-accessibility or pathogenicity score. Structures, partner orientation and mutant energetics were not simulated. A local confidence value cannot validate full-model domain placement.

## What the decision rules mean

4-PBA is a conditional experimental lead only in the stipulated trans + instability-with-useful-residual-function branch. NMN and TUDCA are comparators in that branch. The stop-allele amlexanox experiment requires evaluation of transcript availability and recovered protein function. In cis, successful readthrough retains N1002K. Lack of a detectable baseline transcript warrants investigation, rather than proving that NMD modulation cannot create a substrate.

These rules are author-defined hypotheses, not learned drug rankings. Their 2/12 eligibility count has no probabilistic meaning. The current case cannot be assigned to the qualifying branch. No efficacy, human dose, combination, mutant delta-delta-G, docking or MD result is produced.

## Verified checks

The eight-site batch completed, its N1002 SASA agreed with the earlier reference computation, a separate R727C input ran, an intentionally incorrect reference residue was rejected, and boundary cases of the scenario rules passed. Empty N1002-contact outputs retain their table header when no N1002 row is supplied. No numerical metric is evidence of biological efficacy.

Runtime excludes source retrieval, literature curation and report preparation. Single-run CPU speed is not a population-scale benchmark. Larger cohorts can reuse per-variant measurements; provenance and clinical interpretation remain case-specific.
