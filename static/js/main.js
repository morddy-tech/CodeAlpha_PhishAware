/* PhishAware frontend behaviour.
   - Theme switching (light / dark / system)
   - Mobile navigation
   - User dropdown
   - Quiz timer
 */

(function () {
  "use strict";

  function getStoredTheme() {
    try {
      return localStorage.getItem("phishaware-theme");
    } catch (e) {
      return null;
    }
  }

  function setStoredTheme(theme) {
    try {
      localStorage.setItem("phishaware-theme", theme);
    } catch (e) {
      /* ignore storage errors */
    }
  }

  function preferredTheme() {
    var stored = getStoredTheme();
    if (stored === "light" || stored === "dark") return stored;
    var html = document.documentElement;
    var profile = html.getAttribute("data-profile-theme");
    if (stored === "system" || !stored) {
      if (profile === "light" || profile === "dark") return profile;
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    return "light";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var toggle = document.getElementById("theme-toggle");
    if (toggle) {
      toggle.setAttribute("aria-label", "Switch to " + (theme === "dark" ? "light" : "dark") + " mode");
      toggle.innerHTML =
        theme === "dark"
          ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
          : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    }
  }

  function cycleTheme() {
    var current = preferredTheme();
    var next = current === "dark" ? "light" : "dark";
    setStoredTheme(next);
    applyTheme(next);
  }

  function initTheme() {
    applyTheme(preferredTheme());
    var toggle = document.getElementById("theme-toggle");
    if (toggle) toggle.addEventListener("click", cycleTheme);
    var media = window.matchMedia("(prefers-color-scheme: dark)");
    if (media.addEventListener) {
      media.addEventListener("change", function () {
        if (getStoredTheme() !== "light" && getStoredTheme() !== "dark") applyTheme(preferredTheme());
      });
    }
  }

  function initMobileNav() {
    var toggle = document.getElementById("nav-toggle");
    var menu = document.getElementById("mobile-menu");
    if (!toggle || !menu) return;
    toggle.addEventListener("click", function () {
      var open = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  function initDropdown() {
    var chip = document.getElementById("user-chip");
    var dropdown = document.getElementById("user-dropdown");
    if (!chip || !dropdown) return;
    chip.addEventListener("click", function (e) {
      e.stopPropagation();
      dropdown.classList.toggle("open");
      chip.setAttribute("aria-expanded", dropdown.classList.contains("open") ? "true" : "false");
    });
    document.addEventListener("click", function (e) {
      if (!dropdown.contains(e.target) && !chip.contains(e.target)) {
        dropdown.classList.remove("open");
      }
    });
  }

  function initQuizTimer() {
    var timerEl = document.getElementById("quiz-timer");
    var form = document.getElementById("quiz-form");
    if (!timerEl || !form) return;
    var total = parseInt(timerEl.getAttribute("data-seconds"), 10);
    if (isNaN(total) || total < 0) return;

    function format(s) {
      var m = Math.floor(s / 60);
      var sec = s % 60;
      return m + ":" + (sec < 10 ? "0" : "") + sec;
    }

    var submitted = false;
    function submitOnce() {
      if (submitted) return;
      submitted = true;
      form.submit();
    }

    if (total <= 0) {
      timerEl.textContent = format(0);
      submitOnce();
      return;
    }

    var end = Date.now() + total * 1000;
    var interval = setInterval(function () {
      var remaining = Math.max(0, Math.round((end - Date.now()) / 1000));
      timerEl.textContent = format(remaining);
      if (remaining <= 0) {
        clearInterval(interval);
        submitOnce();
      }
    }, 1000);
  }

  function initAutoDismiss() {
    document.querySelectorAll(".alert[data-dismiss]").forEach(function (el) {
      setTimeout(function () {
        el.style.transition = "opacity .5s ease";
        el.style.opacity = "0";
        setTimeout(function () { el.remove(); }, 550);
      }, 6000);
    });
  }

  function initHeroCarousel() {
    var carousel = document.getElementById("hero-carousel");
    if (!carousel) return;
    var slides = Array.prototype.slice.call(carousel.querySelectorAll(".mock-slide"));
    if (slides.length < 2) return;
    var parent = carousel.parentElement;
    var dotsWrap = parent.querySelector(".carousel-dots");
    var current = 0;
    var interval = null;
    var DURATION = 10000;

    // The HTML hides all but the first slide as a no-JS fallback; the
    // carousel takes over from here so fades can animate.
    slides.forEach(function (slide) {
      slide.removeAttribute("hidden");
    });

    function show(index) {
      slides.forEach(function (slide, i) {
        var active = i === index;
        slide.classList.toggle("active", active);
        slide.setAttribute("aria-hidden", active ? "false" : "true");
      });
      if (dotsWrap) {
        dotsWrap.querySelectorAll(".carousel-dot").forEach(function (dot, i) {
          dot.setAttribute("aria-current", i === index ? "true" : "false");
        });
      }
    }

    function next() {
      current = (current + 1) % slides.length;
      show(current);
    }

    function prev() {
      current = (current - 1 + slides.length) % slides.length;
      show(current);
    }

    function start() {
      if (interval) return;
      interval = setInterval(next, DURATION);
    }

    function stop() {
      if (interval) {
        clearInterval(interval);
        interval = null;
      }
    }

    function restart() {
      stop();
      start();
    }

    function goTo(index) {
      current = index;
      show(current);
      restart();
    }

    // Reduced motion: show the first example only, no rotation.
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      show(0);
      return;
    }

    if (dotsWrap) {
      slides.forEach(function (_, i) {
        var dot = document.createElement("button");
        dot.type = "button";
        dot.className = "carousel-dot";
        dot.setAttribute("aria-label", "Show phishing example " + (i + 1));
        dot.addEventListener("click", function () {
          goTo(i);
        });
        dotsWrap.appendChild(dot);
      });
    }

    // Keyboard support (carousel region is focusable via tabindex="0").
    carousel.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        prev();
        restart();
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        next();
        restart();
      }
    });

    show(0);
    start();
    // Pause while the visitor is interacting with the carousel.
    carousel.addEventListener("mouseenter", stop);
    carousel.addEventListener("mouseleave", start);
    carousel.addEventListener("focusin", stop);
    carousel.addEventListener("focusout", start);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initMobileNav();
    initDropdown();
    initQuizTimer();
    initAutoDismiss();
    initHeroCarousel();
  });
})();