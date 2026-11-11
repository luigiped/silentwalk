/* Silent Walk · FreeSpace APS
 * Solo <audio> nativo (niente Web Audio API, niente Wake Lock):
 * così l'ascolto continua a schermo bloccato su iOS e Android.
 */
(function () {
  "use strict";

  var EVENT_END = "2026-11-21T00:00:00+01:00";
  var SKIP = 15;

  var $ = function (id) { return document.getElementById(id); };
  var a = $("a");
  var playBtn = $("play");
  var seek = $("seek");
  var cur = $("cur");
  var dur = $("dur");
  var statusEl = $("status");
  var errEl = $("err");
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var expired = false;
  try { expired = Date.now() >= new Date(EVENT_END).getTime(); } catch (e) {}

  /* ---------------- Sequenza di avvio ---------------- */
  var landingShown = false;
  function show(id) {
    var screens = document.querySelectorAll(".screen");
    for (var i = 0; i < screens.length; i++) screens[i].classList.toggle("is-active", screens[i].id === id);
  }
  function showLanding() {
    if (landingShown) return;
    landingShown = true;
    show("s-landing");
    window.scrollTo(0, 0);
  }
  try {
    var tLoader = reduced ? 1500 : 4100;
    var tLogo = reduced ? 1500 : 2600;
    setTimeout(function () {
      if (landingShown) return;
      show("s-logo");
      setTimeout(showLanding, tLogo);
    }, tLoader);
  } catch (e) { showLanding(); }
  // rete di sicurezza: la landing compare comunque
  setTimeout(showLanding, 9000);

  /* ---------------- Browser integrati nelle app ---------------- */
  try {
    var ua = navigator.userAgent || "";
    if (/FBAN|FBAV|FB_IAB|Instagram|Snapchat|TikTok|musical_ly|Line\/|MicroMessenger|; wv\)/i.test(ua)) {
      $("inapp").hidden = false;
      document.body.classList.add("has-inapp");
    }
  } catch (e) {}
  $("copy").addEventListener("click", function () {
    var url = location.origin + location.pathname;
    var btn = this;
    function ok() { btn.textContent = "Copiato!"; setTimeout(function () { btn.textContent = "Copia link"; }, 2500); }
    function fallback() {
      var t = document.createElement("textarea");
      t.value = url; t.setAttribute("readonly", ""); t.style.position = "fixed"; t.style.opacity = "0";
      document.body.appendChild(t); t.select(); t.setSelectionRange(0, url.length);
      try { document.execCommand("copy"); ok(); } catch (e) { window.prompt("Copia questo link:", url); }
      document.body.removeChild(t);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(ok, fallback);
    else fallback();
  });

  /* ---------------- Scadenza soft ---------------- */
  if (expired) {
    $("live").hidden = true;
    $("expired").hidden = false;
    return; // l'audio non viene caricato
  }

  /* ---------------- Audio ---------------- */
  var SRC = a.getAttribute("data-src");
  a.src = SRC; // preload="metadata": la durata è nota prima del play

  // iOS 17+: categoria "playback" (ignora l'interruttore silenzioso, continua in background)
  try { if (navigator.audioSession) navigator.audioSession.type = "playback"; } catch (e) {}

  var lastTime = 0;
  var dragging = false;
  var pendingSeek = null;
  var waitTimer = null;
  var retries = 0;

  function fmt(s) {
    if (!isFinite(s) || s < 0) return "--:--";
    s = Math.floor(s);
    var m = Math.floor(s / 60), r = s % 60;
    return m + ":" + (r < 10 ? "0" : "") + r;
  }
  function duration() { return isFinite(a.duration) && a.duration > 0 ? a.duration : 0; }

  function paint(t) {
    var d = duration();
    if (!dragging) seek.value = Math.floor(t);
    var p = d ? Math.min(100, (t / d) * 100) : 0;
    seek.style.setProperty("--p", p + "%");
    cur.textContent = fmt(t);
  }
  function onMeta() {
    var d = duration();
    if (!d) return;
    seek.max = Math.floor(d);
    seek.disabled = false;
    dur.textContent = fmt(d);
    if (pendingSeek !== null) {
      try { a.currentTime = Math.min(pendingSeek, d - 1); } catch (e) {}
      pendingSeek = null;
    }
    paint(a.currentTime || 0);
    updatePosition();
  }
  function setPlayingUI(on) {
    playBtn.classList.toggle("is-playing", on);
    playBtn.setAttribute("aria-label", on ? "Pausa" : "Riproduci");
    if ("mediaSession" in navigator) {
      try { navigator.mediaSession.playbackState = on ? "playing" : "paused"; } catch (e) {}
    }
  }
  function showWaiting(on) {
    clearTimeout(waitTimer);
    if (on) waitTimer = setTimeout(function () { if (!a.paused) statusEl.hidden = false; }, 700);
    else statusEl.hidden = true;
  }

  function doPlay() {
    errEl.hidden = true;
    var p;
    try { p = a.play(); } catch (e) { return; }
    if (p && p.catch) p.catch(function (e) {
      if (e && e.name === "NotAllowedError") setPlayingUI(false);
    });
  }
  function skip(delta) {
    var d = duration();
    var t = (a.currentTime || 0) + delta;
    if (d) t = Math.max(0, Math.min(t, d - 0.5)); else t = Math.max(0, t);
    try { a.currentTime = t; } catch (e) {}
    paint(t);
  }

  // play() sincrono dentro il gesto dell'utente
  playBtn.addEventListener("click", function () {
    if (a.error) { retries = 0; reloadFrom(lastTime, true); }
    else if (a.paused || a.ended) doPlay();
    else a.pause();
  });
  $("back").addEventListener("click", function () { skip(-SKIP); });
  $("fwd").addEventListener("click", function () { skip(SKIP); });

  seek.addEventListener("input", function () {
    dragging = true;
    var t = +seek.value;
    var d = duration();
    seek.style.setProperty("--p", (d ? (t / d) * 100 : 0) + "%");
    cur.textContent = fmt(t);
  });
  seek.addEventListener("change", function () {
    dragging = false;
    try { a.currentTime = +seek.value; } catch (e) {}
  });

  /* Retry: ricarica la sorgente e riparte dal punto salvato */
  function reloadFrom(t, autoplay) {
    pendingSeek = t;
    errEl.hidden = true;
    a.src = SRC + (SRC.indexOf("?") < 0 ? "?" : "&") + "r=" + Date.now();
    a.load();
    if (autoplay) doPlay();
  }
  $("retry").addEventListener("click", function () {
    retries = 0;
    reloadFrom(lastTime, true);
  });

  a.addEventListener("loadedmetadata", onMeta);
  a.addEventListener("durationchange", onMeta);
  a.addEventListener("timeupdate", function () {
    var t = a.currentTime || 0;
    if (t > 0) lastTime = t;
    paint(t);
    updatePositionThrottled();
  });
  a.addEventListener("play", function () { setPlayingUI(true); });
  a.addEventListener("playing", function () { setPlayingUI(true); showWaiting(false); errEl.hidden = true; retries = 0; });
  a.addEventListener("pause", function () { setPlayingUI(false); showWaiting(false); updatePosition(); });
  a.addEventListener("waiting", function () { showWaiting(true); });
  a.addEventListener("stalled", function () { if (!a.paused) showWaiting(true); });
  a.addEventListener("seeked", function () { updatePosition(); });
  a.addEventListener("error", function () {
    if (!a.getAttribute("src")) return;
    var wasPlaying = playBtn.classList.contains("is-playing");
    showWaiting(false);
    // un tentativo automatico, poi pulsante "Riprova"
    if (wasPlaying && retries < 1 && navigator.onLine !== false) {
      retries++;
      setTimeout(function () { reloadFrom(lastTime, true); }, 1500);
      return;
    }
    setPlayingUI(false);
    errEl.hidden = false;
  });
  window.addEventListener("online", function () {
    if (!errEl.hidden) { retries = 0; reloadFrom(lastTime, true); }
  });
  a.addEventListener("ended", function () {
    setPlayingUI(false);
    showWaiting(false);
    $("intro").hidden = true;
    $("player").hidden = true;
    $("help").hidden = true;
    $("final").hidden = false;
    window.scrollTo(0, 0);
  });

  /* ---------------- Media Session (schermata di blocco) ---------------- */
  var lastPos = 0;
  function updatePosition() {
    if (!("mediaSession" in navigator) || !navigator.mediaSession.setPositionState) return;
    var d = duration();
    if (!d) return;
    try {
      navigator.mediaSession.setPositionState({
        duration: d,
        playbackRate: a.playbackRate || 1,
        position: Math.max(0, Math.min(a.currentTime || 0, d))
      });
    } catch (e) {}
  }
  function updatePositionThrottled() {
    var now = Date.now();
    if (now - lastPos > 1000) { lastPos = now; updatePosition(); }
  }
  if ("mediaSession" in navigator) {
    try {
      var base = location.href.replace(/[#?].*$/, "").replace(/[^/]*$/, "");
      navigator.mediaSession.metadata = new MediaMetadata({
        title: "Silent Walk",
        artist: "FreeSpace APS",
        album: "Camminiamo insieme: voci contro il silenzio",
        artwork: [{ src: base + "assets/cover-512.png", sizes: "512x512", type: "image/png" }]
      });
    } catch (e) {}
    var handlers = {
      play: function () { doPlay(); },
      pause: function () { a.pause(); },
      seekbackward: function (d) { skip(-((d && d.seekOffset) || SKIP)); },
      seekforward: function (d) { skip((d && d.seekOffset) || SKIP); },
      seekto: function (d) {
        if (!d || typeof d.seekTime !== "number") return;
        if (d.fastSeek && "fastSeek" in a) a.fastSeek(d.seekTime);
        else a.currentTime = d.seekTime;
        paint(d.seekTime);
      }
    };
    for (var k in handlers) {
      try { navigator.mediaSession.setActionHandler(k, handlers[k]); } catch (e) {}
    }
  }
})();
