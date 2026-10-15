/**
 * AI RESUME LAB — API Service
 * Handles all communication with the Flask backend
 */

// ── Configuration ──────────────────────────────────────────────
const CONFIG = {
  // Change this to your EC2 instance URL when deploying
  API_BASE_URL: window.API_BASE_URL || 'http://localhost:5000/api',
  VERSION: '1.0.0',
  TIMEOUT: 30000,
};

// ── HTTP Client ─────────────────────────────────────────────────
class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  _getHeaders(isForm = false) {
    const headers = {};
    const token = Auth.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!isForm) headers['Content-Type'] = 'application/json';
    return headers;
  }

  async _handleResponse(response) {
    const contentType = response.headers.get('Content-Type') || '';
    const isJson = contentType.includes('application/json');
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const message = (isJson && data.message) ? data.message : `HTTP ${response.status}`;
      const error = new Error(message);
      error.status = response.status;
      error.data = data;
      throw error;
    }
    return data;
  }

  async get(endpoint, params = {}) {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    Object.entries(params).forEach(([k, v]) => url.searchParams.append(k, v));
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: this._getHeaders(),
    });
    return this._handleResponse(response);
  }

  async post(endpoint, body = {}) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this._getHeaders(),
      body: JSON.stringify(body),
    });
    return this._handleResponse(response);
  }

  async postForm(endpoint, formData) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this._getHeaders(true),
      body: formData,
    });
    return this._handleResponse(response);
  }

  async put(endpoint, body = {}) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: this._getHeaders(),
      body: JSON.stringify(body),
    });
    return this._handleResponse(response);
  }

  async delete(endpoint) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this._getHeaders(),
    });
    return this._handleResponse(response);
  }
}

const api = new ApiClient(CONFIG.API_BASE_URL);

// ── Auth API ────────────────────────────────────────────────────
const AuthAPI = {
  async register(name, email, password) {
    return api.post('/auth/register', { name, email, password });
  },
  async login(email, password) {
    return api.post('/auth/login', { email, password });
  },
  async logout() {
    return api.post('/auth/logout');
  },
  async me() {
    return api.get('/auth/me');
  },
  async changePassword(oldPassword, newPassword) {
    return api.put('/auth/password', { old_password: oldPassword, new_password: newPassword });
  },
};

// ── Resume API ──────────────────────────────────────────────────
const ResumeAPI = {
  async upload(file, jobDescription = '') {
    const form = new FormData();
    form.append('file', file);
    if (jobDescription) form.append('job_description', jobDescription);
    return api.postForm('/resume/upload', form);
  },
  async analyzeText(resumeText, jobDescription = '') {
    return api.post('/resume/analyze-text', { resume_text: resumeText, job_description: jobDescription });
  },
  async getAll() {
    return api.get('/resume/list');
  },
  async getById(id) {
    return api.get(`/resume/${id}`);
  },
  async delete(id) {
    return api.delete(`/resume/${id}`);
  },
  async getAnalysis(resumeId) {
    return api.get(`/analyze/${resumeId}`);
  },
};

// ── Job Matching API ────────────────────────────────────────────
const JobAPI = {
  async match(resumeId, jobDescription) {
    return api.post('/jobs/match', { resume_id: resumeId, job_description: jobDescription });
  },
  async getMatches() {
    return api.get('/jobs/list');
  },
  async analyzeSkillGap(skills, targetRole) {
    return api.post('/skills/gap', { skills, target_role: targetRole });
  },
  async getLearningPath(targetRole) {
    return api.get('/skills/learning-path', { role: targetRole });
  },
};

// ── Interview API ───────────────────────────────────────────────
const InterviewAPI = {
  async getQuestions(role, level, technology) {
    return api.post('/interview/questions', { role, level, technology });
  },
  async submitAnswer(sessionId, questionId, answer) {
    return api.post('/interview/answer', { session_id: sessionId, question_id: questionId, answer });
  },
  async startSession(role, level) {
    return api.post('/interview/session', { role, level });
  },
  async getHistory() {
    return api.get('/interview/history');
  },
};

// ── Dashboard API ───────────────────────────────────────────────
const DashboardAPI = {
  async getData() {
    return api.get('/dashboard/summary');
  },
  async getApplications() {
    return api.get('/dashboard/applications');
  },
  async addApplication(data) {
    return api.post('/dashboard/applications', data);
  },
  async updateApplication(id, data) {
    return api.put(`/dashboard/applications/${id}`, data);
  },
  async deleteApplication(id) {
    return api.delete(`/dashboard/applications/${id}`);
  },
};

// ── AI Content API ──────────────────────────────────────────────
const AIContentAPI = {
  async improveSummary(summary, jobTitle) {
    return api.post('/ai/improve-summary', { summary, job_title: jobTitle });
  },
  async rewriteExperience(experience) {
    return api.post('/ai/rewrite-experience', { experience });
  },
  async generateHeadline(name, skills, experience) {
    return api.post('/ai/generate-headline', { name, skills, experience });
  },
  async optimizeKeywords(text, jobDescription) {
    return api.post('/ai/optimize-keywords', { text, job_description: jobDescription });
  },
  async generateAchievement(role, task) {
    return api.post('/ai/generate-achievement', { role, task });
  },
};

// ── Mock Data (used when backend is not connected) ───────────────
const MockData = {
  analysisResult: {
    ats_score: 87,
    job_match: 92,
    resume_structure: 88,
    keywords_score: 85,
    skills_score: 90,
    experience_score: 82,
    education_score: 95,
    formatting_score: 88,
    strengths: [
      "Strong technical skills in Python and cloud technologies",
      "Relevant project experience with measurable outcomes",
      "Clear education section with notable achievements",
      "Good use of action verbs throughout the document",
      "Well-structured work experience with chronological order",
    ],
    weaknesses: [
      "Professional summary lacks specific quantifiable achievements",
      "Missing some industry-specific keywords for the target role",
      "Work experience bullet points could include more metrics",
      "Skills section could be better organized by category",
    ],
    missing_skills: ["Kubernetes", "Terraform", "Jenkins", "Prometheus", "Grafana"],
    recommendations: [
      {
        issue: "Weak professional summary",
        why: "Recruiters spend 6-7 seconds scanning resumes. A compelling summary is your first impression.",
        fix: "Rewrite your summary to include years of experience, key skills, and one measurable achievement.",
      },
      {
        issue: "Missing ATS keywords",
        why: "Many companies use ATS systems that filter resumes before human review.",
        fix: "Add keywords like 'containerization', 'CI/CD pipeline', 'infrastructure as code' from the job description.",
      },
      {
        issue: "No quantifiable achievements",
        why: "Numbers make your experience more credible and impactful.",
        fix: "Transform each bullet point with metrics: 'Improved deployment time by 40%' vs 'Improved deployments'.",
      },
    ],
    matching_skills: ["Python", "AWS", "Docker", "SQL", "Git", "Linux", "REST APIs", "Agile"],
  },

  dashboardData: {
    ats_score: 87,
    job_match: 92,
    total_skills: 24,
    total_applications: 12,
    total_interviews: 4,
    resume_health: 87,
    score_history: [72, 75, 78, 80, 82, 85, 87],
    applications: [
      { company: "Google", job_title: "Cloud Engineer", status: "interview", applied_date: "2024-01-10" },
      { company: "Amazon", job_title: "DevOps Engineer", status: "applied", applied_date: "2024-01-08" },
      { company: "Microsoft", job_title: "SRE", status: "offer", applied_date: "2024-01-05" },
      { company: "Netflix", job_title: "Platform Engineer", status: "rejected", applied_date: "2024-01-02" },
      { company: "Stripe", job_title: "Backend Engineer", status: "applied", applied_date: "2024-01-01" },
    ],
  },

  interviewQuestions: {
    technical: [
      "Explain the difference between containers and virtual machines.",
      "How does Kubernetes handle service discovery?",
      "What is the CAP theorem and how does it apply to distributed systems?",
      "Describe a blue-green deployment strategy.",
      "How would you design a highly available architecture on AWS?",
    ],
    behavioral: [
      "Tell me about a time you had to troubleshoot a critical production issue.",
      "Describe a situation where you had to work with a difficult team member.",
      "How do you prioritize tasks when everything seems urgent?",
      "Give an example of when you learned from a failure.",
    ],
    scenario: [
      "Your application's response time suddenly increases 10x. Walk me through your debugging process.",
      "A deployment causes database corruption. What steps do you take?",
      "You need to migrate a monolith to microservices. How do you approach this?",
    ],
    hr: [
      "Where do you see yourself in 5 years?",
      "Why are you interested in this role?",
      "What is your biggest professional achievement?",
      "How do you keep up with rapidly changing technology?",
    ],
  },
};

// Expose to global scope
window.AuthAPI = AuthAPI;
window.ResumeAPI = ResumeAPI;
window.JobAPI = JobAPI;
window.InterviewAPI = InterviewAPI;
window.DashboardAPI = DashboardAPI;
window.AIContentAPI = AIContentAPI;
window.MockData = MockData;
window.CONFIG = CONFIG;
