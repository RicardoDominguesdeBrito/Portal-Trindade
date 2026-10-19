(() => {'use strict';
const p=new URLSearchParams(location.search),category=p.get('categoria'),q=p.get('q');
const topics=['historia','gastronomia','fe','turismo','cultura'];
if(location.hash==='#roteiros')return;
if(q||topics.includes(category)){const next=new URLSearchParams();if(q)next.set('q',q);if(topics.includes(category))next.set('tipo',category);location.replace('/lugares.html?'+next);}
})();
