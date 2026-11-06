/* Facture entreprise sur la billetterie OVR (SAS ODYSKILLS).
   - FE.monter(ancre, champSociete) : ajoute la case « Besoin d'une facture » + champs, sous l'élément ancre.
   - FE.lire() : null si la case n'est pas cochée ; {erreur} si incomplet ; sinon {raison, siren, adresse}.
   - FE.memoriser(achat) : garde la demande le temps du paiement Stripe.
   - FE.auRetour(msgEl) : au retour ?merci, émet la facture (numéro suivant de l'onglet Facturation), l'envoie et affiche le lien. */
(function(){
  var GW='https://thierryb.app.n8n.cloud/webhook/sheets-gateway',
      MAIL='https://thierryb.app.n8n.cloud/webhook/send-email-unitaire',
      SHEET='1CqFrk0RgkO9xJuglSTPz3dgcd-tbU33VrYaM0lt_BJg',
      CLE='ovr_facture_attente', API='https://recherche-entreprises.api.gouv.fr/search?per_page=5&q=';
  var $=function(i){return document.getElementById(i);};
  function esc(x){return String(x==null?'':x).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');}
  var socExt=null, choisi=false;

  function css(){ if($('fe-css')) return; var s=document.createElement('style'); s.id='fe-css';
    s.textContent='.fe-case{display:flex;gap:.45rem;align-items:center;font-size:.8rem;color:#666;margin:.7rem 0 .2rem;cursor:pointer}'
    +'.fe-case input{margin:0}.fe-bloc{border:1px solid #e3e3e3;border-radius:6px;padding:.7rem .8rem;margin:.4rem 0 .6rem;background:#fff;color:#222}'
    +'.fe-bloc label{display:block;font-size:.78rem;color:#555;margin:.5rem 0 .2rem}.fe-bloc input{width:100%;box-sizing:border-box;padding:.55rem .6rem;border:1px solid #ccc;border-radius:5px;font:inherit;font-size:.9rem;background:#fff;color:#222}'
    +'.fe-sugg{list-style:none;margin:.3rem 0 0;padding:0;border:1px solid #eee;border-radius:5px;max-height:220px;overflow:auto}.fe-sugg li{padding:.45rem .6rem;font-size:.82rem;cursor:pointer;border-bottom:1px solid #f2f2f2;line-height:1.35}'
    +'.fe-sugg li:hover{background:#f7f4ee}.fe-sugg li small{color:#777;display:block}.fe-note{font-size:.74rem;color:#777;margin:.4rem 0 0}';
    document.head.appendChild(s); }

  function chercher(q){
    var ul=$('fe-sugg'); if(!q||q.length<3){ ul.innerHTML=''; return; }
    fetch(API+encodeURIComponent(q)).then(function(r){return r.json();}).then(function(d){
      var R=(d&&d.results||[]).filter(function(x){return x.etat_administratif!=='C';});
      ul.innerHTML=R.map(function(x,i){ var a=(x.siege&&x.siege.adresse)||'';
        return '<li data-i="'+i+'"><b>'+esc(x.nom_complet)+'</b><small>SIREN '+esc(x.siren)+' · '+esc(a)+'</small></li>'; }).join('');
      Array.prototype.forEach.call(ul.children,function(li){ li.addEventListener('click',function(){ var x=R[+li.dataset.i];
        $('fe-raison').value=x.nom_complet||''; $('fe-siren').value=x.siren||''; $('fe-adresse').value=(x.siege&&x.siege.adresse)||'';
        if(socExt && !socExt.value) socExt.value=x.nom_complet||''; choisi=true; ul.innerHTML=''; }); });
    }).catch(function(){ ul.innerHTML=''; });
  }
  var minu=null; function plusTard(q){ clearTimeout(minu); minu=setTimeout(function(){chercher(q);},400); }

  function monter(ancre, champSociete){
    if(!ancre||$('fe-case')) return; css(); socExt=champSociete||null;
    var w=document.createElement('div');
    w.innerHTML='<label class="fe-case"><input type="checkbox" id="fe-case">Besoin d\'une facture</label>'
      +'<div class="fe-bloc" id="fe-bloc" style="display:none">'
      +'<label for="fe-raison">Nom de l\'entreprise</label><input id="fe-raison" type="text" autocomplete="organization" placeholder="Tapez le nom, puis choisissez dans la liste">'
      +'<ul class="fe-sugg" id="fe-sugg"></ul>'
      +'<label for="fe-siren">SIREN</label><input id="fe-siren" type="text" inputmode="numeric" maxlength="11">'
      +'<label for="fe-adresse">Adresse de facturation</label><input id="fe-adresse" type="text">'
      +'<p class="fe-note">La facture vous est envoyée par mail dès le paiement reçu.</p></div>';
    ancre.parentNode.insertBefore(w, ancre.nextSibling);
    $('fe-case').addEventListener('change',function(){ var on=this.checked; $('fe-bloc').style.display=on?'':'none';
      if(on && socExt && socExt.value.trim() && !$('fe-raison').value){ $('fe-raison').value=socExt.value.trim(); chercher(socExt.value.trim()); } });
    $('fe-raison').addEventListener('input',function(){ choisi=false; plusTard(this.value.trim()); });
    if(socExt) socExt.addEventListener('change',function(){ if($('fe-case').checked && !choisi){ $('fe-raison').value=socExt.value.trim(); chercher(socExt.value.trim()); } });
  }

  function lire(){
    var c=$('fe-case'); if(!c||!c.checked) return null;
    var f={raison:$('fe-raison').value.trim(), siren:$('fe-siren').value.replace(/\D/g,''), adresse:$('fe-adresse').value.trim()};
    if(!f.raison) return {erreur:'Merci d\'indiquer le nom de l\'entreprise à facturer.'};
    if(f.siren.length!==9) return {erreur:'Merci d\'indiquer le SIREN de l\'entreprise (9 chiffres) : choisissez-la dans la liste proposée.'};
    if(!f.adresse) return {erreur:'Merci d\'indiquer l\'adresse de facturation.'};
    return f;
  }
  function memoriser(achat){ var f=lire(); if(!f||f.erreur) return;
    try{ localStorage.setItem(CLE, JSON.stringify({f:f,a:achat,t:Date.now()})); }catch(e){} }

  function post(u,p){ return fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)}).then(function(r){return r.json();}); }
  function deux(n){return ('0'+n).slice(-2);}
  function b64(o){ return btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,''); }

  function auRetour(msgEl){
    var raw=null; try{ raw=localStorage.getItem(CLE); }catch(e){} if(!raw) return;
    var o; try{ o=JSON.parse(raw); }catch(e){ return; }
    try{ localStorage.removeItem(CLE); }catch(e){}
    if(!o||!o.f||!o.a||Date.now()-o.t>3*3600*1000) return;
    var a=o.a, f=o.f, d=new Date(), dateStr=deux(d.getDate())+'/'+deux(d.getMonth()+1)+'/'+d.getFullYear(), an=d.getFullYear();
    var ttc=Math.round(a.pu*a.qty*100)/100, ht=Math.round(ttc/1.055*100)/100, tva=Math.round((ttc-ht)*100)/100;
    var fr=function(n){return n.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2});};
    var objet='ON VOUS RAPPELLERA — '+a.seance+' — '+a.qty+' place'+(a.qty>1?'s':'')+' ('+a.tarif+')';
    post(GW,{action:'read',spreadsheetId:SHEET,range:'Facturation!A1:A1000'}).then(function(r){
      var max=0, re=new RegExp('^'+an+'-(\\d+)$'); (r.values||[]).forEach(function(l){ var m=String(l[0]||'').match(re); if(m) max=Math.max(max,parseInt(m[1],10)); });
      var num=an+'-'+String(max+1).padStart(3,'0');
      var url=location.origin+'/facture.html?d='+b64({n:num,dt:dateStr,c:f.raison,s:f.siren,ad:f.adresse,o:objet,q:a.qty,pu:a.pu,ht:ht,tva:tva,ttc:ttc});
      var ligne=[num,dateStr,'Payée',f.raison,objet,fr(a.pu/1.055),String(a.qty),fr(ht),fr(tva),fr(ttc),'Payée (Stripe) — à rapprocher',dateStr,'Carte bancaire (Stripe)',
        'Billetterie en ligne · SIREN '+f.siren+' · '+f.adresse+' · Facture : '+url, a.prenom||'', a.nom||'', a.email||'', a.portable||''];
      return post(GW,{action:'append',spreadsheetId:SHEET,range:'Facturation!A:R',values:[ligne]}).then(function(){ return {num:num,url:url}; });
    }).then(function(x){
      var lien='<a href="'+x.url+'">'+x.url.split('?')[0]+' — facture '+x.num+'</a>';
      var corps='<p>Bonjour,</p><p>Merci pour votre réservation. Voici votre facture '+x.num+' ('+esc(f.raison)+') :<br><a href="'+x.url+'">Voir et télécharger la facture</a></p><p>À très bientôt au théâtre,<br>ON VOUS RAPPELLERA<br>contact@onvousrappellera.fr</p>';
      post(MAIL,{to:a.email,subject:'Votre facture '+x.num+' — ON VOUS RAPPELLERA',body:corps}).catch(function(){});
      post(MAIL,{to:'bismuththierry@gmail.com',subject:'Facture billetterie '+x.num+' — '+f.raison+' — '+fr(ttc)+' € TTC',
        body:'<p>Facture émise automatiquement après paiement Stripe (à rapprocher de l\'encaissement).</p><p>'+esc(f.raison)+' · SIREN '+esc(f.siren)+'<br>'+esc(f.adresse)+'<br>'+esc(objet)+'<br>'+fr(ttc)+' € TTC</p><p>Acheteur : '+esc((a.prenom||'')+' '+(a.nom||''))+' — '+esc(a.email)+'</p><p><a href="'+x.url+'">Voir la facture</a></p>'}).catch(function(){});
      if(msgEl) msgEl.insertAdjacentHTML('beforeend','<br>Votre facture '+esc(x.num)+' : <a href="'+x.url+'" target="_blank">voir et télécharger</a> (également envoyée par mail).');
    }).catch(function(){
      post(MAIL,{to:'bismuththierry@gmail.com',subject:'⚠️ Facture billetterie NON émise — '+f.raison,body:'<p>Paiement revenu, mais la facture n\'a pas pu être enregistrée. À faire à la main.</p><p>'+esc(f.raison)+' · SIREN '+esc(f.siren)+'<br>'+esc(f.adresse)+'<br>'+esc(objet)+' · '+fr(ttc)+' € TTC<br>Acheteur : '+esc(a.email)+'</p>'}).catch(function(){});
      if(msgEl) msgEl.insertAdjacentHTML('beforeend','<br>Votre facture vous sera envoyée par mail sous 24 heures.');
    });
  }
  window.FE={monter:monter,lire:lire,memoriser:memoriser,auRetour:auRetour};
})();
