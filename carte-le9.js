/* Carte du dîner du Cabaret Le 9 (Toulouse) — même bulle que la page BDR */
(function(){
  var css='.menu9{position:relative;color:#d8281f;text-decoration:underline;cursor:help;font-weight:500;}'+
  '.menu9 .bulle9{display:none;position:absolute;left:50%;bottom:calc(100% + 8px);transform:translateX(-50%);width:320px;max-width:80vw;background:#fff;color:#1c1c1c;border:1px solid #e7e2d8;border-radius:6px;box-shadow:0 10px 28px rgba(22,22,22,.18);padding:12px 14px;font-size:.82rem;line-height:1.45;font-weight:300;text-align:left;z-index:50;text-decoration:none;cursor:default;white-space:normal;}'+
  '.menu9 .bulle9 b{display:block;font-weight:600;color:#161616;margin-bottom:6px;}'+
  '.menu9 .bulle9 i{display:block;font-style:normal;font-weight:600;color:#d8281f;margin-top:6px;font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;}'+
  '.menu9:hover .bulle9,.menu9:focus .bulle9,.menu9.on .bulle9{display:block;}'+
  '@media(max-width:700px){.menu9 .bulle9{position:fixed;left:50%;top:50%;bottom:auto;transform:translate(-50%,-50%);width:90vw;max-width:360px;max-height:80vh;overflow:auto;}}';
  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);
  var CARTE='<span class="bulle9" role="tooltip"><b>Carte</b>Le dîner est servi pour toute arrivée entre 19h et 20h15.<i>Entrées</i>Salade de gésiers flambés, noix, persillade, terrine, mesclun — 13&nbsp;€<br>Salade thaï au wakamé et légumes croquants — 11&nbsp;€<i>À partager… ou pas</i>Planche mixte généreuse charcuterie et fromages — 22&nbsp;€<i>Plats</i>Confit de canard IGP du Sud-Ouest à l\'orange, frites et salade — 22&nbsp;€<br>Lasagnes végétariennes, ricotta et légumes du moment, salade de mâche — 18&nbsp;€<br>Assiette de frites fraîches, sauce au choix — 6&nbsp;€<i>Desserts</i>Fondant au chocolat, piment d\'Espelette et fleur de sel — 7&nbsp;€<br>Tarte tatin et sa crème fouettée — 7&nbsp;€</span>';
  window.carte9=function(txt){ return '<span class="menu9" tabindex="0">'+txt+CARTE+'</span>'; };
  document.addEventListener('click',function(e){
    var m=e.target.closest&&e.target.closest('.menu9');
    document.querySelectorAll('.menu9.on').forEach(function(x){ if(x!==m) x.classList.remove('on'); });
    if(m){ e.preventDefault(); e.stopPropagation(); m.classList.toggle('on'); }
  },true);
})();
