import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent; rows=list(csv.DictReader((root/'results/variant_context.csv').open()))
colors={'case_unknown':'#c17b1a','instability':'#b64343','low_abundance':'#b64343','specific_function':'#76508f','assay_tolerated':'#257d75'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig,(a,b)=plt.subplots(1,2,figsize=(9.8,4.3),gridspec_kw={'width_ratios':[1,1.5]})
y=np.arange(len(rows))
a.barh(y,[float(r['plddt']) for r in rows],color=[colors[r['experimental_context']] for r in rows],height=.56)
a.set_yticks(y,[r['variant'] for r in rows]);a.invert_yaxis();a.set_xlim(0,100);a.axvline(70,color='#888',lw=.7,ls='--');a.set_xlabel('WT Cα pLDDT');a.set_title('A  Local model confidence',loc='left',fontweight='bold')
for i,r in enumerate(rows):
 full=float(r['sasa_1920_A2']); b.scatter(full,i,color=colors[r['experimental_context']],s=40,zorder=3)
 if r['domain_sasa_A2']:
  dom=float(r['domain_sasa_A2']);b.plot([full,dom],[i,i],color='#777',lw=1);b.scatter(dom,i,facecolors='none',edgecolors='#202c3b',s=65,zorder=4)
b.set_yticks(y,[r['variant'] for r in rows]);b.invert_yaxis();b.set_xscale('log');b.set_xlim(.45,350);b.set_xlabel('Total WT residue SASA (Å²; logarithmic scale)');b.set_title('B  Sensitivity to model context',loc='left',fontweight='bold')
b.scatter([],[],color='#555',label='Full model');b.scatter([],[],facecolors='none',edgecolors='#202c3b',label='Domain 740–1050');b.legend(frameon=False,fontsize=8,loc='upper right')
fig.tight_layout(w_pad=3);fig.savefig(root/'results/comparison.png',dpi=200);plt.close(fig)
