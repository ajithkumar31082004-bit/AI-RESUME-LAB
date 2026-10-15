/**
 * AI RESUME LAB — Auth Module
 * Handles user authentication, session management, and UI state
 */

const Auth = {
  TOKEN_KEY: 'arl_token',
  USER_KEY: 'arl_user',

  // ── Token Management ──────────────────────────────────────────
  setToken(token) {
    localStorage.setItem(this.TOKEN_KEY, token);
  },

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  removeToken() {
    localStorage.removeItem(this.TOKEN_KEY);
  },

  // ── User Management ───────────────────────────────────────────
  setUser(user) {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  },

  getUser() {
    try {
      return JSON.parse(localStorage.getItem(this.USER_KEY));
    } catch {
      return null;
    }
  },

  removeUser() {
    localStorage.removeItem(this.USER_KEY);
  },

  // ── Session Check ─────────────────────────────────────────────
  isLoggedIn() {
    return !!this.getToken();
  },

  // ── Login / Logout ────────────────────────────────────────────
  async login(email, password) {
    try {
      let data;
      try {
        data = await AuthAPI.login(email, password);
      } catch (err) {
        // Demo mode: allow test@demo.com / demo123
        if (email === 'test@demo.com' && password === 'demo123') {
          data = {
            token: 'demo_token_' + Date.now(),
            user: { id: 1, name: 'Alex Johnson', email, role: 'user' },
          };
        } else {
          throw err;
        }
      }
      this.setToken(data.token);
      this.setUser(data.user);
      return { success: true, user: data.user };
    } catch (err) {
      return { success: false, message: err.message || 'Login failed' };
    }
  },

  async register(name, email, password) {
    try {
      const data = await AuthAPI.register(name, email, password);
      this.setToken(data.token);
      this.setUser(data.user);
      return { success: true, user: data.user };
    } catch (err) {
      return { success: false, message: err.message || 'Registration failed' };
    }
  },

  async logout() {
    try {
      await AuthAPI.logout();
    } catch {}
    this.removeToken();
    this.removeUser();
    window.location.href = 'login.html';
  },

  // ── UI Helpers ────────────────────────────────────────────────
  updateNavUI() {
    const user = this.getUser();
    const loginBtns = document.querySelectorAll('.nav-login-btn');
    const userMenus = document.querySelectorAll('.nav-user-menu');
    const userNames = document.querySelectorAll('.nav-user-name');
    const userAvatars = document.querySelectorAll('.nav-avatar');

    if (this.isLoggedIn() && user) {
      loginBtns.forEach(btn => btn.style.display = 'none');
      userMenus.forEach(el => el.style.display = 'flex');
      userNames.forEach(el => el.textContent = user.name.split(' ')[0]);
      userAvatars.forEach(el => el.textContent = user.name.charAt(0).toUpperCase());
    } else {
      loginBtns.forEach(btn => btn.style.display = 'inline-flex');
      userMenus.forEach(el => el.style.display = 'none');
    }
  },

  // ── Guard: Redirect if not authenticated ─────────────────────
  requireAuth() {
    if (!this.isLoggedIn()) {
      const returnUrl = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `login.html?return=${returnUrl}`;
      return false;
    }
    return true;
  },

  // ── Guard: Redirect if already authenticated ──────────────────
  redirectIfAuth() {
    if (this.isLoggedIn()) {
      window.location.href = 'dashboard.html';
    }
  },
};

// ── DOM Ready ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Auth.updateNavUI();

  // Attach logout handler to all logout buttons
  document.querySelectorAll('[data-action="logout"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      Auth.logout();
    });
  });

  // Handle login form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    Auth.redirectIfAuth();
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;
      const btn = loginForm.querySelector('[type="submit"]');
      const errEl = document.getElementById('login-error');

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Signing in...';
      if (errEl) errEl.textContent = '';

      const result = await Auth.login(email, password);

      if (result.success) {
        Toast.show('success', 'Welcome back!', `Hello, ${result.user.name}`);
        setTimeout(() => {
          const params = new URLSearchParams(window.location.search);
          const returnUrl = params.get('return') || 'dashboard.html';
          window.location.href = returnUrl;
        }, 800);
      } else {
        if (errEl) errEl.textContent = result.message;
        btn.disabled = false;
        btn.innerHTML = '<span>🔑</span> Sign In';
      }
    });
  }

  // Handle register form
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    Auth.redirectIfAuth();
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('reg-name').value.trim();
      const email = document.getElementById('reg-email').value.trim();
      const password = document.getElementById('reg-password').value;
      const confirm = document.getElementById('reg-confirm').value;
      const btn = registerForm.querySelector('[type="submit"]');
      const errEl = document.getElementById('reg-error');

      if (password !== confirm) {
        if (errEl) errEl.textContent = 'Passwords do not match';
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Creating account...';
      if (errEl) errEl.textContent = '';

      const result = await Auth.register(name, email, password);

      if (result.success) {
        Toast.show('success', 'Account created!', 'Welcome to AI Resume Lab');
        setTimeout(() => { window.location.href = 'dashboard.html'; }, 800);
      } else {
        if (errEl) errEl.textContent = result.message;
        btn.disabled = false;
        btn.innerHTML = '<span>🚀</span> Create Account';
      }
    });
  }
});

window.Auth = Auth;
