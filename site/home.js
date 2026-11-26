/*
  Home di Trama: movimento facoltativo. Senza questo file la pagina è completa e ferma.
  - testata: due curve dose-risposta a quattro parametri che convergono sui punti. Le forme
    intermedie sono le iterazioni reali di un Levenberg-Marquardt su questi dati sintetici;
  - testata: il programma al lavoro, quattro schermate intere in dissolvenza, con pausa; un clic
    le apre a grandezza piena in un visore. Più sotto una seconda finestra, a schede;
  - comparsa allo scorrimento e numeri che contano.
  Con "riduci movimento" del sistema mostra subito lo stato finale.
*/
(() => {
  const FIT = {"x":[0.01,0.022,0.047,0.103,0.225,0.49,1.067,2.324,5.06,11.02,24.0],"c":{"y":[5,6.3,12.8,16.9,25.7,47.4,68,80.2,89.2,93.8,92.4],"path":[[5.0,93.8,-1.2,0.6],[2.688145,107.829292,0.158909,0.404188],[-0.077737,90.834567,-0.670571,0.718391],[13.747588,97.933822,0.022196,0.976481],[4.54629,92.645656,-0.346634,1.101003],[5.702199,94.904738,-0.248277,1.183686],[5.646705,94.563947,-0.258328,1.214455],[5.66763,94.567073,-0.257823,1.216475],[5.669716,94.565211,-0.257816,1.216667],[5.669894,94.565072,-0.257815,1.216682],[5.669909,94.565061,-0.257815,1.216683],[5.66991,94.56506,-0.257815,1.216683],[5.66991,94.56506,-0.257815,1.216683]],"r2":0.998196},"t":{"y":[1.5,6.4,4.9,6.8,8.8,17.7,34,52.4,67.2,77.4,79.4],"path":[[1.5,79.4,-1.2,0.6],[-20.899449,82.523133,-0.352087,0.115906],[-24.044892,89.63603,-0.131839,0.426939],[6.416559,102.07859,0.674256,0.605681],[1.395858,91.658041,0.230664,0.818434],[5.346192,80.231616,0.188671,1.163811],[3.91465,82.11597,0.199715,1.290934],[3.815513,82.215127,0.198654,1.288518],[3.815524,82.214856,0.198652,1.288558],[3.815522,82.214857,0.198652,1.288557],[3.815522,82.214857,0.198652,1.288557]],"r2":0.998438}};
  const doc = document.documentElement, lang = doc.lang.startsWith("it") ? "it" : "en";
  const T = {
    it: { wait: "in attesa", arrive: "Punti in arrivo…", run: "Il fit sta convergendo…", done: "Convergenza raggiunta, dati sintetici", slope: "pendenza", iter: "iter.", step: "Passo", of: "di", pause: "Pausa", play: "Riproduci", prev: "Schermata precedente", next: "Schermata successiva", close: "Chiudi" },
    en: { wait: "waiting", arrive: "Plotting the points…", run: "The fit is converging…", done: "Converged, synthetic data", slope: "slope", iter: "iter.", step: "Step", of: "of", pause: "Pause", play: "Play", prev: "Previous screenshot", next: "Next screenshot", close: "Close" }
  }[lang];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
  doc.classList.add("js");
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
    // parte quando il grafico entra nello schermo, così chi scorre lo vede dall'inizio
    if (!reduce && "IntersectionObserver" in window) {
      const once = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { once.disconnect(); play(); } }, { threshold: .4 });
      once.observe(svg);
    } else play();
  }

  /* ---- finestre con le schermate: la prima scorre da sola, le altre a mano ---- */
  const stoppers = [];
  const pauseDemo = () => stoppers.forEach(f => f());
  $$(".demo").forEach(demo => {
    const q = sel => [...demo.querySelectorAll(sel)];
    const stage = demo.querySelector(".stage"), shots = q(".shot"), btns = q(".steps button");
    const toggle = demo.querySelector(".demo-toggle"), count = demo.querySelector(".demo-count");
    const auto = demo.hasAttribute("data-auto"), HOLD = 6000;
    let cur = 0, playing = auto && !reduce, timer;
    const go = i => {
      cur = (i + shots.length) % shots.length;
      shots.forEach((a, j) => { a.classList.toggle("on", j === cur); a.tabIndex = j === cur ? 0 : -1; });
      btns.forEach((b, j) => {
        j === cur ? b.setAttribute("aria-current", "step") : b.removeAttribute("aria-current");
        const p = b.querySelector(".prog"); p.classList.remove("run"); if (j === cur && playing) { void p.offsetWidth; p.classList.add("run"); }
      });
      count.textContent = T.step + " " + (cur + 1) + " " + T.of + " " + shots.length;
      clearTimeout(timer);
      if (playing) timer = setTimeout(() => go(cur + 1), HOLD);
    };
    const setPlaying = on => { playing = on; toggle.textContent = playing ? T.pause : T.play; go(cur); };
    stoppers.push(() => { if (playing) setPlaying(false); });
    // scegliere un passo a mano ferma la sequenza: chi guarda decide il ritmo
    btns.forEach((b, j) => b.addEventListener("click", () => { playing = false; toggle.textContent = T.play; go(j); }));
    if (auto) {
      toggle.hidden = false;
      toggle.textContent = playing ? T.pause : T.play;
      toggle.addEventListener("click", () => setPlaying(!playing));
    }
    go(0); clearTimeout(timer);
    // la sequenza scorre solo mentre la finestra è sullo schermo
    if (playing && "IntersectionObserver" in window) {
      let seen = false;
      new IntersectionObserver(es => es.forEach(e => {
        if (e.isIntersecting && !seen) { seen = true; if (playing) go(cur); }
        else if (!e.isIntersecting && seen) { clearTimeout(timer); seen = false; }
      }), { threshold: .35 }).observe(stage);
    } else if (playing) go(0);
  });

  /* ---- visore: un clic su una schermata la apre a grandezza piena ---- */
  const zooms = $$(".stage .shot");
  if (zooms.length && "HTMLDialogElement" in window) {
    const dlg = document.createElement("dialog");
    dlg.className = "lb";
    dlg.innerHTML = '<div class="lb-in"><div class="lb-top"><p></p><button type="button" data-d="-1" aria-label="' + T.prev + '">‹</button><button type="button" data-d="1" aria-label="' + T.next + '">›</button><button type="button" data-d="0" aria-label="' + T.close + '">×</button></div><div class="lb-scroll"><img alt="" width="1320" height="810"></div></div>';
    document.body.append(dlg);
    const img = dlg.querySelector("img"), cap = dlg.querySelector("p"), box = dlg.querySelector(".lb-scroll");
    let at = 0;
    const fit = () => dlg.classList.toggle("can-zoom", box.clientWidth < 1300);
    const open = i => {
      at = (i + zooms.length) % zooms.length;
      const src = zooms[at].querySelector("img");
      img.src = zooms[at].href; img.alt = src.alt; cap.textContent = src.alt;
      dlg.classList.remove("full"); box.scrollTo(0, 0);
      if (!dlg.open) dlg.showModal();
      fit();
    };
    zooms.forEach((a, i) => a.addEventListener("click", e => {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
      e.preventDefault(); pauseDemo(); open(i);
    }));
    dlg.addEventListener("click", e => {
      const b = e.target.closest("button");
      if (b) return +b.dataset.d ? open(at + +b.dataset.d) : dlg.close();
      if (e.target === img) { if (dlg.classList.contains("can-zoom") || dlg.classList.contains("full")) dlg.classList.toggle("full"); return; }
      if (!e.target.closest(".lb-top")) dlg.close();
    });
    dlg.addEventListener("keydown", e => { if (e.key === "ArrowLeft") open(at - 1); else if (e.key === "ArrowRight") open(at + 1); });
    addEventListener("resize", () => { if (dlg.open) fit(); });
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
