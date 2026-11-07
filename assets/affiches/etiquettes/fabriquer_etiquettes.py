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
    hs=[' et '.join(d['h']) for d in J]
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
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
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

FORMATS={'40x60':(cm(15),cm(10.5),2),'A3':(cm(11),cm(6.8),4)}
def slug(t): return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFD',t).encode('ascii','ignore').decode().lower()).strip('-')
A4=(cm(21),cm(29.7)); os.makedirs('out',exist_ok=True); fichiers=[]
fl=ImageFont.truetype(F+'Poppins-Medium.ttf',cm(0.35))
for fmt,(W,H,n) in FORMATS.items():
    for g in groups:
        lab=etiquette(g,W,H)
        p=Image.new('RGB',A4,'white'); d=ImageDraw.Draw(p)
        d.text((cm(1.2),cm(0.8)),g['ville']+' — '+g['theatre']+' · étiquettes pour l\'affiche '+fmt.replace('x',' × ')+' — à découper sur les pointillés',fill=(140,140,140),font=fl)
        gap=(A4[1]-cm(2)-n*H)//(n+1)
        for k in range(n):
            x=(A4[0]-W)//2; y=cm(1.6)+gap+k*(H+gap)
            p.paste(lab,(x,y))
            for (x0,y0,x1,y1) in [(x,y,x+W,y),(x,y+H,x+W,y+H),(x,y,x,y+H),(x+W,y,x+W,y+H)]:
                L=max(x1-x0,y1-y0); st=40
                for s0 in range(0,L,2*st):
                    if x0==x1: d.line((x0,y0+s0,x0,min(y1,y0+s0+st)),fill=(150,150,150),width=4)
                    else: d.line((x0+s0,y0,min(x1,x0+s0+st),y0),fill=(150,150,150),width=4)
        nom='out/etiquettes-%s-%s-%s.pdf'%(fmt,slug(g['ville']),slug(g['theatre']))
        p.save(nom,resolution=DPI); fichiers.append((fmt,g['ville'],g['theatre'],nom))
        if g['theatre']=='Théâtre Clavel': p.resize((A4[0]//6,A4[1]//6)).save('apercu_planche_%s.jpg'%fmt)
json.dump(fichiers,open('out/liste.json','w'),ensure_ascii=False)
print(len(fichiers),'planches')
