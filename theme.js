// Light/dark theme toggle. The early inline <head> script applies any saved
// choice before paint; this wires up the header button and keeps its icon in
// sync. With no saved choice, the site follows the system preference.
(function () {
  var root = document.documentElement;
  var KEY = "theme";

  function systemDark() {
    return window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function effective() {
    return root.getAttribute("data-theme") || (systemDark() ? "dark" : "light");
  }

  var btn = document.querySelector(".theme-toggle");
  if (!btn) return;

  function sync() {
    var dark = effective() === "dark";
    btn.classList.toggle("is-dark", dark);
    btn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    btn.setAttribute("aria-pressed", String(dark));
  }

  btn.addEventListener("click", function () {
    var next = effective() === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem(KEY, next); } catch (e) {}
    sync();
  });

  // If the visitor hasn't chosen a theme, follow live system changes.
  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
      if (!root.getAttribute("data-theme")) sync();
    });
  }

  sync();
})();
