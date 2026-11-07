"""Vendor curated topic icons so the profile does not depend on live icon widgets."""
from pathlib import Path
import concurrent.futures
import json
import io
import zipfile
import urllib.request
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/icons'; OUT.mkdir(parents=True,exist_ok=True)
ICONS=json.loads((ROOT/'data/topics.json').read_text(encoding='utf-8'))

def fetch(icon):
    try:
        request=urllib.request.Request(icon['source'],headers={'User-Agent':'ninglinLiu-profile'})
        with urllib.request.urlopen(request,timeout=30) as response: content=response.read()
        if icon.get('archive_member'):
            content=zipfile.ZipFile(io.BytesIO(content)).read(icon['archive_member'])
        name=icon.get('file',icon['slug']+'.svg')
        if name.endswith('.svg'):
            xml=ET.fromstring(content)
            if not xml.tag.endswith('svg'):raise RuntimeError('Not an SVG')
        (OUT/name).write_bytes(content)
        return icon,None
    except Exception as error:return icon,type(error).__name__+': '+str(error)

if __name__=='__main__':
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for icon,error in pool.map(fetch,ICONS):
            if error:print(icon['name'],error)
            else:results.append(icon)
    if len(results)!=len(ICONS):raise RuntimeError('Some icons could not be refreshed; the manifest was preserved.')
    print(f'Vendored {len(results)} / {len(ICONS)} topic icons.')
