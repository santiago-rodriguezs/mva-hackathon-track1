"""Derive the animation's WT C-alpha trace from the frozen analysis PDB."""
from pathlib import Path
import argparse,json
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=ROOT/'renders/bubr1_ca.json')
a=p.parse_args()
rows=[]
for l in (ROOT.parent/'analysis/inputs/AF-O60566-F1-model_v6.pdb').read_text().splitlines():
    if l.startswith('ATOM') and l[12:16].strip()=='CA' and 740<=int(l[22:26])<=1050:
        rows.append({'residue':int(l[22:26]),'xyz':[float(l[30:38]),float(l[38:46]),float(l[46:54])],
                     'plddt':float(l[60:66])})
assert len(rows)==311
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps({'source':'https://alphafold.ebi.ac.uk/files/AF-O60566-F1-model_v6.pdb',
                               'region':[740,1050],'note':'Wild-type AlphaFold model, not a mutant trajectory.',
                               'atoms':rows},indent=2))
print(a.output)
