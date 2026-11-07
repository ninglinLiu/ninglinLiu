"""Render the profile's self-contained animated SVGs and public contribution index."""
from pathlib import Path
from collections import Counter
import base64
import html
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
DATA = json.loads((ROOT / 'data/contributions.json').read_text(encoding='utf-8'))
PRS = DATA['contributions']
COUNTS = Counter(p['repository'] for p in PRS)
INK, PANEL, LINE = '#101c22', '#17272e', '#32434a'
WHITE, MUTED, JADE, GOLD = '#f4f0e6', '#adbec1', '#89d9c1', '#dfbc84'

def txt(x,y,text,size=24,color=WHITE,weight=400,font='Arial, Helvetica, sans-serif',extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" font-weight="{weight}" {extra}>{html.escape(str(text))}</text>'

def rect(x,y,w,h,fill=PANEL,rx=16,stroke=None):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>'

def line(x1,y1,x2,y2,color=LINE,width=1,extra=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {extra}/>'

def dot(x,y,r=4,color=JADE,delay=0):
    return f'<circle class="pulse" style="animation-delay:{delay}s" cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'

STYLE='''
text{font-kerning:normal} .trace{stroke-dasharray:8 16;animation:flow 4s linear infinite}
.trace-slow{stroke-dasharray:3 13;animation:flow 8s linear infinite}
.pulse{animation:pulse 3.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
.spin{animation:spin 24s linear infinite;transform-box:fill-box;transform-origin:center}
.spin-reverse{animation:spin 35s linear infinite reverse;transform-box:fill-box;transform-origin:center}
.float{animation:float 5s ease-in-out infinite}
.draw{stroke-dasharray:1200;animation:draw 7s ease-in-out infinite}
.bar{transform-box:fill-box;transform-origin:bottom;animation:bar 4s ease-in-out infinite}
.cursor{animation:cursor 1.5s step-end infinite}
.sheen{animation:sheen 9s ease-in-out infinite}
.frame{animation:frame 9s ease-in-out infinite}
@keyframes flow{to{stroke-dashoffset:-192}}
@keyframes pulse{0%,100%{opacity:.45;transform:scale(.85)}50%{opacity:1;transform:scale(1.15)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
@keyframes draw{0%{stroke-dashoffset:1200}45%,80%{stroke-dashoffset:0}100%{stroke-dashoffset:-1200}}
@keyframes bar{0%,100%{transform:scaleY(.45)}50%{transform:scaleY(1)}}
@keyframes cursor{50%{opacity:0}}
@keyframes sheen{0%,20%{transform:translateX(-500px);opacity:0}35%{opacity:.5}65%{transform:translateX(1300px);opacity:0}100%{transform:translateX(1300px);opacity:0}}
@keyframes frame{0%,100%{opacity:.4}35%,65%{opacity:1}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
'''

def svg(name,w,h,title,body):
    s=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title">
<title id="title">{html.escape(title)}</title><defs>
<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#182c32"/><stop offset="1" stop-color="#0c171e"/></linearGradient>
<linearGradient id="metal" x2="1" y2="1"><stop stop-color="#c2efdd"/><stop offset=".35" stop-color="#6aaf9c"/><stop offset=".7" stop-color="#243c43"/><stop offset="1" stop-color="#dcc494"/></linearGradient>
<linearGradient id="fade"><stop stop-color="#89d9c1" stop-opacity="0"/><stop offset=".5" stop-color="#89d9c1" stop-opacity=".5"/><stop offset="1" stop-color="#89d9c1" stop-opacity="0"/></linearGradient>
<radialGradient id="glow"><stop stop-color="#7ec9b5" stop-opacity=".18"/><stop offset="1" stop-color="#7ec9b5" stop-opacity="0"/></radialGradient>
<clipPath id="outer"><rect width="{w}" height="{h}" rx="24"/></clipPath>
</defs><style>{STYLE}</style><g clip-path="url(#outer)">{rect(0,0,w,h,'url(#bg)',24)}{body}</g></svg>'''
    (OUT/name).write_text(s,encoding='utf-8')

def eyebrow(x,y,label):
    return txt(x,y,label,17,JADE,600,extra='letter-spacing="2.5"')

def chip(x,y,label,w=None,color=JADE):
    w=w or len(label)*12+28
    return rect(x,y-23,w,34,'#20363b',7)+txt(x+14,y,label,17,color,600)

def orb(cx,cy,r):
    b=f'<circle cx="{cx}" cy="{cy}" r="{r*1.65}" fill="url(#glow)"/>'
    for a in [-55,-30,0,30,55]:
        b+=f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*.36}" fill="none" stroke="url(#metal)" stroke-width="1.8" transform="rotate({a} {cx} {cy})"/>'
    b+=f'<g class="spin"><circle cx="{cx}" cy="{cy}" r="{r*.9}" fill="none" stroke="#587e79" stroke-width="1" stroke-dasharray="3 14"/>'
    for a in range(0,360,60):
        x=cx+math.cos(math.radians(a))*r*.9;y=cy+math.sin(math.radians(a))*r*.9
        b+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{JADE if a%120==0 else GOLD}"/>'
    b+='</g>'
    b+=f'<g class="spin-reverse"><ellipse cx="{cx}" cy="{cy}" rx="{r*.48}" ry="{r*.88}" fill="none" stroke="{JADE}" stroke-opacity=".5" stroke-width="1.8"/></g>'
    b+=rect(cx-46,cy-46,92,92,INK,22,JADE)+txt(cx,cy+10,'YL',32,WHITE,700,extra='text-anchor="middle"')
    return b

def hero(mobile=False):
    w,h=(600,970) if mobile else (1200,660)
    b=eyebrow(40,48,'YU LIU / ENGINEERING PORTFOLIO')
    b+=line(40,73,w-40,73)
    if not mobile:b+=dot(1028,43,4)+txt(1042,49,'OPEN TO WORK',14,MUTED,600)
    b+=txt(40,153,'Yu Liu',70,WHITE,700)+txt(42,193,'AI ENGINEER  /  OPEN SOURCE',19,JADE,600,extra='letter-spacing="1.4"')
    b+=txt(40,273,'Ideas into systems.',47 if mobile else 54,WHITE,400,'Georgia, serif')
    b+=txt(40,333,'Systems into products.',44 if mobile else 50,WHITE,400,'Georgia, serif')
    b+=txt(42,382,'Agents. Creative tools. On-chain systems.',20 if mobile else 24,MUTED)
    b+=chip(42,435,'AI AGENTS',132)+chip(186,435,'FULL STACK',145)+chip(343,435,'WEB3',92)
    if mobile:
        b+=orb(300,635,128)
        b+=txt(300,808,'RETRIEVE  /  REASON  /  BUILD',18,JADE,600,extra='text-anchor="middle" letter-spacing="1"')
        yy=850;cols=[(35,'1,000+','omniAI users'),(233,str(len(PRS)),'merged PRs'),(419,str(len(COUNTS)),'upstream repos')]
    else:
        b+=line(687,109,687,470)
        b+=orb(931,287,147)
        for x,y,s in [(734,132,'KNOWLEDGE'),(1042,158,'TOOLS'),(1022,417,'PRODUCT'),(730,407,'CODE')]:
            b+=chip(x,y,s,len(s)*9+28,color=GOLD)
        b+=f'<path d="M750 185 C840 154 1000 154 1100 226 M1100 349 C1000 430 850 430 750 344" fill="none" stroke="{JADE}" stroke-width="2" class="trace"/>'
        b+=txt(932,486,'DESIGNED TO SHIP.',16,JADE,600,extra='text-anchor="middle" letter-spacing="3"')
        yy=524;cols=[(42,'1,000+','omniAI registered users'),(442,str(len(PRS)),'merged upstream PRs'),(842,str(len(COUNTS)),'open-source repositories')]
    b+=line(40,yy-15,w-40,yy-15)
    for x,v,l in cols:
        b+=txt(x,yy+51,v,44 if mobile else 49,WHITE,600)+txt(x,yy+84,l,20 if mobile else 19,MUTED)
    if not mobile:b+=txt(40,h-20,'XJTLU  /  SHANGHAI + REMOTE',13,MUTED,500)
    svg('hero-mobile.svg' if mobile else 'hero.svg',w,h,'Yu Liu — AI, full-stack and Web3. 1,000+ omniAI registered users; '+str(len(PRS))+' merged upstream PRs.',b)

def section(name,num,title,subtitle,color=JADE):
    b=txt(8,53,num,28,color,500,'Georgia, serif')+txt(72,54,title,37,WHITE,600)+line(72,77,1190,77)+txt(73,112,subtitle,20,MUTED)
    svg('section-'+name+'.svg',1200,143,title,b)

def omni(mobile=False):
    w,h=(600,850) if mobile else (1200,860)
    image_path=OUT/'omniai-product.jpg'
    image64=base64.b64encode(image_path.read_bytes()).decode() if image_path.exists() else ''
    b=eyebrow(36,46,'01 / LIVE PRODUCT')+txt(36,113,'omniAI',65,WHITE,700)
    b+=txt(38,159,'A research agent you can step inside.',24 if mobile else 29,MUTED,400,'Georgia, serif')
    if mobile:
        b+=chip(38,208,'1,000+ REGISTERED USERS',345,GOLD)
        photo_y,photo_h=244,360
    else:
        b+=rect(880,28,280,104,'#243a3d',16)+txt(902,77,'1,000+',43,GOLD,700)+txt(902,109,'REGISTERED USERS',17,MUTED,600)
        photo_y,photo_h=193,520
    b+=f'<defs><clipPath id="photo"><rect x="22" y="{photo_y}" width="{w-44}" height="{photo_h}" rx="15"/></clipPath></defs>'
    b+=f'<image x="22" y="{photo_y}" width="{w-44}" height="{photo_h}" href="data:image/jpeg;base64,{image64}" preserveAspectRatio="xMidYMid slice" clip-path="url(#photo)"/>'
    b+=f'<g clip-path="url(#photo)"><rect class="sheen" x="0" y="{photo_y}" width="260" height="{photo_h}" fill="url(#fade)"/></g>'
    y=photo_y+photo_h+43
    labels=['RAG RETRIEVAL','TOOL CALLING','STREAMING + MCP']
    if mobile:
        for i,l in enumerate(labels):
            b+=dot(40,y+i*48,5,JADE,-i)+txt(58,y+7+i*48,l,22,WHITE,600)
        b+=txt(38,h-25,'omniaihello.com  /  Next.js + TypeScript',19,MUTED)
    else:
        for i,l in enumerate(labels):
            x=38+i*390;b+=dot(x,y,6,JADE,-i)+txt(x+20,y+7,l,21,WHITE,600)
            if i<2:b+=line(x+230,y,x+357,y,JADE,1.6,extra='class="trace"')
        b+=txt(38,h-30,'Bilingual experience  /  3D interaction  /  Source-linked answers',22,MUTED)
    svg('omniai-mobile.svg' if mobile else 'omniai.svg',w,h,'omniAI — live financial research agent, 1,000+ registered users. Product screenshot with an animated workflow.',b)

GROUPS=[('AI & AGENTS',['microsoft/agent-framework','livekit/agents','pipecat-ai/pipecat','ag2ai/ag2','kyegomez/swarms','567-labs/instructor','browser-use/browser-use','pydantic/pydantic-ai','topoteretes/cognee','BerriAI/litellm']),('DATA & RUNTIME',['apache/arrow-rs','apache/iceberg-rust','apache/datafusion','microsoft/onnxruntime','pydantic/pydantic']),('WEB3 & TOOLING',['foundry-rs/foundry','foundry-rs/foundry-core','foundry-rs/book','OpenZeppelin/openzeppelin-monitor','NonceGeek/dim-sum-right-proof']),('REALTIME & CREATIVE',['livekit/client-sdk-js','livekit/components-js','pipecat-ai/pipecat-examples','pipecat-ai/docs','CrossGL/crosstl'])]
SHORT={'microsoft/agent-framework':'MS Agent Framework','OpenZeppelin/openzeppelin-monitor':'OpenZeppelin Monitor','NonceGeek/dim-sum-right-proof':'dim-sum-right-proof','pipecat-ai/pipecat-examples':'Pipecat Examples','pipecat-ai/docs':'Pipecat Docs','CrossGL/crosstl':'CrossGL / CrossTL','livekit/client-sdk-js':'LiveKit Client SDK','livekit/components-js':'LiveKit Components','livekit/agents':'LiveKit Agents','foundry-rs/foundry-core':'Foundry Core','foundry-rs/book':'Foundry Book'}
known={repo for _,repos in GROUPS for repo in repos}
if set(COUNTS)-known:GROUPS.append(('MORE UPSTREAM WORK',sorted(set(COUNTS)-known)))

def atlas(mobile=False):
    w=600 if mobile else 1200
    h=230+sum(73+math.ceil(len(repos)/(2 if mobile else 4))*81 for _,repos in GROUPS)+45
    b=eyebrow(36,45,'02 / OPEN SOURCE ATLAS')
    b+=txt(36,112,'Built in the open.',43 if mobile else 58,WHITE,400,'Georgia, serif')
    b+=txt(38,155,f'{len(PRS)} merged PRs  /  {len(COUNTS)} upstream repositories',23 if mobile else 28,GOLD,500)
    b+=txt(38,195,'Features, fixes, tests, refactors & documentation.',19 if mobile else 23,MUTED)
    y=230; colw=254 if mobile else 266; cols=2 if mobile else 4
    for gi,(name,repos) in enumerate(GROUPS):
        b+=txt(36,y+18,name,17,JADE,600,extra='letter-spacing="1.5"')
        b+=line(36,y+31,w-36,y+31)
        for idx,repo in enumerate(repos):
            x=36+(idx%cols)*(colw+14);yy=y+48+(idx//cols)*81
            b+=rect(x,yy,colw,67,'#1c3037',10)
            b+=rect(x,yy,3,67,JADE,0)
            label=SHORT.get(repo,repo.split('/')[1])
            b+=txt(x+14,yy+28,label,19 if mobile else 18,WHITE,600)
            b+=txt(x+14,yy+51,f'{COUNTS[repo]} merged',19 if mobile else 15,MUTED)
            b+=dot(x+colw-18,yy+44,3,GOLD,-idx*.3)
        y+=48+math.ceil(len(repos)/cols)*81+25
    b+=txt(36,h-31,'Every contribution links to its upstream pull request.',17,MUTED)
    b+=txt(w-36,h-31,DATA['updated_at'],15,MUTED,extra='text-anchor="end"') if not mobile else ''
    svg('oss-atlas-mobile.svg' if mobile else 'oss-atlas.svg',w,h,'All '+str(len(COUNTS))+' upstream repositories with merged PR counts, including code, tests and documentation.',b)

def pipeline(mobile=False):
    w,h=(600,770) if mobile else (1200,360)
    b=eyebrow(36,43,'03 / CREATIVE ENGINEERING')+txt(36,100,'Script to Video',47,WHITE,600)
    b+=txt(38,142,'From an article to a moving explanation.',23,MUTED,400,'Georgia, serif')
    labels=[('01','RESEARCH','Source & script'),('02','DIRECT','Voice & timeline'),('03','RENDER','3D & motion'),('04','DELIVER','MP4 + source')]
    for i,(n,title,sub) in enumerate(labels):
        x=36 if mobile else 36+i*291;y=180+i*133 if mobile else 190
        ww=528 if mobile else 255
        b+=rect(x,y,ww,108,'#203139',12)+txt(x+17,y+30,n,17,GOLD,500)
        b+=txt(x+53,y+34,title,23,WHITE,600)+txt(x+17,y+77,sub,19,MUTED)
        if mobile:
            if i<3:b+=line(x+270,y+109,x+270,y+130,JADE,3,extra='class="trace"')
        elif i<3:b+=line(x+257,y+53,x+289,y+53,JADE,3,extra='class="trace"')
        for j in range(6):
            hh=12+(j*7+i*3)%20
            b+=f'<rect class="bar" style="animation-delay:-{j*.25+i}s" x="{x+ww-61+j*6}" y="{y+82-hh}" width="3" height="{hh}" fill="{JADE}"/>'
    svg('video-pipeline-mobile.svg' if mobile else 'video-pipeline.svg',w,h,'Script to Video: evidence research, narration, Three.js animation, rendering and editable delivery.',b)

def web3(mobile=False):
    w,h=(600,755) if mobile else (1200,430)
    b=eyebrow(36,44,'04 / WEB3 + DATA SYSTEMS')+txt(36,108,'Follow the data.',46 if mobile else 57,WHITE,400,'Georgia, serif')
    b+=txt(38,151,'On-chain events to research and execution.',22 if mobile else 26,MUTED)
    yy=209
    labels=[('EVM / SOLANA','Events & contracts'),('DATA SYSTEMS','Pipelines & storage'),('EXECUTION','Trading & risk')]
    for i,(l,s) in enumerate(labels):
        x=36 if mobile else 36+i*390;y=yy+i*157 if mobile else yy
        b+=rect(x,y,528 if mobile else 348,123,'#1b2d35',13)
        b+=txt(x+22,y+36,l,24,JADE,600)+txt(x+22,y+72,s,22,WHITE)
        b+=f'<path d="M{x+22} {y+99} q30 -20 60 0 t60 0 t60 0 t60 0" fill="none" stroke="{GOLD}" stroke-width="2" class="draw"/>'
        if not mobile and i<2:b+=line(x+350,y+60,x+387,y+60,JADE,2,extra='class="trace"')
    b+=txt(36,h-27,'Solidity / Python / TypeScript / ClickHouse / Redis',18,MUTED)
    svg('web3-mobile.svg' if mobile else 'web3.svg',w,h,'Web3 engineering: on-chain applications, data pipelines, research and trading systems.',b)

def stack(mobile=False):
    w,h=(600,550) if mobile else (1200,350)
    b=eyebrow(36,44,'05 / TOOLS OF THE TRADE')
    rows=[('BUILD','TypeScript   Python   Rust   Solidity'),('PRODUCT','React   Next.js   Three.js   Tailwind'),('AGENTS','RAG   Tool Calling   MCP   SSE'),('DATA','SQL   ClickHouse   Redis   SQLite'),('SHIP','Linux   Docker   Git   CI / CD')]
    for i,(name,tools) in enumerate(rows):
        y=90+i*(87 if mobile else 48)
        b+=txt(36,y,name,16,JADE,600,extra='letter-spacing="1.8"')
        b+=txt(36 if mobile else 230,y+34 if mobile else y,tools,22 if mobile else 24,WHITE)
        b+=line(36,y+49 if mobile else y+18,w-36,y+49 if mobile else y+18)
    svg('stack-mobile.svg' if mobile else 'stack.svg',w,h,'Technology stack by engineering area.',b)

def archive():
    lines=['# Open-source contributions','',f'**{len(PRS)} merged pull requests across {len(COUNTS)} upstream repositories.**','',f'Updated: {DATA["updated_at"]}. Scope: PRs authored by `ninglinLiu`, merged upstream, excluding repositories owned by `ninglinLiu`. Features, fixes, tests, refactoring and documentation are all included.','', '[Back to profile](../README.md) · [Live GitHub search](https://github.com/search?q=is%3Apr+author%3AninglinLiu+is%3Amerged+-user%3AninglinLiu&type=pullrequests)','']
    for repo,count in sorted(COUNTS.items(),key=lambda p:(-p[1],p[0])):
        lines += [f'## {repo} · {count} merged','', '| Pull request | Merged (UTC) |','|---|---|']
        for p in sorted([p for p in PRS if p['repository']==repo],key=lambda p:p['merged_at'],reverse=True):
            title=p['title'].replace('|','\\|').replace('\n',' ')
            lines.append(f'| [#{p["number"]} — {title}]({p["url"]}) | {p["merged_at"][:10]} |')
        lines+=['']
    (ROOT/'docs').mkdir(exist_ok=True)
    (ROOT/'docs/OPEN_SOURCE.md').write_text('\n'.join(lines),encoding='utf-8')

def main():
    for mobile in [False,True]:
        hero(mobile);omni(mobile);atlas(mobile);pipeline(mobile);web3(mobile);stack(mobile)
    archive()
    readme=ROOT/'README.md'
    content=readme.read_text(encoding='utf-8')
    content=re.sub(r'\d+ merged upstream PRs across \d+ repositories',f'{len(PRS)} merged upstream PRs across {len(COUNTS)} repositories',content)
    content=re.sub(r'\d+ merged PRs in \d+ upstream repositories',f'{len(PRS)} merged PRs in {len(COUNTS)} upstream repositories',content)
    content=re.sub(r'Snapshot: \d{4}-\d{2}-\d{2}',f'Snapshot: {DATA["updated_at"]}',content)
    readme.write_text(content,encoding='utf-8')
    print(f'Built 12 animated SVGs and index for {len(PRS)} PRs / {len(COUNTS)} repositories.')

if __name__=='__main__':main()
