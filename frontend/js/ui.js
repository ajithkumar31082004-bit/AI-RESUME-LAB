/**
 * AI RESUME LAB — UI Utilities
 * Toast, AOS, Score Circles, Progress Bars, Theme Toggle, Nav
 */

// ============================================================
// TOAST NOTIFICATION SYSTEM
// ============================================================
const Toast = {
  container: null,

  _ensureContainer() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  show(type = 'info', title = '', message = '', duration = 4000) {
    this._ensureContainer();

    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <div class="toast-content">
        ${title ? `<div class="toast-title">${title}</div>` : ''}
        ${message ? `<div class="toast-message">${message}</div>` : ''}
      </div>
      <button class="toast-close" aria-label="Close">✕</button>
    `;

    this.container.appendChild(toast);
    toast.querySelector('.toast-close').addEventListener('click', () => this._remove(toast));
    setTimeout(() => this._remove(toast), duration);
    return toast;
  },

  _remove(toast) {
    toast.style.animation = 'fadeOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  },

  success(title, message) { return this.show('success', title, message); },
  error(title, message) { return this.show('error', title, message); },
  warning(title, message) { return this.show('warning', title, message); },
  info(title, message) { return this.show('info', title, message); },
};

// ============================================================
// ANIMATE ON SCROLL (AOS)
// ============================================================
const AOS = {
  init() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('aos-visible');
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('[data-aos]').forEach(el => observer.observe(el));
  },
};

// ============================================================
// SCORE CIRCLE SVG
// ============================================================
const ScoreCircle = {
  /**
   * Render an animated SVG score circle
   * @param {HTMLElement} el  - container element
   * @param {number} score    - 0-100
   * @param {string} color    - 'cyan' | 'purple' | 'emerald'
   * @param {string} label    - text below circle
   */
  render(el, score, color = 'cyan', label = '') {
    const radius = 52;
    const circumference = 2 * Math.PI * radius;
    const gradId = `grad-${color}-${Math.random().toString(36).substr(2, 6)}`;

    const gradColors = {
      cyan: ['#06b6d4', '#3b82f6'],
      purple: ['#8b5cf6', '#ec4899'],
      emerald: ['#10b981', '#34d399'],
      amber: ['#f59e0b', '#fbbf24'],
    };
    const [c1, c2] = gradColors[color] || gradColors.cyan;

    el.innerHTML = `
      <div class="score-circle-wrap">
        <div class="score-circle">
          <svg viewBox="0 0 120 120">
            <defs>
              <linearGradient id="${gradId}" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="${c1}"/>
                <stop offset="100%" stop-color="${c2}"/>
              </linearGradient>
            </defs>
            <circle class="track" cx="60" cy="60" r="${radius}"/>
            <circle class="fill" cx="60" cy="60" r="${radius}"
              stroke="url(#${gradId})"
              stroke-dasharray="${circumference}"
              stroke-dashoffset="${circumference}"
              id="${gradId}-fill"/>
          </svg>
          <div class="score-inner">
            <div class="score-number">${score}</div>
            <div class="score-total">/100</div>
          </div>
        </div>
        ${label ? `<div class="score-label">${label}</div>` : ''}
      </div>
    `;

    // Animate after a short delay
    requestAnimationFrame(() => {
      setTimeout(() => {
        const fill = document.getElementById(`${gradId}-fill`);
        if (fill) {
          const offset = circumference * (1 - score / 100);
          fill.style.strokeDashoffset = offset;
        }
      }, 300);
    });
  },
};

// ============================================================
// PROGRESS BAR ANIMATION
// ============================================================
const ProgressBar = {
  /**
   * Animate a progress bar fill to a target percentage
   */
  animate(fillEl, percentage, delay = 0) {
    fillEl.style.width = '0%';
    setTimeout(() => {
      fillEl.style.width = `${Math.min(100, Math.max(0, percentage))}%`;
    }, delay);
  },

  /**
   * Create a progress bar element
   */
  create(label, value, max = 100, colorClass = 'cyan') {
    const pct = Math.round((value / max) * 100);
    const wrap = document.createElement('div');
    wrap.className = 'progress-wrap';
    wrap.innerHTML = `
      <div class="progress-header">
        <span class="progress-label">${label}</span>
        <span class="progress-value">${value}${max === 100 ? '%' : `/${max}`}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill ${colorClass}" style="width:0%" data-target="${pct}"></div>
      </div>
    `;
    return wrap;
  },

  /**
   * Animate all progress fills on page
   */
  animateAll(delay = 400) {
    setTimeout(() => {
      document.querySelectorAll('.progress-fill[data-target]').forEach(fill => {
        fill.style.width = fill.getAttribute('data-target') + '%';
      });
    }, delay);
  },
};

// ============================================================
// NAVBAR SCROLL BEHAVIOR
// ============================================================
const Navbar = {
  init() {
    const nav = document.querySelector('.navbar');
    if (!nav) return;

    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });

    // Hamburger toggle
    const hamburger = document.querySelector('.hamburger');
    const mobileNav = document.querySelector('.mobile-nav');
    if (hamburger && mobileNav) {
      hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('open');
        mobileNav.classList.toggle('open');
      });
    }

    // Active link highlighting
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a, .mobile-nav a').forEach(link => {
      const href = link.getAttribute('href');
      if (href === currentPage || (currentPage === '' && href === 'index.html')) {
        link.classList.add('active');
      }
    });
  },
};

// ============================================================
// THEME TOGGLE (Dark / Light)
// ============================================================
const Theme = {
  STORAGE_KEY: 'arl_theme',

  init() {
    const saved = localStorage.getItem(this.STORAGE_KEY);
    if (saved === 'light') document.body.classList.add('light-mode');
    this._updateToggle();
  },

  toggle() {
    document.body.classList.toggle('light-mode');
    const isLight = document.body.classList.contains('light-mode');
    localStorage.setItem(this.STORAGE_KEY, isLight ? 'light' : 'dark');
    this._updateToggle();
  },

  _updateToggle() {
    const btn = document.querySelector('[data-theme-toggle]');
    if (btn) {
      const isLight = document.body.classList.contains('light-mode');
      btn.textContent = isLight ? '🌙' : '☀️';
      btn.setAttribute('title', isLight ? 'Switch to dark mode' : 'Switch to light mode');
    }
  },
};

// ============================================================
// TABS
// ============================================================
const Tabs = {
  init(container) {
    const tabBtns = container.querySelectorAll('.tab-btn');
    const tabContents = container.querySelectorAll('.tab-content');

    tabBtns.forEach((btn, i) => {
      btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        if (tabContents[i]) tabContents[i].classList.add('active');
      });
    });

    // Activate first tab
    if (tabBtns[0]) tabBtns[0].click();
  },

  initAll() {
    document.querySelectorAll('[data-tabs]').forEach(container => this.init(container));
  },
};

// ============================================================
// UPLOAD ZONE
// ============================================================
const UploadZone = {
  init(zoneEl, onFileSelect) {
    if (!zoneEl) return;
    const input = zoneEl.querySelector('input[type="file"]');

    // Click to browse
    zoneEl.addEventListener('click', (e) => {
      if (e.target !== input) input.click();
    });

    // File input change
    if (input) {
      input.addEventListener('change', () => {
        if (input.files.length) onFileSelect(input.files[0]);
      });
    }

    // Drag & Drop
    zoneEl.addEventListener('dragover', (e) => {
      e.preventDefault();
      zoneEl.classList.add('drag-over');
    });

    zoneEl.addEventListener('dragleave', () => {
      zoneEl.classList.remove('drag-over');
    });

    zoneEl.addEventListener('drop', (e) => {
      e.preventDefault();
      zoneEl.classList.remove('drag-over');
      const file = e.dataTransfer.files[0];
      if (file) onFileSelect(file);
    });
  },
};

// ============================================================
// MODAL
// ============================================================
const Modal = {
  open(id) {
    const overlay = document.getElementById(id);
    if (overlay) {
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
  },
  close(id) {
    const overlay = document.getElementById(id);
    if (overlay) {
      overlay.classList.remove('open');
      document.body.style.overflow = '';
    }
  },
  closeAll() {
    document.querySelectorAll('.modal-overlay.open').forEach(o => {
      o.classList.remove('open');
    });
    document.body.style.overflow = '';
  },
  init() {
    // Close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) this.closeAll();
      });
    });
    // Close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
      btn.addEventListener('click', () => this.closeAll());
    });
    // ESC key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.closeAll();
    });
  },
};

// ============================================================
// COUNTER ANIMATION
// ============================================================
const Counter = {
  animate(el, target, duration = 1500, prefix = '', suffix = '') {
    const start = performance.now();
    const update = (timestamp) => {
      const elapsed = timestamp - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      const current = Math.round(eased * target);
      el.textContent = prefix + current + suffix;
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  },

  initAll() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.dataset.animated) {
          entry.target.dataset.animated = 'true';
          const target = parseInt(entry.target.dataset.count || 0);
          const suffix = entry.target.dataset.suffix || '';
          const prefix = entry.target.dataset.prefix || '';
          this.animate(entry.target, target, 1500, prefix, suffix);
        }
      });
    }, { threshold: 0.5 });

    document.querySelectorAll('[data-count]').forEach(el => observer.observe(el));
  },
};

// ============================================================
// SIDEBAR MOBILE
// ============================================================
const Sidebar = {
  init() {
    const toggleBtn = document.querySelector('[data-sidebar-toggle]');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    if (!toggleBtn || !sidebar) return;

    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
      if (overlay) overlay.classList.toggle('active');
    });

    if (overlay) {
      overlay.addEventListener('click', () => {
        sidebar.classList.remove('mobile-open');
        overlay.classList.remove('active');
      });
    }
  },
};

// ============================================================
// CHART UTILITIES (Using CSS-only charts or Canvas)
// ============================================================
const Charts = {
  /**
   * Draw a simple line chart on a canvas element
   */
  lineChart(canvas, data, labels = [], color = '#06b6d4') {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const { width, height } = canvas;
    const padding = 30;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    ctx.clearRect(0, 0, width, height);

    const max = Math.max(...data) * 1.1;
    const min = Math.min(...data) * 0.9;
    const range = max - min;

    const points = data.map((val, i) => ({
      x: padding + (i / (data.length - 1)) * chartWidth,
      y: padding + chartHeight - ((val - min) / range) * chartHeight,
    }));

    // Gradient fill
    const grad = ctx.createLinearGradient(0, padding, 0, height - padding);
    grad.addColorStop(0, color + '40');
    grad.addColorStop(1, color + '05');

    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.forEach(p => ctx.lineTo(p.x, p.y));
    ctx.lineTo(points[points.length - 1].x, height - padding);
    ctx.lineTo(points[0].x, height - padding);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // Line
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.forEach(p => ctx.lineTo(p.x, p.y));
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.stroke();

    // Dots
    points.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = '#020817';
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  },

  /**
   * Draw a simple bar chart
   */
  barChart(canvas, data, labels = [], colors = []) {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const { width, height } = canvas;
    const padding = { top: 20, right: 20, bottom: 40, left: 30 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    ctx.clearRect(0, 0, width, height);

    const max = Math.max(...data) * 1.1;
    const barWidth = (chartWidth / data.length) * 0.6;
    const gap = (chartWidth / data.length) * 0.4;

    const defaultColors = ['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b'];

    data.forEach((val, i) => {
      const barHeight = (val / max) * chartHeight;
      const x = padding.left + i * (barWidth + gap) + gap / 2;
      const y = padding.top + chartHeight - barHeight;
      const col = colors[i] || defaultColors[i % defaultColors.length];

      const grad = ctx.createLinearGradient(0, y, 0, y + barHeight);
      grad.addColorStop(0, col);
      grad.addColorStop(1, col + '80');

      // Rounded top bars
      const r = Math.min(4, barWidth / 2);
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.lineTo(x + barWidth - r, y);
      ctx.arcTo(x + barWidth, y, x + barWidth, y + r, r);
      ctx.lineTo(x + barWidth, y + barHeight);
      ctx.lineTo(x, y + barHeight);
      ctx.arcTo(x, y, x + r, y, r);
      ctx.closePath();
      ctx.fillStyle = grad;
      ctx.fill();

      // Label
      if (labels[i]) {
        ctx.fillStyle = 'rgba(148,163,184,0.8)';
        ctx.font = '10px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(labels[i], x + barWidth / 2, height - 10);
      }
    });
  },

  /**
   * Draw a donut chart
   */
  donutChart(canvas, segments, colors = []) {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const outerR = Math.min(cx, cy) - 8;
    const innerR = outerR * 0.6;
    const total = segments.reduce((a, b) => a + b, 0);
    const defaultColors = ['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let startAngle = -Math.PI / 2;
    segments.forEach((val, i) => {
      const sliceAngle = (val / total) * Math.PI * 2;
      const col = colors[i] || defaultColors[i % defaultColors.length];

      ctx.beginPath();
      ctx.arc(cx, cy, outerR, startAngle, startAngle + sliceAngle);
      ctx.arc(cx, cy, innerR, startAngle + sliceAngle, startAngle, true);
      ctx.closePath();
      ctx.fillStyle = col;
      ctx.fill();
      startAngle += sliceAngle;
    });
  },
};

// ============================================================
// INIT ON DOM READY
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  Navbar.init();
  AOS.init();
  Theme.init();
  Modal.init();
  Tabs.initAll();
  Counter.initAll();
  ProgressBar.animateAll();
  Sidebar.init();

  // Theme toggle btn
  document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
    btn.addEventListener('click', () => Theme.toggle());
  });
});

// Expose globally
window.Toast = Toast;
window.AOS = AOS;
window.ScoreCircle = ScoreCircle;
window.ProgressBar = ProgressBar;
window.UploadZone = UploadZone;
window.Modal = Modal;
window.Counter = Counter;
window.Charts = Charts;
window.Theme = Theme;
window.Tabs = Tabs;
