/*
  Home di Trama: movimento facoltativo. Senza questo file la pagina è completa e ferma.
  - testata: due curve dose-risposta a quattro parametri che convergono sui punti. Le forme
    intermedie sono le iterazioni reali di un Levenberg-Marquardt su questi dati sintetici;
  - "Guarda come si lavora": quattro schermate in sequenza, con pausa;
  - comparsa allo scorrimento e numeri che contano.
  Con "riduci movimento" del sistema mostra subito lo stato finale.
*/
(() => {
  const FIT = {"x":[0.01,0.022,0.047,0.103,0.225,0.49,1.067,2.324,5.06,11.02,24.0],"c":{"y":[5,6.3,12.8,16.9,25.7,47.4,68,80.2,89.2,93.8,92.4],"path":[[5.0,93.8,-1.2,0.6],[2.688145,107.829292,0.158909,0.404188],[-0.077737,90.834567,-0.670571,0.718391],[13.747588,97.933822,0.022196,0.976481],[4.54629,92.645656,-0.346634,1.101003],[5.702199,94.904738,-0.248277,1.183686],[5.646705,94.563947,-0.258328,1.214455],[5.66763,94.567073,-0.257823,1.216475],[5.669716,94.565211,-0.257816,1.216667],[5.669894,94.565072,-0.257815,1.216682],[5.669909,94.565061,-0.257815,1.216683],[5.66991,94.56506,-0.257815,1.216683],[5.66991,94.56506,-0.257815,1.216683]],"r2":0.998196},"t":{"y":[1.5,6.4,4.9,6.8,8.8,17.7,34,52.4,67.2,77.4,79.4],"path":[[1.5,79.4,-1.2,0.6],[-20.899449,82.523133,-0.352087,0.115906],[-24.044892,89.63603,-0.131839,0.426939],[6.416559,102.07859,0.674256,0.605681],[1.395858,91.658041,0.230664,0.818434],[5.346192,80.231616,0.188671,1.163811],[3.91465,82.11597,0.199715,1.290934],[3.815513,82.215127,0.198654,1.288518],[3.815524,82.214856,0.198652,1.288558],[3.815522,82.214857,0.198652,1.288557],[3.815522,82.214857,0.198652,1.288557]],"r2":0.998438}};
  const doc = document.documentElement, lang = doc.lang.startsWith("it") ? "it" : "en";
  const T = {
    it: { wait: "in attesa", arrive: "Punti in arrivo…", run: "Il fit sta convergendo…", done: "Convergenza raggiunta, dati sintetici", slope: "pendenza", iter: "iter.", step: "Passo", of: "di", pause: "Pausa", play: "Riproduci" },
    en: { wait: "waiting", arrive: "Plotting the points…", run: "The fit is converging…", done: "Converged, synthetic data", slope: "slope", iter: "iter.", step: "Step", of: "of", pause: "Pause", play: "Play" }
  }[lang];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
  if (!reduce) doc.classList.add("anim");

  /* ---- fit in testata ---- */
  const svg = $("#fit-svg");
  if (svg) {
    const W = 520, H = 300, L = 46, R = 12, TOP = 12, B = 40, lx0 = -2.2, lx1 = 1.6;
    const X = lx => L + (lx - lx0) / (lx1 - lx0) * (W - L - R), Y = y => TOP + (1 - y / 100) * (H - TOP - B);
    const f4 = (p, lx) => p[0] + (p[1] - p[0]) / (1 + Math.pow(10, (p[2] - lx) * p[3]));
    const curve = p => { let d = ""; for (let i = 0; i <= 80; i++) { const lx = lx0 + (lx1 - lx0) * i / 80; d += (i ? "L" : "M") + X(lx).toFixed(1) + " " + Y(f4(p, lx)).toFixed(1); } return d; };
    const num = (v, d) => lang === "it" ? v.toFixed(d).replace(".", ",") : v.toFixed(d);
    const show = (k, p, it, done) => {
      $("#cv-" + k).setAttribute("d", curve(p));
      $("#ro-" + k).textContent = "EC50 " + num(Math.pow(10, p[2]), 4) + " µM · " + T.slope + " " + num(p[3], 4) + (done ? " · R² " + num(FIT[k].r2, 4) : " · " + T.iter + " " + it);
    };
    const pts = $$("#fit-svg .pt");
    let run = 0;
    const play = () => {
      const me = ++run;
      if (reduce) { for (const k of ["c", "t"]) show(k, FIT[k].path.at(-1), 0, true); $("#fit-state").textContent = T.done; return; }
      $("#fit-state").textContent = T.arrive;
      pts.forEach((c, i) => { c.style.opacity = 0; setTimeout(() => { if (me === run) c.style.opacity = 1; }, 40 * i); });
      for (const k of ["c", "t"]) { $("#cv-" + k).setAttribute("d", ""); $("#ro-" + k).textContent = T.wait; }
      const start = performance.now() + 40 * pts.length + 250, per = 260;
      const tick = t => {
        if (me !== run) return;
        if (t < start) return requestAnimationFrame(tick);
        let all = true;
        for (const k of ["c", "t"]) {
          const P = FIT[k].path, u = Math.min(P.length - 1, (t - start) / per), i = Math.floor(u), fr = u - i;
          const a = P[i], b = P[Math.min(i + 1, P.length - 1)], e = fr * fr * (3 - 2 * fr), done = u >= P.length - 1;
          show(k, a.map((v, j) => v + (b[j] - v) * e), Math.min(i + 1, P.length - 1), done);
          all = all && done;
        }
        $("#fit-state").textContent = all ? T.done : T.run;
        if (!all) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    $("#fit-replay").hidden = false;
    $("#fit-replay").addEventListener("click", play);
    play();
  }

  /* ---- dimostrazione in quattro passi ---- */
  const stage = $("#stage");
  if (stage) {
    const imgs = $$("#stage img"), btns = $$("#steps button"), toggle = $("#demo-toggle"), count = $("#demo-count");
    let cur = 0, playing = !reduce, timer;
    const go = i => {
      cur = (i + imgs.length) % imgs.length;
      imgs.forEach((im, j) => { im.classList.remove("zoom"); im.classList.toggle("on", j === cur); if (j === cur && playing) { void im.offsetWidth; im.classList.add("zoom"); } });
      btns.forEach((b, j) => {
        j === cur ? b.setAttribute("aria-current", "step") : b.removeAttribute("aria-current");
        const p = b.querySelector(".prog"); p.classList.remove("run"); if (j === cur && playing) { void p.offsetWidth; p.classList.add("run"); }
      });
      count.textContent = T.step + " " + (cur + 1) + " " + T.of + " " + imgs.length + ": " + btns[cur].querySelector("span").textContent;
      clearTimeout(timer);
      if (playing) timer = setTimeout(() => go(cur + 1), 5200);
    };
    btns.forEach((b, j) => b.addEventListener("click", () => go(j)));
    toggle.hidden = false;
    toggle.textContent = playing ? T.pause : T.play;
    toggle.addEventListener("click", () => { playing = !playing; toggle.textContent = playing ? T.pause : T.play; go(cur); });
    // la sequenza parte quando la finestra è visibile e si ferma quando esce dallo schermo
    if ("IntersectionObserver" in window && playing) {
      let seen = false;
      new IntersectionObserver(es => es.forEach(e => {
        if (e.isIntersecting && !seen) { seen = true; go(cur); }
        else if (!e.isIntersecting && seen && playing) { clearTimeout(timer); seen = false; }
      }), { threshold: .35 }).observe(stage);
    } else go(0);
    btns.forEach(b => b.removeAttribute("disabled"));
  }

  /* ---- comparsa allo scorrimento e numeri ---- */
  const nums = $("#nums");
  const countUp = () => {
    if (reduce) return;
    $$("#nums b[data-n]").forEach(b => {
      const n = +b.dataset.n; if (!n) return;
      const t0 = performance.now(), tick = t => { const k = Math.min(1, (t - t0) / 1100), e = 1 - Math.pow(1 - k, 3); b.textContent = String(Math.round(n * e)); if (k < 1) requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    });
  };
  const items = $$(".rv, .kit article");
  if (reduce || !("IntersectionObserver" in window)) { items.forEach(e => e.classList.add("in")); return; }
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add("in"); io.unobserve(e.target);
    if (e.target === nums) countUp();
  }), { rootMargin: "0px 0px -8% 0px" });
  items.forEach(e => io.observe(e));
  // rete di sicurezza: dopo 4 s tutto è visibile anche se l'osservatore non è scattato
  setTimeout(() => items.forEach(e => e.classList.add("in")), 4000);
})();
