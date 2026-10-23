"""Verify archived results, extension, rule boundaries, references and report reproduction.

Run from any directory: python /path/to/validation/verify.py
Optional animation smoke test: add --animation (requires FFmpeg or imageio-ffmpeg).
New results go to validation/runs/; archived scientific results are never overwritten.
"""
from pathlib import Path
import argparse, ast, csv, datetime, hashlib, importlib.util, json, platform, subprocess, sys, time

ROOT = Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--animation',action='store_true')
a=p.parse_args()
RUN=ROOT/'validation/runs';RUN.mkdir(parents=True,exist_ok=True)
results={};started=time.perf_counter()

def run(name, cmd):
    start=time.perf_counter()
    done=subprocess.run([str(x) for x in cmd],capture_output=True,text=True)
    (RUN/(name+'.log')).write_text(done.stdout+'\n'+done.stderr)
    if done.returncode: raise AssertionError(f'{name} failed; see {RUN/(name+".log")}')
    results[name]={'status':'passed','seconds':round(time.perf_counter()-start,3)}

def same_csv(name, actual, archived):
    assert actual.read_bytes()==archived.read_bytes(),f'CSV mismatch: {name}'
    results[name]={'status':'passed','sha256':hashlib.sha256(actual.read_bytes()).hexdigest()}

run('analysis',[sys.executable,ROOT/'analysis/analyze.py','--out',RUN/'analysis'])
for file in ('variant_context.csv','polar_contacts.csv','scenarios.csv'):
    same_csv('main_'+file,RUN/'analysis'/file,ROOT/'analysis/results'/file)
run('extension',[sys.executable,ROOT/'analysis/analyze.py','--variants',ROOT/'analysis/inputs/extension_R727C.csv','--out',RUN/'extension'])
for file in ('variant_context.csv','polar_contacts.csv','scenarios.csv'):
    same_csv('extension_'+file,RUN/'extension'/file,ROOT/'analysis/extension_results'/file)

spec=importlib.util.spec_from_file_location('analysis',ROOT/'analysis/analyze.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.routes('trans','stability_with_residual_function',False)['four_PBA']=='conditional_lead'
assert m.routes('cis','stability_with_residual_function',True)['four_PBA']=='not_supported_by_this_branch'
assert m.routes('trans','specific_function_defect',True)['four_PBA']=='not_supported_by_this_branch'
assert m.routes('trans','tolerated',False)['amlexanox']=='deprioritize_no_demonstrated_substrate'
results['scenario_boundaries']={'status':'passed','interpretation':'Author-defined experimental rules, not response probabilities.'}
invalid=RUN/'invalid.csv'
with invalid.open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['variant','position','reference','alternate','experimental_context','evidence'])
    w.writerow(['wrong',1002,'A','K','test','Intentional invalid reference'])
done=subprocess.run([sys.executable,str(ROOT/'analysis/analyze.py'),'--variants',str(invalid),'--out',str(RUN/'invalid')],capture_output=True,text=True)
assert done.returncode and 'Reference residue mismatch' in done.stderr
results['invalid_reference_rejection']={'status':'passed'}

# Verify geometry used by the animation, independently of the rendering backend.
atoms={};ca={}
for line in (ROOT/'analysis/inputs/AF-O60566-F1-model_v6.pdb').read_text().splitlines():
    if line.startswith('ATOM'):
        pos=int(line[22:26]);name=line[12:16].strip()
        xyz=[float(line[30:38]),float(line[38:46]),float(line[46:54])]
        atoms[f'{pos}:{name}']=xyz
        if name=='CA': ca[pos]=xyz
trace=json.loads((ROOT/'animation/assets/bubr1_ca.json').read_text())
assert len(trace['atoms'])==311
for i,row in enumerate(trace['atoms'],740): assert row['xyz']==ca[i]
module=ast.parse((ROOT/'animation/animate.py').read_text())
polar=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='POLAR_ATOMS' for t in n.targets))
for key,xyz in polar.items(): assert xyz==atoms[key]
results['animation_reference_coordinates']={'status':'passed','CA_atoms':311,'polar_atoms':len(polar),'interpretation':'WT coordinates, not a mutant trajectory.'}

run('report',[sys.executable,ROOT/'report/build_report.py','--output-dir',RUN/'report'])
from pypdf import PdfReader
archived=PdfReader(ROOT/'report/BUB1B_Therapeutic_Hypothesis.pdf')
rebuilt=PdfReader(RUN/'report/BUB1B_Therapeutic_Hypothesis.pdf')
assert len(archived.pages)==len(rebuilt.pages)==11
for old,new in zip(archived.pages,rebuilt.pages): assert old.extract_text()==new.extract_text()
results['report_text_reproduction']={'status':'passed','pages':11,'note':'Byte differences from PDF metadata timestamps are allowed.'}
run('methods',[sys.executable,ROOT/'report/extract_methods.py','--output',RUN/'methods_answers.json'])
assert json.loads((RUN/'methods_answers.json').read_text())==json.loads((ROOT/'report/methods_answers.json').read_text())
results['methods_answer_reproduction']={'status':'passed'}

if a.animation:
    run('animation_smoke',[sys.executable,ROOT/'animation/animate.py','--quality','draft','--width','480','--fps','12','--start','45','--end','46','--preset','ultrafast','--output',RUN/'animation_smoke.mp4'])

report={'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python':platform.python_version(),'checks':results,'total_seconds':round(time.perf_counter()-started,3),
        'biological_validation':'not_performed','scope':'Reproduction of numerical/context/rule results, not validation of pathogenicity or efficacy.'}
(RUN/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
