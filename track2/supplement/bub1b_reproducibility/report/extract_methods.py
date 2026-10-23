"""Extract both methods-form sheets to auditable JSON using the Python standard library."""
from pathlib import Path
import argparse, json, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--input', type=Path, default=ROOT/'methods_description_form.xlsx')
p.add_argument('--output', type=Path, default=ROOT/'methods_answers.json')
a = p.parse_args()
ns = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(a.input) as z:
    shared = [''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    links = {r.attrib['Id']:r.attrib['Target'] for r in rels}
    out = {}
    for sheet in wb.find('s:sheets',ns):
        rel = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        target = links[rel]
        path = target.lstrip('/') if target.startswith('/') else 'xl/'+target
        root = ET.fromstring(z.read(path)); cells = {}
        for c in root.findall('.//s:c',ns):
            v = c.find('s:v',ns)
            val = v.text if v is not None else None
            if c.attrib.get('t')=='s' and val is not None: val = shared[int(val)]
            elif c.attrib.get('t')=='inlineStr': val = ''.join(c.find('s:is',ns).itertext())
            if val is not None: cells[c.attrib['r']] = val
        out[sheet.attrib['name']] = [{'row':i,'question':cells.get(f'A{i}',''),
              'answer':cells[f'B{i}']} for i in range(7,100) if f'B{i}' in cells]
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
print(a.output)
