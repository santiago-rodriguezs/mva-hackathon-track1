"""Batch WT structural context and explicit scenario routing; no efficacy prediction.

python analyze.py --variants inputs/variants.csv --out results
All paths default to this script's directory. No network requests are required.
"""
from pathlib import Path
import argparse, csv, hashlib, itertools, json, platform, time
import numpy as np
import scipy
from scipy.spatial.distance import cdist

ROOT = Path(__file__).resolve().parent

def write_csv(path, rows, fields=None):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader(); w.writerows(rows)

def routes(phase, mechanism, substrate):
    # Eligibility means justification for an experiment, never a prescribing rule.
    stable_rescue = phase == 'trans' and mechanism == 'stability_with_residual_function'
    return dict(four_PBA='conditional_lead' if stable_rescue else 'not_supported_by_this_branch',
                NMN='pathway_comparator' if stable_rescue else 'not_supported_by_this_branch',
                TUDCA='proteostasis_comparator' if stable_rescue else 'not_supported_by_this_branch',
                amlexanox=('exploratory_stop_allele' if phase == 'trans' else 'exploratory_cis_product_unresolved')
                          if substrate else 'deprioritize_no_demonstrated_substrate')

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variants', type=Path, default=ROOT/'inputs/variants.csv')
    p.add_argument('--out', type=Path, default=ROOT/'results')
    args = p.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    pdb = ROOT/'inputs/AF-O60566-F1-model_v6.pdb'
    seqfile = ROOT/'inputs/bubr1.fasta'; cdsfile = ROOT/'inputs/bubr1_cds.fasta'
    seq = ''.join(x.strip() for x in seqfile.read_text().splitlines() if not x.startswith('>'))
    cds = ''.join(x.strip() for x in cdsfile.read_text().splitlines() if not x.startswith('>'))
    bases = 'TCAG'
    code = dict(zip([a+b+c for a in bases for b in bases for c in bases],
                   'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'))
    assert ''.join(code[cds[i:i+3]] for i in range(0,len(cds),3)) == seq+'*'
    assert cds[2208:2211] == 'TTA' and cds[3003:3006] == 'AAT'
    assert cds[2208]+'G'+cds[2210] == 'TGA' and cds[3003:3005]+'G' == 'AAG'
    records = list(csv.DictReader(args.variants.open()))
    atoms = []
    for l in pdb.read_text().splitlines():
        if l.startswith('ATOM') and l[16] in (' ', 'A'):
            atoms.append(dict(pos=int(l[22:26]), name=l[12:16].strip(),
                              xyz=[float(l[30:38]),float(l[38:46]),float(l[46:54])],
                              plddt=float(l[60:66]), element=l[76:78].strip()))
    xyz = np.array([a['xyz'] for a in atoms]); positions = np.array([a['pos'] for a in atoms])
    radii = np.array([dict(C=1.7,N=1.55,O=1.52,S=1.8)[a['element']]+1.4 for a in atoms])
    ca = {a['pos']: a for a in atoms if a['name']=='CA'}
    assert len(ca) == len(seq) == 1050
    spheres = {}
    for n in (960,1920):
        k=np.arange(n); z=1-2*(k+.5)/n; th=np.pi*(3-np.sqrt(5))*k
        spheres[n]=np.c_[np.sqrt(1-z*z)*np.cos(th),np.sqrt(1-z*z)*np.sin(th),z]
    def sasa(pos, n, domain=False):
        ids=np.flatnonzero(positions==pos)
        env=np.flatnonzero((positions>=740)&(positions<=1050)) if domain else np.arange(len(atoms))
        total=side=0.
        for i in ids:
            near=env[(np.linalg.norm(xyz[env]-xyz[i],axis=1)<radii[env]+radii[i])&(env!=i)]
            pts=xyz[i]+radii[i]*spheres[n]
            area=np.all(cdist(pts,xyz[near])>=radii[near],axis=1).mean()*4*np.pi*radii[i]**2
            total+=area
            if atoms[i]['name'] not in ('N','CA','C','O','OXT'): side+=area
        return float(total),float(side)
    rows=[]; contact_rows=[]
    for record in records:
        pos=int(record['position'])
        if not 1<=pos<=len(seq) or seq[pos-1]!=record['reference']:
            raise ValueError(f'Reference residue mismatch: {record}')
        a960,_=sasa(pos,960); a1920,side=sasa(pos,1920)
        domain=sasa(pos,1920,True)[0] if pos>=740 else None
        dist=np.array([np.linalg.norm(np.array(a['xyz'])-ca[pos]['xyz']) for a in ca.values()])
        row=dict(record, plddt=ca[pos]['plddt'], sasa_960_A2=round(a960,3),
                 sasa_1920_A2=round(a1920,3), sidechain_sasa_A2=round(side,3),
                 domain_sasa_A2=None if domain is None else round(domain,3),
                 sasa_sampling_delta_A2=round(abs(a1920-a960),3),
                 CA_neighbors_8A=int(np.sum((dist>0)&(dist<=8))),
                 CA_neighbors_10A=int(np.sum((dist>0)&(dist<=10))),
                 domain_context='C_terminal' if pos>=740 else 'outside_C_terminal',
                 interpretation='WT context only; no mutant energy or clinical classification')
        rows.append(row)
        if record['variant']=='N1002K':
            for i,a in enumerate(atoms):
                if a['pos']==pos and a['name'] in ('OD1','ND2'):
                    for j,b in enumerate(atoms):
                        d=np.linalg.norm(xyz[i]-xyz[j])
                        if b['pos']!=pos and b['element'] in ('N','O','S') and d<=4:
                            contact_rows.append(dict(atom=a['name'],partner_position=b['pos'],
                                                     partner_atom=b['name'],distance_A=round(float(d),3)))
    scenarios=[]
    for phase,mechanism,substrate in itertools.product(('cis','trans'),
            ('stability_with_residual_function','specific_function_defect','tolerated'),(False,True)):
        scenarios.append(dict(scenario=len(scenarios)+1,phase=phase,mechanism=mechanism,
                              detectable_stop_transcript=substrate,**routes(phase,mechanism,substrate)))
    write_csv(args.out/'variant_context.csv',rows)
    write_csv(args.out/'scenarios.csv',scenarios)
    write_csv(args.out/'polar_contacts.csv',sorted(contact_rows,key=lambda r:r['distance_A']),
              ['atom','partner_position','partner_atom','distance_A'])
    elapsed=time.perf_counter()-start
    summary=dict(structural_rows=len(rows),comparators=sum(r['experimental_context']!='case_unknown' for r in rows),scenarios=len(scenarios),
                 conditional_four_PBA_scenarios=sum(r['four_PBA']=='conditional_lead' for r in scenarios),
                 note='Scenario counts are coverage of stipulated assumptions, not probabilities or response rates.',
                 codons={'Leu737Ter':'TTA>TGA','Asn1002Lys':'AAT>AAG'},truncation_removed_residues=314,
                 runtime_seconds=elapsed,python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                 hashes={str(f.relative_to(ROOT)) if f.is_relative_to(ROOT) else str(f):
                         hashlib.sha256(f.read_bytes()).hexdigest() for f in (pdb,seqfile,cdsfile,args.variants)},
                 scope='One static WT model. No variant classifier, efficacy simulation, docking, MD or delta-delta-G.')
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
