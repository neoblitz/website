// Writing page: filter the post list by free-text search and by the sidebar's
// Tags / Archive facets. Posts carry data-tags and data-month attributes; the
// search index (search-index.json) supplies the full text for search.
(function () {
  var input = document.getElementById("post-search");
  var list = document.getElementById("posts");
  if (!input || !list) return;
  var empty = document.getElementById("search-empty");
  var note = document.getElementById("filter-note");
  var items = Array.prototype.slice.call(list.querySelectorAll("li"));
  var hay = {};   // url -> lowercased searchable text
  var facet = null;   // {type:'tag'|'month', value, label}

  fetch("/search-index.json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      data.forEach(function (p) {
        hay[p.url] = (p.title + " " + p.text).toLowerCase();
      });
      apply();
    })
    .catch(function () {});

  function apply() {
    var q = (input.value || "").trim().toLowerCase();
    var visible = 0;
    items.forEach(function (li) {
      var ok = true;
      if (facet) {
        ok = facet.type === "tag"
          ? (li.getAttribute("data-tags") || "").split(" ").indexOf(facet.value) !== -1
          : li.getAttribute("data-month") === facet.value;
      }
      if (ok && q) {
        var a = li.querySelector("a");
        var text = hay[a && a.getAttribute("href")] || li.textContent.toLowerCase();
        ok = text.indexOf(q) !== -1;
      }
      li.hidden = !ok;
      if (ok) visible++;
    });
    if (empty) {
      empty.hidden = visible !== 0;
      empty.textContent = "No posts found.";
    }
    updateNote();
    updateActive();
  }

  function updateNote() {
    if (!note) return;
    if (!facet) { note.hidden = true; note.innerHTML = ""; return; }
    var what = facet.type === "tag"
      ? "tagged “" + facet.label + "”"
      : "from " + facet.label;
    note.innerHTML = "Showing posts " + what +
      ' · <a href="#" class="clear-filter">show all</a>';
    note.hidden = false;
    note.querySelector(".clear-filter").addEventListener("click", function (e) {
      e.preventDefault();
      setFacet(null);
    });
  }

  function updateActive() {
    document.querySelectorAll(".facet-list a").forEach(function (a) {
      var on = facet && (
        (facet.type === "tag" && a.getAttribute("data-tag") === facet.value) ||
        (facet.type === "month" && a.getAttribute("data-month") === facet.value));
      a.classList.toggle("is-active", !!on);
    });
  }

  function setFacet(f) {
    facet = f;
    try {
      var url = new URL(window.location);
      url.searchParams.delete("tag");
      url.searchParams.delete("month");
      if (f) url.searchParams.set(f.type, f.value);
      history.replaceState(null, "", url.pathname + url.search);
    } catch (e) {}
    apply();
  }

  document.querySelectorAll(".facet-list a").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      var type = a.hasAttribute("data-tag") ? "tag" : "month";
      var value = a.getAttribute("data-" + type);
      if (facet && facet.type === type && facet.value === value) {
        setFacet(null);                       // click the active facet to clear
      } else {
        setFacet({ type: type, value: value, label: a.getAttribute("data-label") });
      }
    });
  });

  input.addEventListener("input", apply);

  // Apply a facet from the URL (?tag=… or ?month=…) so links are shareable.
  try {
    var p = new URLSearchParams(window.location.search);
    var t = p.get("tag"), m = p.get("month");
    var sel = t ? '.facet-list a[data-tag="' + t + '"]'
                : m ? '.facet-list a[data-month="' + m + '"]' : null;
    if (sel) {
      var a = document.querySelector(sel);
      if (t) facet = { type: "tag", value: t, label: a ? a.getAttribute("data-label") : t };
      else if (m) facet = { type: "month", value: m, label: a ? a.getAttribute("data-label") : m };
    }
  } catch (e) {}

  apply();
})();
