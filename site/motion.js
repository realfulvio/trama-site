/*
  Movimento delle pagine interne (Funzionalità, Novità). La home ha il suo home.js.
  Senza questo file, o con "riduci movimento", ogni pagina è completa e ferma.
  - .anim sulla radice accende ingressi e curve di sfondo (style.css);
  - .rv compare quando entra nello schermo;
  - i numeri di .count salgono da zero quando si vedono.
*/
(() => {
  const doc = document.documentElement;
  doc.classList.add("js");
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  doc.classList.add("anim");
  const items = [...document.querySelectorAll(".rv")];
  const nums = [...document.querySelectorAll(".count b")];
  if (!("IntersectionObserver" in window)) { items.forEach(e => e.classList.add("in")); return; }
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add("in"); io.unobserve(e.target);
  }), { rootMargin: "0px 0px -8% 0px" });
  items.forEach(e => io.observe(e));
  // rete di sicurezza: dopo 4 s tutto è visibile anche se l'osservatore non è scattato
  setTimeout(() => items.forEach(e => e.classList.add("in")), 4000);
  const up = b => {
    const n = parseInt(b.textContent, 10); if (!(n > 1)) return;
    const t0 = performance.now(), tick = t => { const k = Math.min(1, (t - t0) / 1200), e = 1 - Math.pow(1 - k, 3); b.textContent = String(Math.round(n * e)); if (k < 1) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
  };
  const nio = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { nio.unobserve(e.target); up(e.target); } }), { threshold: .6 });
  nums.forEach(b => nio.observe(b));
})();
