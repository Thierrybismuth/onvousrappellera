import json, urllib.request
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/truetype/google-fonts/'
RED=(225,6,19); DARK=(25,25,25)
DPI=300; cm=lambda v:int(round(v/2.54*DPI))
W,H=cm(19),cm(11)
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
    while size>30:
        f=ImageFont.truetype(F+fn,size)
        if d.textlength(t,font=f)<=maxw: return f
        size-=4
    return ImageFont.truetype(F+fn,size)
def etiquette(g):
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    rows=[(g['ville'].upper(),'Poppins-Bold.ttf',230,RED)]
    cols=[DARK,RED]
    for i,t in enumerate(lignes(g)): rows.append((t,'Poppins-Bold.ttf',150,cols[i%2]))
    rows.append((g['theatre'],'Poppins-Bold.ttf',150,DARK if len(rows)%2==1 else RED))
    rows.append((court(g['adresse']),'Poppins-Bold.ttf',105,RED))
    fonts=[fit(d,t,fn,s,W-cm(1.2)) for t,fn,s,c in rows]
    hs=[f.size*1.18 for f in fonts]; tot=sum(hs)
    if tot>H-cm(1):
        k=(H-cm(1))/tot; fonts=[ImageFont.truetype(F+r[1],int(f.size*k)) for f,r in zip(fonts,rows)]; hs=[f.size*1.18 for f in fonts]; tot=sum(hs)
    y=(H-tot)/2
    for (t,fn,s,c),f,h in zip(rows,fonts,hs):
        tw=d.textlength(t,font=f); d.text(((W-tw)/2,y),t,fill=c,font=f); y+=h
    return im
labs=[(g,etiquette(g)) for g in groups]
# planche A4 : 2 étiquettes par page, traits de coupe pointillés
A4=(cm(21),cm(29.7)); pages=[]
for i in range(0,len(labs),2):
    p=Image.new('RGB',A4,'white'); d=ImageDraw.Draw(p)
    for k,(g,im) in enumerate(labs[i:i+2]):
        x=(A4[0]-W)//2; y=cm(2.5)+k*(H+cm(2.5))
        p.paste(im,(x,y))
        for (x0,y0,x1,y1) in [(x,y,x+W,y),(x,y+H,x+W,y+H),(x,y,x,y+H),(x+W,y,x+W,y+H)]:
            n=int(max(x1-x0,y1-y0)/40)
            for s in range(0,n,2):
                if x0==x1: d.line((x0,y0+s*40,x0,y0+(s+1)*40),fill=(150,150,150),width=4)
                else: d.line((x0+s*40,y0,x0+(s+1)*40,y0),fill=(150,150,150),width=4)
    pages.append(p)
pages[0].save('OVR_etiquettes_affiche.pdf',save_all=True,append_images=pages[1:],resolution=DPI)
apercu=Image.new('RGB',(W//4*2+30,(H//4+20)*((len(labs)+1)//2)),(235,235,235))
for i,(g,im) in enumerate(labs):
    t=im.resize((W//4,H//4)); apercu.paste(t,((i%2)*(W//4+30),(i//2)*(H//4+20)))
apercu.save('apercu_etiquettes.jpg',quality=88)
print(len(labs),'étiquettes,',len(pages),'pages A4 ;',[ (g['ville'],g['theatre']) for g,_ in labs])
