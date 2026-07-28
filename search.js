// Client-side post search for the Writing page. Fetches the static
// search-index.json (built by build.py) and filters posts as you type.
(function () {
  var input = document.getElementById("post-search");
  if (!input) return;
  var staticList = document.getElementById("posts");
  var results = document.getElementById("search-results");
  var empty = document.getElementById("search-empty");
  var index = [];

  fetch("/search-index.json")
    .then(function (r) { return r.json(); })
    .then(function (data) { index = data; render(input.value); })
    .catch(function () { /* search stays inert if the index can't load */ });

  function esc(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function render(q) {
    q = (q || "").trim().toLowerCase();
    if (!q) {
      staticList.hidden = false;
      results.hidden = true;
      results.innerHTML = "";
      empty.hidden = true;
      return;
    }
    var matches = index.filter(function (p) {
      return (p.title + " " + p.text).toLowerCase().indexOf(q) !== -1;
    });
    staticList.hidden = true;
    if (matches.length) {
      results.innerHTML = matches.map(function (p) {
        return '<li><time datetime="' + p.date + '">' + p.date + "</time>" +
               '<a href="' + p.url + '">' + esc(p.title) + "</a></li>";
      }).join("");
      results.hidden = false;
      empty.hidden = true;
    } else {
      results.hidden = true;
      results.innerHTML = "";
      empty.textContent = 'No posts match "' + q + '".';
      empty.hidden = false;
    }
  }

  input.addEventListener("input", function () { render(input.value); });
})();
