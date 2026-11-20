/* Centro guide: miglioramenti progressivi. Senza JavaScript restano indice, collegamenti, confronti (radio + CSS)
   e la ricerca porta all'indice con ?q= nell'indirizzo. */
(() => {
  const en = document.documentElement.lang === "en";
  const T = en
    ? { one: "chapter found for", many: "chapters found for", copied: "Copied", copy: "Copy the sentence" }
    : { one: "capitolo trovato per", many: "capitoli trovati per", copied: "Copiata", copy: "Copia la frase" };
  // Senza accenti, maiuscole e trattini: «unità» trova «unita», «kmeans» trova «K-means».
  const fold = text => text.normalize("NFD").replace(/\p{M}/gu, "").replace(/[-\u2010-\u2013]/g, "").toLocaleLowerCase(en ? "en" : "it");

  // Ricerca nell'indice: filtra i capitoli, ignora accenti e maiuscole, legge ?q= dall'indirizzo.
  const items = [...document.querySelectorAll(".ch[data-q]")];
  const input = document.querySelector(".search.big input");
  if (items.length && input) {
    const guides = [...document.querySelectorAll(".guide")];
    const empty = document.getElementById("vuoto");
    const result = document.getElementById("esito");
    const initial = result ? result.textContent : "";
    const apply = () => {
      const words = fold(input.value.trim()).split(/\s+/).filter(Boolean);
      let shown = 0;
      for (const li of items) {
        const hay = li.dataset.folded || (li.dataset.folded = fold(li.dataset.q));
        const hit = words.every(w => hay.includes(w));
        li.hidden = !hit;
        if (hit) shown += 1;
      }
      for (const g of guides) g.hidden = !g.querySelector(".ch:not([hidden])");
      document.body.classList.toggle("searching", words.length > 0);
      if (empty) {
        empty.hidden = shown > 0;
        empty.querySelector("[data-echo]").textContent = input.value.trim();
      }
      if (result) {
        result.textContent = words.length ? `${shown} ${shown === 1 ? T.one : T.many} ${en ? "“" : "«"}${input.value.trim()}${en ? "”" : "»"}` : initial;
      }
    };
    const params = new URLSearchParams(location.search);
    if (params.get("q")) input.value = params.get("q");
    input.addEventListener("input", apply);
    input.form.addEventListener("submit", e => {
      e.preventDefault();
      const url = new URL(location.href);
      if (input.value.trim()) url.searchParams.set("q", input.value.trim()); else url.searchParams.delete("q");
      history.replaceState(null, "", url);
      apply();
      const first = document.querySelector(".ch:not([hidden]) a");
      if (first) first.focus();
    });
    document.querySelectorAll("[data-clear]").forEach(b => b.addEventListener("click", () => {
      input.value = "";
      const url = new URL(location.href); url.searchParams.delete("q"); history.replaceState(null, "", url);
      apply(); input.focus();
    }));
    apply();
  }

  // Sezione corrente nell'indice del capitolo.
  const links = [...document.querySelectorAll(".toc a[href^='#']")];
  if (links.length && "IntersectionObserver" in window) {
    const byId = new Map(links.map(a => [a.getAttribute("href").slice(1), a]));
    const seen = new Map();
    const mark = () => {
      let current = null;
      for (const [id, top] of seen) if (top < window.innerHeight * 0.45 && (!current || top > seen.get(current))) current = id;
      if (!current) return;
      links.forEach(a => a.removeAttribute("aria-current"));
      byId.get(current).setAttribute("aria-current", "true");
    };
    const io = new IntersectionObserver(entries => {
      for (const e of entries) seen.set(e.target.id, e.boundingClientRect.top);
      mark();
    }, { rootMargin: "-80px 0px -40% 0px", threshold: [0, 1] });
    byId.forEach((_, id) => { const el = document.getElementById(id); if (el) io.observe(el); });
    window.addEventListener("scroll", () => {
      for (const id of seen.keys()) seen.set(id, document.getElementById(id).getBoundingClientRect().top);
      mark();
    }, { passive: true });
  }

  // Sul telefono i pannelli di navigazione partono chiusi.
  if (window.matchMedia("(max-width: 860px)").matches) {
    document.querySelectorAll("details.gnav, details.toc, details.proof").forEach(d => d.removeAttribute("open"));
  }

  // Annuncia la soluzione scelta nei confronti (il cambio di figura e riga è già fatto dal CSS).
  document.querySelectorAll(".kcmp").forEach(kcmp => {
    const live = document.createElement("p");
    live.className = "sr"; live.setAttribute("aria-live", "polite");
    kcmp.append(live);
    kcmp.addEventListener("change", e => {
      const row = kcmp.querySelector(`tr[data-k="${e.target.value}"]`);
      if (row) live.textContent = [...row.cells].map(c => c.textContent.trim()).join(" · ");
    });
  });

  // Copia della frase per i metodi.
  document.querySelectorAll("[data-copy]").forEach(button => {
    if (!navigator.clipboard) return;
    button.hidden = false;
    button.addEventListener("click", () => {
      navigator.clipboard.writeText(document.querySelector(button.dataset.copy).innerText.trim())
        .then(() => { button.textContent = T.copied; setTimeout(() => { button.textContent = T.copy; }, 1600); });
    });
  });
})();
