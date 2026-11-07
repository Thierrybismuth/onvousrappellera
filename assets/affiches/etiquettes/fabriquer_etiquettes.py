import json, urllib.request
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/truetype/google-fonts/'
RED=(225,6,19); DARK=(25,25,25)
DPI=300; cm=lambda v:int(round(v/2.54*DPI))
import sys,os,re,unicodedata
S=json.load(open('/home/claude/onvousrappellera/seances.json'))['seances']
JC={'Lundi':'Lun.','Mardi':'Mar.','Mercredi':'Mer.','Jeudi':'Jeu.','Vendredi':'Ven.','Samedi':'Sam.','Dimanche':'Dim.'}
def court(adr):
    a=adr.replace(', 75019 Paris',', Paris 19e').replace(', 75018 Paris',', Paris 18e').replace(', 69007 Lyon',', Lyon 7e')
    import re; return re.sub(r', \d{5} ',', ',a)
groups=[]; idx={}
for x in S:
    k=(x['ville'],x['theatre'])
    if k not in idx: idx[k]=len(groups); groups.append({'ville':x['ville'],'theatre':x['theatre'],'adresse':x['adresse'],'jours':[],'prec':x.get('precision','')})
    g=groups[idx[k]]; j=x['jour'].rsplit(' ',1)[0]
    d=next((d for d in g['jours'] if d['j']==j),None)
    if d: d['h'].append(x['heure'])
    else: g['jours'].append({'j':j,'h':[x['heure']]})
def lignes(g):
    J=g['jours']; L=[]
    hs=[(', '.join(d['h'][:-1])+' et '+d['h'][-1]) if len(d['h'])>1 else d['h'][0] for d in J]
    if len(J)==1:
        L=[J[0]['j'], hs[0]+(' — '+g['prec'] if g['prec'] else '')]
    elif len(set(hs))==1:
        L=[d['j'] for d in J]+[hs[0]]
    else:
        L=[JC[d['j'].split()[0]]+' '+' '.join(d['j'].split()[1:])+' · '+h for d,h in zip(J,hs)]
    return L
def fit(d,t,fn,size,maxw):
    while size>12:
        f=ImageFont.truetype(F+fn,size)
        if d.textlength(t,font=f)<=maxw: return f
        size-=4
    return ImageFont.truetype(F+fn,size)
def etiquette(g,W,H):
    z=H/cm(11)
    im=Image.new('RGB',(W,H),(255,236,90)); d=ImageDraw.Draw(im)
    rows=[(g['ville'].upper(),'Poppins-Bold.ttf',int(230*z),RED)]
    cols=[DARK,RED]
    for i,t in enumerate(lignes(g)): rows.append((t,'Poppins-Bold.ttf',int(150*z),cols[i%2]))
    rows.append((g['theatre'],'Poppins-Bold.ttf',int(150*z),DARK if len(rows)%2==1 else RED))
    rows.append((court(g['adresse']),'Poppins-Bold.ttf',int(105*z),RED))
    fonts=[fit(d,t,fn,s,W-cm(1.2*z)) for t,fn,s,c in rows]
    hs=[f.size*1.18 for f in fonts]; tot=sum(hs)
    if tot>H-cm(1*z):
        k=(H-cm(1*z))/tot; fonts=[ImageFont.truetype(F+r[1],int(f.size*k)) for f,r in zip(fonts,rows)]; hs=[f.size*1.18 for f in fonts]; tot=sum(hs)
    y=(H-tot)/2
    for (t,fn,s,c),f,h in zip(rows,fonts,hs):
        tw=d.textlength(t,font=f); d.text(((W-tw)/2,y),t,fill=c,font=f); y+=h
    return im

FORMATS={'A2':(cm(16.3),cm(11.2),2,1,False),'A3':(cm(11.5),cm(7.8),2,2,True),'A4':(cm(8.1),cm(5.5),4,2,False)}
import math, random
def slug(t): return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFD',t).encode('ascii','ignore').decode().lower()).strip('-')
def postit(lab):
    W,H=lab.size; p=lab.convert('RGBA')
    sh=Image.new('L',(W,H),0); ds=ImageDraw.Draw(sh)
    for i in range(int(H*0.18)):        # léger dégradé en bas, papier qui se décolle
        ds.line((0,H-1-i,W,H-1-i),fill=int(38*(1-i/(H*0.18))))
    dark=Image.new('RGBA',(W,H),(150,110,0,255)); p=Image.composite(dark,p,sh.point(lambda v:v))
    # coin bas droit corné
    c=int(min(W,H)*0.09); d=ImageDraw.Draw(p)
    d.polygon([(W-c,H),(W,H-c),(W,H)],fill=(255,255,255,0))
    d.polygon([(W-c,H),(W,H-c),(W-c*0.92,H-c*0.92)],fill=(232,205,60,255))
    return p
A4=(cm(21),cm(29.7)); os.makedirs('out',exist_ok=True); fichiers=[]
fl=ImageFont.truetype(F+'Poppins-Medium.ttf',cm(0.35))
for f in os.listdir('out'):
    if f.endswith('.pdf'): os.remove('out/'+f)
for fmt,(W,H,n,nc,pays) in FORMATS.items():
    A4=(cm(29.7),cm(21)) if pays else (cm(21),cm(29.7))
    for gi,g in enumerate(groups):
        lab=postit(etiquette(g,W,H))
        p=Image.new('RGB',A4,'white'); d=ImageDraw.Draw(p)
        d.text((cm(1.2),cm(0.8)),g['ville']+' — '+g['theatre']+' · post-it pour l\'affiche '+fmt+' — à découper sur les pointillés',fill=(140,140,140),font=fl)
        gap=(A4[1]-cm(1.6)-n*(H+cm(0.6)))//(n+1)
        colw=A4[0]//nc
        for k in range(n*nc):
            ang=[-3,2.5,2,-2.5][k%4]; row,colk=k//nc,k%nc
            r=lab.rotate(ang,expand=True,resample=Image.BICUBIC)
            x=colk*colw+(colw-r.width)//2; y=cm(1.6)+gap+row*(H+cm(0.6)+gap)
            p.paste(r,(x,y),r)
            # pointillés autour du post-it penché
            cx,cy=x+r.width/2,y+r.height/2; t=math.radians(-ang)
            pts=[(-W/2,-H/2),(W/2,-H/2),(W/2,H/2),(-W/2,H/2)]
            P=[(cx+px*math.cos(t)-py*math.sin(t), cy+px*math.sin(t)+py*math.cos(t)) for px,py in pts]
            for i in range(4):
                (x0,y0),(x1,y1)=P[i],P[(i+1)%4]; L=math.hypot(x1-x0,y1-y0); st=40
                for s0 in range(0,int(L),2*st):
                    a0=s0/L; a1=min(1,(s0+st)/L)
                    d.line((x0+(x1-x0)*a0-((x1-x0)/L)*cm(0.15)*0, y0+(y1-y0)*a0, x0+(x1-x0)*a1, y0+(y1-y0)*a1),fill=(150,150,150),width=4)
        nom='out/etiquettes-%s-%s-%s.pdf'%(fmt,slug(g['ville']),slug(g['theatre']))
        p.save(nom,resolution=DPI); fichiers.append((fmt,g['ville'],g['theatre'],nom))
        if g['theatre']=='Théâtre Artisse': p.resize((A4[0]//6,A4[1]//6)).save('apercu_planche_%s.jpg'%fmt)
json.dump(fichiers,open('out/liste.json','w'),ensure_ascii=False)
print(len(fichiers),'planches')
