(function () {
  var saved = localStorage.getItem("showcase-lang") || "zh";
  applyLang(saved);
})();

function toggleLang() {
  var cur = document.documentElement.getAttribute("lang");
  applyLang(cur === "en" ? "zh" : "en");
}

function applyLang(lang) {
  var root = document.documentElement;
  var button = document.getElementById("lang-toggle");
  var english = lang === "en";
  root.setAttribute("lang", english ? "en" : "zh-TW");
  if (button) button.textContent = english ? "繁體中文" : "English";
  document.querySelectorAll(".lang-en").forEach(function (element) {
    element.hidden = !english;
  });
  document.querySelectorAll(".lang-zh").forEach(function (element) {
    element.hidden = english;
  });
  localStorage.setItem("showcase-lang", english ? "en" : "zh");
}

function printShowcase() {
  window.print();
}
