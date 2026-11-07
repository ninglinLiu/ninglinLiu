"""Render the contribution city, language profile and curated topic gallery."""
from datetime import date
from pathlib import Path
import base64
import html
import json
import math
import mimetypes
from build_profile import svg, txt, rect, line, dot, eyebrow, WHITE, MUTED, JADE, GOLD, INK

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/activity.json').read_text(encoding='utf-8'))
TOPICS=json.loads((ROOT/'data/topics.json').read_text(encoding='utf-8'))

def poly(points,color):
    return '<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{color}"/>'

def image_icon(icon,x,y,size):
    path=ROOT/'assets/icons'/icon.get('file',icon['slug']+'.svg')
    mime=mimetypes.guess_type(path.name)[0] or 'image/svg+xml'
    data=base64.b64encode(path.read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:{mime};base64,{data}"/>'

def activity(mobile=False):
    w,h=(600,830) if mobile else (1200,520)
    days=D['calendar']; total=sum(d['count'] for d in days)
    active=sum(d['count']>0 for d in days);best=run=0
    for d in days:
        run=run+1 if d['count'] else 0;best=max(best,run)
    peak=max(d['count'] for d in days)
    b='<style>.activity-cube{animation:city 5s ease-in-out infinite}@keyframes city{0%,100%{opacity:.8}50%{opacity:1}}</style>'
    b+=eyebrow(36,44,'06 / GITHUB ACTIVITY')
    b+=txt(36,104,'A year in the making.',44 if mobile else 54,WHITE,400,'Georgia, serif')
    b+=txt(38,145,f'{days[0]["date"]} — {days[-1]["date"]}',20,MUTED)
    # Every tile is one actual day. Height is a logarithmic scale of contribution count.
    start=date.fromisoformat(days[0]['date']); offset=(start.weekday()+1)%7
    sx=8.7 if mobile else 11.7; sy=3.0 if mobile else 3.4
    ox=92 if mobile else 105; oy=227 if mobile else 231
    for i,d in enumerate(days):
        week=(i+offset)//7; weekday=(i+offset)%7
        x=ox+(week-weekday)*sx;y=oy+(week+weekday)*sy
        hh=2 if not d['count'] else 7+math.log1p(d['count'])*10
        palette=['#243940','#286355','#3e9676','#62c798','#b7ecc3']
        color=palette[d['level']]
        a=(x,y);bb=(x+sx-1,y+sy);c=(x,y+2*sy);dd=(x-sx+1,y+sy)
        motion=f' class="activity-cube" style="animation-delay:-{i%13*.4}s"' if d['count'] else ''
        b+=f'<g{motion}><title>{d["date"]}: {d["count"]} contributions</title>'
        b+=poly([dd,c,(c[0],c[1]-hh),(dd[0],dd[1]-hh)],'#264d44' if d['count'] else '#172d32')
        b+=poly([bb,c,(c[0],c[1]-hh),(bb[0],bb[1]-hh)],'#39775c' if d['count'] else '#1c363c')
        b+=poly([(p[0],p[1]-hh) for p in [a,bb,c,dd]],color)+'</g>'
    b+=f'<path class="trace" d="M40 {450 if mobile else 462} H{555 if mobile else 722}" stroke="{JADE}" stroke-width="2" fill="none" opacity=".4"/>'
    stats=[(f'{total:,}','CONTRIBUTIONS'),(str(active),'ACTIVE DAYS'),(str(best)+' days','LONGEST STREAK'),(str(peak),'BEST DAY')]
    for i,(value,label) in enumerate(stats):
        x=36+(i%2)*274 if mobile else 805+(i%2)*185
        y=497+(i//2)*129 if mobile else 212+(i//2)*128
        b+=txt(x,y,value,42 if mobile else 38,WHITE,600)+txt(x,y+30,label,16,JADE,600)
        b+=dot(x+220 if mobile else x+155,y-12,3,GOLD,-i*.7)
    b+=txt(36,h-33,'Public GitHub contribution calendar · rolling 12 months',18,MUTED)
    svg('activity-mobile.svg' if mobile else 'activity.svg',w,h,'Public GitHub activity: contributions over the last 365 days.',b)

def languages(mobile=False):
    w,h=(600,875) if mobile else (1200,500)
    languages=D['languages'];total=sum(d['bytes'] for d in languages)
    b=eyebrow(36,43,'07 / LANGUAGE ACTIVITY')
    b+=txt(36,101,'The code behind the work.',38 if mobile else 53,WHITE,400,'Georgia, serif')
    b+=txt(38,144,f'{len(languages)} languages  /  {len(D["repositories"])} public repositories',22 if mobile else 25,GOLD,500)
    x=36
    for lang in languages:
        width=(w-72)*lang['bytes']/total
        b+=rect(x,177,width,18,lang['color'],0);x+=width
    for i,lang in enumerate(languages[:8]):
        x=36 if mobile else 36+(i%2)*574
        y=250+i*67 if mobile else 248+(i//2)*49
        b+=f'<circle cx="{x+7}" cy="{y-7}" r="7" fill="{lang["color"]}"/>'
        b+=txt(x+24,y,lang['name'],23,WHITE,500)
        b+=txt(w-36 if mobile else x+514,y,f'{lang["bytes"]/total*100:.1f}%',22,MUTED,extra='text-anchor="end"')
        b+=line(x+24,y+16,w-36 if mobile else x+514,y+16)
    b+=txt(36,h-54,'Measured by code bytes in public, non-fork repositories.',17,MUTED)
    b+=txt(36,h-27,'Updated '+D['updated_at'],17,MUTED)
    svg('languages-mobile.svg' if mobile else 'languages.svg',w,h,'Language distribution across owned public non-fork repositories, measured in bytes.',b)

def topics(mobile=False):
    w=600 if mobile else 1200;cols=4 if mobile else 8
    groups=[('DEVELOPMENT & PLATFORMS',[i for i in TOPICS if i['group']=='development']),('WEB3 & ON-CHAIN ECOSYSTEM',[i for i in TOPICS if i['group']=='web3'])]
    step=126 if mobile else 121
    h=190+sum(55+math.ceil(len(items)/cols)*step+24 for _,items in groups)+35
    b=eyebrow(36,44,'08 / TOPICS & ECOSYSTEM')
    b+=txt(36,107,'A wider world of building.',37 if mobile else 54,WHITE,400,'Georgia, serif')
    b+=txt(38,149,'Tools, platforms and on-chain ecosystems I follow.',20 if mobile else 24,MUTED)
    y=190;cell=(w-72)/cols
    for label,items in groups:
        b+=txt(36,y+18,label,17,JADE,600,extra='letter-spacing="1"')
        b+=line(36,y+32,w-36,y+32)
        for i,icon in enumerate(items):
            x=36+(i%cols)*cell;yy=y+45+(i//cols)*step
            b+=rect(x,yy,cell-10,step-12,'#1b3037',13)
            # Light backing preserves legibility of black brand marks.
            light=icon['group']=='development' or icon['slug']=='circle'
            b+=rect(x+(cell-10)/2-31,yy+8,62,62,'#edf1ed' if light else '#101c22',12)
            b+=image_icon(icon,x+(cell-10)/2-24,yy+15,48)
            words=icon['name'].split(' ',1) if len(icon['name'])>15 else [icon['name']]
            for j,word in enumerate(words):
                b+=txt(x+(cell-10)/2,yy+91+j*17,word,15 if len(word)>12 else 17,WHITE,500,extra='text-anchor="middle"')
        y+=55+math.ceil(len(items)/cols)*step+24
    b+=dot(40,h-29,4,JADE)+txt(53,h-23,'BUILD  /  EXPLORE  /  CONNECT',16,JADE,600,extra='letter-spacing="1.5"')
    svg('topics-mobile.svg' if mobile else 'topics.svg',w,h,'Curated development and Web3 topic icons.',b)

if __name__=='__main__':
    for mobile in [False,True]:activity(mobile);languages(mobile);topics(mobile)
    print(f'Built activity, language and topic panels with {len(TOPICS)} icons.')
