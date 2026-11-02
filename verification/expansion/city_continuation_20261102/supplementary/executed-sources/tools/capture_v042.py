#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, math
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parents[1]
O=R/'verification';O.mkdir(exist_ok=True)
HTML=R/'JOUER_FALLOUT_MISTRAL_v0.42.html'
H=HTML.read_text(encoding='utf-8')
CAT=json.loads((R/'data/fallout_layer_v042.json').read_text(encoding='utf-8'))
shots=[];errors=[]

def font(size,bold=False):
    p='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    try:return ImageFont.truetype(p,size)
    except:return None

# Computed catalog overview: exact generated coordinates, not concept art.
W,HMAP=1280,760
canvas=Image.new('RGB',(W,HMAP),(10,15,11));d=ImageDraw.Draw(canvas)
d.text((40,24),'COUCHE FALLOUT TERRITORIALE v0.42 · 248 IMPLANTATIONS PERSISTANTES',fill=(239,226,178),font=font(27,True))
d.text((40,62),'Positions WGS84 déterministes au-dessus des huit macro-régions réelles',fill=(161,187,157),font=font(16))
west,east=5.245,5.77;south,north=43.115,43.43
left,top,right,bottom=55,105,1225,680
kind_colors={'shelter':(231,210,103),'settlement':(115,194,126),'outpost':(101,172,195),'interior':(176,177,171),'nest':(191,91,66),'elite':(219,120,57),'boss':(225,64,65),'landmark':(150,132,191),'caravan':(202,167,94)}
macros=CAT['macros']
for mid,m in macros.items():
    b=m['bbox']; y1=bottom-(b[0]-south)/(north-south)*(bottom-top);x1=left+(b[1]-west)/(east-west)*(right-left);y2=bottom-(b[2]-south)/(north-south)*(bottom-top);x2=left+(b[3]-west)/(east-west)*(right-left)
    d.rectangle((x1,y2,x2,y1),outline=(64,84,66),width=1)
    d.text((x1+5,y2+5),m['label'].replace('MACRO-RÉGION · ',''),fill=(109,133,108),font=font(11,True))
for s in CAT['sites']:
    x=left+(s['lon']-west)/(east-west)*(right-left);y=bottom-(s['lat']-south)/(north-south)*(bottom-top)
    r=5 if s['kind']=='boss' else 4 if s['kind'] in ('shelter','elite') else 2
    col=kind_colors[s['kind']];d.ellipse((x-r,y-r,x+r,y+r),fill=col)
# legend
x0,y0=55,700
for i,(k,col) in enumerate(kind_colors.items()):
    x=x0+(i%5)*235;y=y0+(i//5)*24;d.ellipse((x,y,x+10,y+10),fill=col);d.text((x+16,y-2),f"{k.upper()} · {CAT['meta']['counts'][k]}",fill=(210,220,202),font=font(12))
chart=O/'v042_00_catalogue_territorial.png';canvas.save(chart);shots.append((chart,'Catalogue territorial calculé','Les 248 points sont dessinés depuis le catalogue final WGS84. Ce graphique décrit le placement, pas une capture satellite.'))

def site(kind,macro='geo_huveaune',index=0):
    rows=[s for s in CAT['sites'] if s['macro']==macro and s['kind']==kind]
    return rows[index]

with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
    p=b.new_page(viewport={'width':1440,'height':960});p.set_default_timeout(12000);p.on('pageerror',lambda e:errors.append(str(e)))
    p.route('https://hykklcvvwjwhcvukbzts.supabase.co/**',lambda r:r.abort())
    p.set_content(H,wait_until='load');p.wait_for_timeout(700)
    p.evaluate("""() => {const st={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>st[k]??null,setItem:(k,v)=>st[k]=String(v),removeItem:k=>delete st[k],clear:()=>Object.keys(st).forEach(k=>delete st[k])}});Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:536870912})}})}""")
    def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
    def snap(name,title,note):
        p.evaluate("document.getElementById('toastStack').innerHTML=''")
        p.wait_for_timeout(80);path=O/name;p.screenshot(path=str(path));shots.append((path,title,note));print('CAP',name,flush=True)
    def load_at(s):
        c('v017LoadMacro',s['macro']);c('v017SetPlayerLatLon',s['lat'],s['lon']);c('v042Update',.9);p.wait_for_timeout(160)
        q=c('v042Project',s['id']);return q
    def frame(s,dist=20,height=3.0,angle=.78,pitch=-.10):
        q=c('v042Project',s['id']);target=q['free'];cx=target[0]+math.sin(angle)*dist;cz=target[2]+math.cos(angle)*dist;yaw=math.atan2(target[0]-cx,-(target[2]-cz));c('v021RenderAt',[cx,target[1]+height,cz],yaw,pitch,2)
    c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True);c('v020Reset')
    snap('v042_01_menu.png','Menu v0.42','La nouvelle version est identifiée comme couche Fallout territoriale ; les outils internes restent dans Admin.')

    # Entire territorial map with all macro-regions discovered.
    c('v020Load','transit_depot')
    for mid in CAT['macros']:c('v042DiscoverMacro',mid)
    c('v042Map');p.wait_for_timeout(120)
    snap('v042_02_pip_carte_complete.png','Pip-Boy · couche complète','Les 248 implantations sont consultables, filtrables et suivies par macro-région.')
    c('closePip')

    settlement=site('settlement')
    load_at(settlement);frame(settlement,23,3.5,.85,-.11)
    snap('v042_03_colonie.png','Colonie habitée','Une colonie n’instancie que ses bâtiments, collisions et quatre PNJ lorsque le joueur s’en approche.')
    world=c('v042World');pn=next(n for n in world['npcs'] if n['site']==settlement['id'])
    c('v042Talk',pn['id']);snap('v042_04_dialogue_contrat.png','PNJ et contrat territorial','Les habitants disposent d’un dialogue contextualisé, de commerce simple et de contrats vers une menace locale.')
    c('v020ModalDismiss')

    nest=site('nest',index=2)
    load_at(nest);frame(nest,22,4.0,-.7,-.14)
    snap('v042_05_nid.png','Nid de créatures','Les nids persistent, utilisent le bestiaire existant et se réinitialisent uniquement selon leur délai de respawn.')

    elite=site('elite')
    load_at(elite);frame(elite,24,4.2,.65,-.14)
    snap('v042_06_elite.png','Repaire élite','Chaque macro-région possède trois repaires vétérans avec un ennemi élite distinct et des récompenses persistantes.')

    boss=site('boss')
    load_at(boss);frame(boss,27,5.0,-.55,-.16)
    snap('v042_07_boss_regional.png','Boss régional','Un boss et son escorte sont instanciés localement ; sa défaite est mémorisée par région.')

    shelter=site('shelter')
    load_at(shelter);frame(shelter,21,3.6,.82,-.10)
    snap('v042_08_abri_exterieur.png','Entrée d’abri','Les seize abris disposent d’une implantation stable, d’une entrée physique et d’un dossier propre.')
    c('v042Enter',shelter['id']);p.wait_for_timeout(180);c('v028Set',{'lamp':True});c('v021RenderAt',[0,2.2,44],-1.063,-.05,2)
    snap('v042_09_abri_interieur.png','Abri visitable','L’intérieur configurable possède six sous-zones, un trajet principal, un terminal, des menaces et un noyau à sécuriser.')
    c('v042Defeat',shelter['id']);c('v042Claim',shelter['id']);snap('v042_10_abri_securise.png','Abri sécurisé','Après neutralisation des menaces, le noyau peut être revendiqué et la progression est sauvegardée.')
    c('v020ModalDismiss')

    # Regional dashboard and mobile view.
    c('v020Load','transit_depot');c('v042Map');p.wait_for_timeout(100)
    snap('v042_11_progression_regionale.png','Progression régionale','Le tableau distingue découvertes, sécurisations et boss encore actifs dans les huit macro-régions.')
    p.set_viewport_size({'width':390,'height':844});p.wait_for_timeout(100)
    snap('v042_12_mobile.png','Carte sur écran étroit','La couche territoriale reste défilable à 390 × 844 ; il s’agit d’une fenêtre simulée, pas d’une certification matérielle.')
    b.close()

# 2-column report montage.
tw,th=620,348;gap=22;head=122;rows=math.ceil(len(shots)/2)
report=Image.new('RGB',(tw*2+gap*3,head+rows*(th+100)+gap),(9,14,10));dr=ImageDraw.Draw(report)
dr.text((gap,22),'FALLOUT : MISTRAL — v0.42 · COUCHE FALLOUT TERRITORIALE',fill=(239,225,176),font=font(28,True))
dr.text((gap,62),'Captures directes du HTML final et catalogue calculé depuis les 248 coordonnées persistantes.',fill=(163,187,157),font=font(15))
for i,(path,title,note) in enumerate(shots):
    im=Image.open(path).convert('RGB');im.thumbnail((tw,th));bg=Image.new('RGB',(tw,th),(0,0,0));bg.paste(im,((tw-im.width)//2,(th-im.height)//2))
    x=gap+(i%2)*(tw+gap);y=head+(i//2)*(th+100);report.paste(bg,(x,y));dr.rectangle((x,y+th,x+tw,y+th+100),fill=(19,28,21));dr.text((x+12,y+th+8),title,fill=(232,220,171),font=font(17,True));dr.text((x+12,y+th+37),note[:112],fill=(164,181,156),font=font(13))
report_path=R/'RAPPORT_VISUEL_V0.42.png';report.save(report_path)
meta={'version':'0.42.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'errors':errors,'disclosure':'All game screenshots are captured from the final HTML. Cameras and progression states are prepared for presentation. The catalog map is computed from the deterministic WGS84 catalog and is not satellite imagery.','shots':[{'file':x.name,'title':t,'note':n} for x,t,n in shots]}
(O/'CAPTURES_V042.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('REPORT',report_path,'shots',len(shots),'errors',errors)
raise SystemExit(bool(errors))
