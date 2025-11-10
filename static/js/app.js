// ==================== DARK MODE ====================
const themeToggle = document.getElementById("theme-toggle");
const body = document.body;

document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    body.classList.add("dark");
    if (themeToggle) themeToggle.textContent = "☀️";
  }
});

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    body.classList.add("theme-transition");
    setTimeout(() => body.classList.remove("theme-transition"), 600);

    const isDark = body.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    themeToggle.textContent = isDark ? "☀️" : "🌙";
  });
}

// ==================== FLASH MESSAGE AUTO HIDE ====================
document.addEventListener("DOMContentLoaded", () => {
  const toasts = document.querySelectorAll(".toast");
  toasts.forEach(t => {
    setTimeout(() => {
      t.style.opacity = "0";
      t.style.transform = "translateY(-10px)";
      setTimeout(() => t.remove(), 500);
    }, 3000);
  });
});

// ==================== PAGE LOAD FADE ====================
window.addEventListener("load", () => {
  document.body.classList.add("loaded");
  const loader = document.getElementById("loader-overlay");
  if (loader) loader.style.display = "none";
});

// ==================== LOADING SPINNER ON FORM SUBMIT ====================
document.addEventListener("submit", (e) => {
  const loader = document.getElementById("loader-overlay");
  if (loader) loader.style.display = "flex";
});

// ==================== LOADER ON PAGE NAVIGATION ====================
document.querySelectorAll("a").forEach(link => {
  link.addEventListener("click", (e) => {
    const href = link.getAttribute("href");
    if (href && !href.startsWith("#") && !href.startsWith("javascript")) {
      const loader = document.getElementById("loader-overlay");
      if (loader) loader.style.display = "flex";
    }
  });
});
