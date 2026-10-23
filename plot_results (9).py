import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
p=Path(__file__).resolve().parent
r=json.loads((p/'structure_results.json').read_text())
fig,ax=plt.subplots(1,2,figsize=(9,3.15),gridspec_kw={'width_ratios':[1.15,1]})
pos=[];conf=[]
for l in (p.parent/'analysis/inputs/AF-O60566-F1-model_v6.pdb').read_text().splitlines():
 if l.startswith('ATOM') and l[12:16].strip()=='CA' and 970<=int(l[22:26])<=1025:
  pos.append(int(l[22:26]));conf.append(float(l[60:66]))
ax[0].plot(pos,conf,color='#315b73',lw=1.5)
ax[0].axhline(90,color='gray',ls=':',lw=1)
for n,c in [(1002,'#a4482a'),(1012,'#315b73')]:
 v=r['residues'][str(n)]['CA_pLDDT'];ax[0].scatter([n],[v],color=c,zorder=3);ax[0].annotate(f'{r["residues"][str(n)]["aa"]}{n}',(n,v),xytext=(0,-23),textcoords='offset points',ha='center',fontsize=9,color=c)
ax[0].set(xlabel='Human BUBR1 residue',ylabel='Local confidence (pLDDT)',ylim=(70,100),title='A  Local structural confidence')
vals=[r['residues'][str(n)]['full_1920']['total_sasa_A2'] for n in [1002,1008,1012]]
bars=ax[1].bar(['N1002','T1008','L1012'],vals,color=['#a4482a','#96a4af','#315b73'],width=.6)
for b,v in zip(bars,vals):ax[1].text(b.get_x()+b.get_width()/2,v+.6,f'{v:.2f}',ha='center',fontsize=9)
ax[1].set(ylabel='Total residue SASA (Å²)',ylim=(0,34),title='B  Solvent-accessible area')
for a in ax:a.spines[['top','right']].set_visible(False);a.tick_params(labelsize=9);a.title.set_fontsize(11)
fig.tight_layout(w_pad=2.5)
(p/'rebuilt').mkdir(exist_ok=True)
fig.savefig(p/'rebuilt/structure_figure.png',dpi=220,bbox_inches='tight')
