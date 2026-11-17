(function(){
  var btn=document.querySelector('.menu-btn'),nav=document.getElementById('nav');
  if(btn&&nav){btn.addEventListener('click',function(){var o=nav.classList.toggle('open');btn.setAttribute('aria-expanded',o)});
    nav.addEventListener('click',function(e){if(e.target.tagName==='A'){nav.classList.remove('open');btn.setAttribute('aria-expanded','false')}})}
  // tabs filter
  var tabs=document.querySelectorAll('[data-filter]');
  function apply(f){tabs.forEach(function(t){t.setAttribute('aria-selected',t.dataset.filter===f)});
    document.querySelectorAll('.card[data-aud]').forEach(function(c){var a=c.dataset.aud;c.hidden=!(f==='all'||a===f||a==='both')})}
  tabs.forEach(function(t){t.addEventListener('click',function(){apply(t.dataset.filter)})});
  document.querySelectorAll('[data-go]').forEach(function(a){a.addEventListener('click',function(){apply(a.dataset.go)})});
  // reveal
  if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px'});
    document.querySelectorAll('.rv').forEach(function(el){io.observe(el)})}else{document.querySelectorAll('.rv').forEach(function(el){el.classList.add('in')})}
  // lazy social embeds
  var lz=document.querySelectorAll('iframe[data-src]');
  if('IntersectionObserver' in window){var io2=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.src=e.target.dataset.src;io2.unobserve(e.target)}})},{rootMargin:'300px'});lz.forEach(function(f){io2.observe(f)})}else{lz.forEach(function(f){f.src=f.dataset.src})}
  // video: pause when reduced motion
  var v=document.querySelector('.hero video');
  if(v&&window.matchMedia('(prefers-reduced-motion: reduce)').matches){v.removeAttribute('autoplay');v.pause()}
  // contact form -> whatsapp
  var f=document.getElementById('lead');
  if(f){f.addEventListener('submit',function(e){e.preventDefault();var d=new FormData(f);
    var t='היי ברוך, שמי '+(d.get('name')||'')+'.\n'+'מתעניין/ת ב: '+(d.get('what')||'')+'\n'+(d.get('when')?'תאריך/מקום: '+d.get('when')+'\n':'')+(d.get('msg')||'');
    window.open('https://wa.me/972528508677?text='+encodeURIComponent(t),'_blank','noopener')})}
  var y=document.getElementById('yr');if(y)y.textContent=new Date().getFullYear();
})();
