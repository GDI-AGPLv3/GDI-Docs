// Abre los links externos en pestaña nueva.
// document$ es el observable de Material (compatible con navigation.instant).
document$.subscribe(function () {
  document.querySelectorAll("a[href^='http']").forEach(function (link) {
    if (link.hostname !== window.location.hostname) {
      link.target = "_blank";
      link.rel = "noopener";
    }
  });
});
