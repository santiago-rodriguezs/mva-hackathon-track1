"""Deterministic WT structural context; not a mutant stability simulation."""
import json, time, hashlib, sys, platform
from pathlib import Path
import urllib.request
import numpy as np
import scipy
from scipy.spatial.distance import cdist

start=time.perf_counter()
base=Path(__file__).resolve().parent.parent/'analysis/inputs'
out_dir=Path(__file__).resolve().parent/'rebuilt'
out_dir.mkdir(exist_ok=True)
meta=json.loads((base/'af_metadata.json').read_text())[0]
pdb=base/'AF-O60566-F1-model_v6.pdb'
if not pdb.exists():
    pdb.write_bytes(urllib.request.urlopen(meta['pdbUrl'],timeout=30).read())
seq=''.join(x.strip() for x in (base/'bubr1.fasta').read_text().splitlines() if not x.startswith('>'))
atoms=[]
for line in pdb.read_text().splitlines():
    if line.startswith('ATOM') and line[16] in (' ','A'):
        atoms.append(dict(name=line[12:16].strip(),res=line[17:20].strip(),chain=line[21],pos=int(line[22:26]),xyz=[float(line[30:38]),float(line[38:46]),float(line[46:54])],plddt=float(line[60:66]),element=line[76:78].strip()))
assert len(seq)==1050 and seq[1001]=='N' and seq[1011]=='L' and seq[736]=='L'
assert seq==meta['uniprotSequence']
cds=''.join(x.strip() for x in (base/'bubr1_cds.fasta').read_text().splitlines() if not x.startswith('>'))
bases='TCAG'
code=dict(zip([a+b+c for a in bases for b in bases for c in bases], 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'))
translated=''.join(code[cds[i:i+3]] for i in range(0,len(cds),3))
assert translated==seq+'*'
assert cds[2209]=='T' and cds[3005]=='T'
codons={'Leu737Ter':{'reference':cds[2208:2211],'alternate':cds[2208]+'G'+cds[2210]},'Asn1002Lys':{'reference':cds[3003:3006],'alternate':cds[3003:3005]+'G'}}
assert code[codons['Leu737Ter']['alternate']]=='*' and code[codons['Asn1002Lys']['alternate']]=='K'
assert len([a for a in atoms if a['name']=='CA'])==1050
xyz=np.array([a['xyz'] for a in atoms]); radii=np.array([{'C':1.70,'N':1.55,'O':1.52,'S':1.80}[a['element']]+1.4 for a in atoms])

def sasa(pos,n,domain=False):
    # Fibonacci sphere; points occluded by any other expanded atomic sphere.
    ids=[i for i,a in enumerate(atoms) if a['pos']==pos]
    env=np.array([i for i,a in enumerate(atoms) if not domain or 740<=a['pos']<=1050])
    k=np.arange(n,dtype=float);z=1-2*(k+.5)/n;theta=np.pi*(3-np.sqrt(5))*k
    sphere=np.stack([np.sqrt(1-z*z)*np.cos(theta),np.sqrt(1-z*z)*np.sin(theta),z],axis=1)
    area=side=isolated=0.
    for i in ids:
        near=env[(np.linalg.norm(xyz[env]-xyz[i],axis=1)<radii[env]+radii[i]) & (env!=i)]
        pts=xyz[i]+radii[i]*sphere
        exposed=np.all(cdist(pts,xyz[near])>=radii[near],axis=1)
        ai=float(exposed.mean()*4*np.pi*radii[i]**2);area+=ai
        if atoms[i]['name'] not in ['N','CA','C','O','OXT']:side+=ai
        own=np.array([j for j in ids if j!=i])
        isolated+=float(np.all(cdist(pts,xyz[own])>=radii[own],axis=1).mean()*4*np.pi*radii[i]**2)
    return {'total_sasa_A2':round(area,3),'sidechain_sasa_A2':round(side,3),'isolated_residue_sasa_A2':round(isolated,3),'within_conformation_exposure_fraction':round(area/isolated,5)}

res={}
for pos in [1002,1008,1012]:
    ca=next(a for a in atoms if a['pos']==pos and a['name']=='CA')
    res[str(pos)]={'aa':seq[pos-1],'CA_pLDDT':ca['plddt'],'full_960':sasa(pos,960),'full_1920':sasa(pos,1920),'domain_1920':sasa(pos,1920,True)}
source=[i for i,a in enumerate(atoms) if a['pos']==1002 and a['name'] in ['OD1','ND2']]
contacts=[]
for i in source:
    for j,b in enumerate(atoms):
        if b['pos']!=1002 and b['element'] in ['N','O','S']:
            d=float(np.linalg.norm(xyz[i]-xyz[j]))
            if d<=4.0:contacts.append({'N1002_atom':atoms[i]['name'],'partner_residue':b['res']+str(b['pos']),'partner_atom':b['name'],'distance_A':round(d,3)})
contacts.sort(key=lambda x:x['distance_A'])
ca={a['pos']:np.array(a['xyz']) for a in atoms if a['name']=='CA'}
out={'analysis':'Wild-type AlphaFold structural-context analysis; no mutation modeling or dynamics','date':'2026-10-22','protein_length':len(seq),'sequence_window_992_1016':seq[991:1016],'source_url':meta['pdbUrl'],'model_version':meta['latestVersion'],'model_created':meta['modelCreatedDate'],'residues':res,'N1002_CA_distances_A':{str(p):round(float(np.linalg.norm(ca[1002]-ca[p])),3) for p in [1005,1006,1008,1012]},'N1002_polar_contacts_under_4A':contacts,'removed_by_Leu737Ter':1050-736,'assumptions':{'probe_A':1.4,'radii_A':{'C':1.7,'N':1.55,'O':1.52,'S':1.8},'sample_points':[960,1920],'domain_comparison':[740,1050],'exposure_fraction':'SASA divided by isolated residue SASA in identical conformation; not standardized RSA'},'input_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [pdb,base/'bubr1.fasta',base/'af_metadata.json']},'python':platform.python_version(),'numpy':np.__version__,'runtime_seconds':round(time.perf_counter()-start,3)}
out['codon_validation']=codons
out['transcript']='NM_001211.6 / NP_001202.5'
out['CDS_translation_matches_UniProt']=True
out['scipy']=scipy.__version__
out['input_sha256']['bubr1_cds.fasta']=hashlib.sha256((base/'bubr1_cds.fasta').read_bytes()).hexdigest()
out['runtime_seconds']=round(time.perf_counter()-start,3)
(out_dir/'structure_results.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
