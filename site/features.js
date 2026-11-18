/* Mappa delle funzionalità: costruisce la griglia dagli elenchi statici della pagina (senza JS restano gli elenchi). */
(() => {
  const S = JSON.parse(document.getElementById("f-i18n").textContent);
  const root = document.documentElement;
  root.classList.add("js");
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const map = document.getElementById("fmap"), rows = document.getElementById("mrows"), card = document.getElementById("card");
  const fams = [...document.querySelectorAll(".fam")].map(f => ({
    id: f.dataset.id, icon: f.querySelector(".fam-ico").innerHTML, title: f.querySelector("h3").textContent,
    items: [...f.querySelectorAll("li")].map(li => ({ t: li.textContent, s: li.dataset.s }))
  }));
  const counts = { ok: 0, plan: 0 };
  for (const family of fams) {
    for (const item of family.items) counts[item.s] += 1;
  }
  for (const counter of document.querySelectorAll("[data-feature-count]")) {
    counter.textContent = counts[counter.dataset.featureCount];
  }
  let k = 0;
  rows.innerHTML = fams.map(f => {
    const ok = f.items.filter(i => i.s === "ok").length, plan = f.items.length - ok;
    const cells = f.items.map((it, i) => `<button class="cell${it.s === "plan" ? " plan" : ""}" type="button" style="animation-delay:${(k++) * 6}ms" data-f="${f.id}" data-i="${i}" aria-label="${esc(it.t)}, ${it.s === "ok" ? S.ok : S.plan}"></button>`).join("");
    return `<div class="mrow" data-f="${f.id}"><button class="mrow-l" type="button" aria-pressed="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${f.icon}</svg>${esc(f.title)}</button><div class="cells">${cells}</div><span class="mrow-n">${ok} <i>+${plan}</i></span></div>`;
  }).join("");
  const fam = id => fams.find(f => f.id === id);
  const intro = () => { card.innerHTML = `<span class="k">${esc(S.howK)}</span><h3>${esc(S.howT)}</h3><p>${esc(S.howP)}</p>`; };
  intro();
  const clearCur = () => document.querySelectorAll(".cell.cur, .flow li.cur").forEach(x => x.classList.remove("cur"));
  function cellCard(c) {
    clearCur(); c.classList.add("cur");
    const f = fam(c.dataset.f), it = f.items[c.dataset.i];
    card.innerHTML = `<span class="k">${esc(f.title)}</span><h3>${esc(it.t)}</h3><span class="ftag ${it.s}">${it.s === "ok" ? S.ok : S.plan}</span>`;
    document.querySelectorAll(".links path.on").forEach(p => p.classList.remove("on"));
  }
  rows.addEventListener("mouseover", e => { const c = e.target.closest(".cell"); if (c) cellCard(c); });
  rows.addEventListener("focusin", e => { const c = e.target.closest(".cell"); if (c) cellCard(c); });
  rows.addEventListener("click", e => {
    const c = e.target.closest(".cell"); if (c) return cellCard(c);
    const l = e.target.closest(".mrow-l"); if (!l) return;
    const row = l.closest(".mrow"), on = l.getAttribute("aria-pressed") !== "true";
    rows.querySelectorAll(".mrow").forEach(r => { r.classList.toggle("sel", on && r === row); r.querySelector(".mrow-l").setAttribute("aria-pressed", on && r === row); });
    map.classList.toggle("dim", on);
    if (!on) return intro();
    const f = fam(row.dataset.f);
    card.innerHTML = `<span class="k">${esc(S.family)}</span><h3>${esc(f.title)}</h3><p>${esc(S.count.replace("{ok}", f.items.filter(i => i.s === "ok").length).replace("{plan}", f.items.filter(i => i.s === "plan").length))}</p><ul>${f.items.map(i => `<li${i.s === "plan" ? ' class="plan"' : ""}>${esc(i.t)}${i.s === "plan" ? " (" + esc(S.plan.toLowerCase()) + ")" : ""}</li>`).join("")}</ul>`;
  });
  document.querySelectorAll(".seg button").forEach(b => b.addEventListener("click", () => {
    document.querySelectorAll(".seg button").forEach(x => x.setAttribute("aria-pressed", x === b));
    map.classList.remove("mode-ok", "mode-plan"); if (b.dataset.m !== "all") map.classList.add("mode-" + b.dataset.m);
  }));

  // formati
  const flow = document.getElementById("flow"), links = document.getElementById("links");
  flow.querySelectorAll("li:not(.plan)").forEach(li => {
    const b = li.querySelector("b"), n = li.querySelector("span");
    const btn = document.createElement("button"); btn.type = "button"; btn.className = "fbtn";
    btn.append(n, b); li.prepend(btn);
  });
  function draw() {
    const hub = flow.querySelector(".hub img"); if (!hub || getComputedStyle(hub.parentElement).display === "none") { links.innerHTML = ""; return; }
    const r = flow.getBoundingClientRect(), h = hub.getBoundingClientRect(), hx = h.left - r.left + h.width / 2, hy = h.top - r.top + h.height / 2;
    links.innerHTML = [...flow.querySelectorAll("li")].map(li => {
      const q = li.getBoundingClientRect(), left = li.closest("ul").id === "fin", y = q.top - r.top + q.height / 2, x = left ? q.right - r.left : q.left - r.left, mid = (x + hx) / 2;
      return `<path data-id="${li.dataset.id || ""}" class="${li.classList.contains("plan") ? "plan" : ""}" d="M${x},${y} C${mid},${y} ${mid},${hy} ${hx},${hy}"/>`;
    }).join("");
  }
  flow.addEventListener("click", e => {
    const li = e.target.closest("li[data-id]"); if (!li) return;
    clearCur(); li.classList.add("cur");
    links.querySelectorAll("path").forEach(p => p.classList.toggle("on", p.dataset.id === li.dataset.id));
    card.innerHTML = `<span class="k">${esc(S.fmtK)} · ${esc(S.dir[li.dataset.dir])}</span><h3>${esc(li.querySelector("b").textContent)}</h3><p>${esc(li.querySelector("span").textContent)}. ${esc(li.querySelector("small").textContent)}</p>`;
    if (matchMedia("(max-width: 960px)").matches) card.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "nearest" });
  });
  addEventListener("resize", draw);
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(draw); draw();
})();
