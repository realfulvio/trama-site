/* Enhance the verified static download; published beta releases are eligible. */
(() => {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);
  const safeURL = (value, host) => {
    try { const url = new URL(value); return url.protocol === "https:" && url.hostname === host && url.pathname.startsWith("/realfulvio/Trama/"); }
    catch { return false; }
  };
  fetch("https://api.github.com/repos/realfulvio/Trama/releases?per_page=30", {
    signal: controller.signal, credentials: "omit", referrerPolicy: "no-referrer",
    headers: { Accept: "application/vnd.github+json" }
  }).then(response => { if (!response.ok) throw new Error("Release lookup unavailable"); return response.json(); })
    .then(releases => {
      if (!Array.isArray(releases)) return;
      const published = releases.filter(release => !release.draft &&
        /^v?\d+\.\d+\.\d+(?:[-+][a-zA-Z0-9.-]+)?$/.test(release.tag_name || "") &&
        Number.isFinite(Date.parse(release.published_at)) && safeURL(release.html_url, "github.com"))
        .sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at));
      for (const release of published) {
        const version = release.tag_name.replace(/^v/, "");
        const asset = (Array.isArray(release.assets) ? release.assets : []).find(item =>
          item.name === `Trama-${version}-Windows-x64.zip` && safeURL(item.browser_download_url, "github.com"));
        if (!asset) continue;
        document.querySelectorAll("[data-release-version]").forEach(node => { node.textContent = `${release.prerelease ? "Beta " : ""}${version}`; });
        document.querySelectorAll("[data-release-download]").forEach(node => { node.href = asset.browser_download_url; });
        document.querySelectorAll("[data-release-page]").forEach(node => { node.href = release.html_url; node.textContent = `${document.documentElement.lang.startsWith("it") ? "Novità" : "What\'s new in"} ${version}`; });
        break;
      }
    }).catch(() => { /* Keep the working static version and links on network/rate-limit errors. */ })
    .finally(() => clearTimeout(timer));
})();
