/**
 * AI RESUME LAB — Job Matcher & Skill Gap Module
 */

const ROADMAPS = {
  cloud_engineer: {
    name: 'Cloud Engineer',
    steps: [
      { label: 'Linux', icon: '🐧', status: 'completed', desc: 'Master Linux fundamentals, shell scripting, file systems' },
      { label: 'Networking', icon: '🌐', status: 'completed', desc: 'TCP/IP, DNS, HTTP, VPNs, firewalls' },
      { label: 'Python', icon: '🐍', status: 'completed', desc: 'Scripting, automation, Boto3 for AWS' },
      { label: 'AWS Core', icon: '☁️', status: 'current', desc: 'EC2, S3, VPC, IAM, RDS, Lambda' },
      { label: 'Docker', icon: '🐳', status: 'locked', desc: 'Containers, Dockerfile, Docker Compose' },
      { label: 'Terraform', icon: '⚙️', status: 'locked', desc: 'Infrastructure as Code, state management' },
      { label: 'Kubernetes', icon: '☸️', status: 'locked', desc: 'Orchestration, Helm, EKS, service mesh' },
      { label: 'CI/CD', icon: '🔄', status: 'locked', desc: 'Jenkins, GitHub Actions, ArgoCD' },
    ],
  },
  devops_engineer: {
    name: 'DevOps Engineer',
    steps: [
      { label: 'Linux', icon: '🐧', status: 'completed', desc: 'OS fundamentals, scripting, package management' },
      { label: 'Git', icon: '📝', status: 'completed', desc: 'Version control, branching, GitFlow' },
      { label: 'Docker', icon: '🐳', status: 'completed', desc: 'Containerization, multi-stage builds' },
      { label: 'Kubernetes', icon: '☸️', status: 'current', desc: 'Pod management, services, Ingress, RBAC' },
      { label: 'CI/CD', icon: '🔄', status: 'locked', desc: 'Jenkins, GitHub Actions, pipeline as code' },
      { label: 'Monitoring', icon: '📊', status: 'locked', desc: 'Prometheus, Grafana, ELK Stack' },
      { label: 'Terraform', icon: '⚙️', status: 'locked', desc: 'IaC, modules, workspaces, state' },
      { label: 'Security', icon: '🔒', status: 'locked', desc: 'DevSecOps, SAST, DAST, secrets management' },
    ],
  },
  backend_developer: {
    name: 'Backend Developer',
    steps: [
      { label: 'Python/Java', icon: '💻', status: 'completed', desc: 'Strong OOP, design patterns, SOLID principles' },
      { label: 'REST APIs', icon: '🔌', status: 'completed', desc: 'HTTP methods, status codes, API design' },
      { label: 'Databases', icon: '🗄️', status: 'completed', desc: 'SQL, indexing, transactions, ORM' },
      { label: 'Caching', icon: '⚡', status: 'current', desc: 'Redis, Memcached, cache strategies' },
      { label: 'Message Queues', icon: '📨', status: 'locked', desc: 'RabbitMQ, Kafka, async processing' },
      { label: 'Microservices', icon: '🔧', status: 'locked', desc: 'Service decomposition, API Gateway' },
      { label: 'Docker/K8s', icon: '🐳', status: 'locked', desc: 'Containerize and deploy services' },
      { label: 'System Design', icon: '🏗️', status: 'locked', desc: 'Scalability, CAP theorem, distributed systems' },
    ],
  },
  data_scientist: {
    name: 'Data Scientist',
    steps: [
      { label: 'Python', icon: '🐍', status: 'completed', desc: 'NumPy, Pandas, Matplotlib, Scikit-learn' },
      { label: 'Statistics', icon: '📊', status: 'completed', desc: 'Probability, hypothesis testing, regression' },
      { label: 'ML Basics', icon: '🤖', status: 'current', desc: 'Supervised, unsupervised, model evaluation' },
      { label: 'Deep Learning', icon: '🧠', status: 'locked', desc: 'TensorFlow, PyTorch, neural networks' },
      { label: 'NLP', icon: '💬', status: 'locked', desc: 'Text processing, transformers, BERT' },
      { label: 'Big Data', icon: '📦', status: 'locked', desc: 'Spark, Hadoop, data pipelines' },
      { label: 'MLOps', icon: '⚙️', status: 'locked', desc: 'Model deployment, monitoring, MLflow' },
    ],
  },
};

const DEFAULT_ROADMAP = ROADMAPS.cloud_engineer;

document.addEventListener('DOMContentLoaded', () => {
  // Skills preview chips
  const skillsInput = document.getElementById('current-skills');
  if (skillsInput) {
    skillsInput.addEventListener('input', updateSkillsPreview);
    skillsInput.value = 'Python, AWS, Docker, SQL, Git, Linux, REST APIs, Agile';
    updateSkillsPreview();
  }
});

function updateSkillsPreview() {
  const input = document.getElementById('current-skills');
  const preview = document.getElementById('skills-preview');
  if (!input || !preview) return;

  const skills = input.value.split(',').map(s => s.trim()).filter(Boolean);
  preview.innerHTML = skills.slice(0, 8).map(skill => `
    <span class="skill-tag neutral">${skill}</span>
  `).join('') + (skills.length > 8 ? `<span class="skill-tag neutral">+${skills.length - 8} more</span>` : '');
}

async function runMatching() {
  const jobDesc = document.getElementById('job-desc-match')?.value.trim();
  const skills = document.getElementById('current-skills')?.value.trim();
  const targetRole = document.getElementById('target-role')?.value;

  if (!jobDesc && !targetRole) {
    Toast.warning('Missing Input', 'Please paste a job description or select a target role.');
    return;
  }

  const btn = document.getElementById('match-btn');
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Analyzing...'; }

  try {
    let data;
    try {
      const userSkills = skills ? skills.split(',').map(s => s.trim()) : [];
      data = await JobAPI.analyzeSkillGap(userSkills, targetRole);
    } catch {
      // Mock response
      await delay(1800);
      data = generateMockMatch(jobDesc, skills);
    }

    showMatchResults(data, targetRole);
    Toast.success('Analysis Complete', 'Job match analysis ready!');
  } catch (err) {
    Toast.error('Error', err.message);
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = '🎯 Analyze Job Match & Skills'; }
  }
}

function generateMockMatch(jobDesc = '', skills = '') {
  const jd = (jobDesc + ' ' + skills).toLowerCase();
  const userSkills = skills ? skills.split(',').map(s => s.trim().toLowerCase()) : ['python', 'aws', 'docker', 'sql', 'git'];

  const allJobSkills = ['Python', 'AWS', 'Docker', 'Kubernetes', 'Terraform', 'SQL', 'Git', 'Linux', 'Jenkins', 'Grafana', 'Prometheus', 'CI/CD', 'REST APIs', 'Agile'];
  const matching = allJobSkills.filter(s => userSkills.some(u => u.includes(s.toLowerCase()) || s.toLowerCase().includes(u)));
  const missing = allJobSkills.filter(s => !matching.includes(s));
  const score = Math.round(40 + (matching.length / allJobSkills.length) * 60);

  return {
    match_score: score,
    matching_skills: matching,
    missing_skills: missing,
    recommended_skills: missing.slice(0, 5),
  };
}

function showMatchResults(data, targetRole) {
  document.getElementById('match-placeholder')?.classList.add('hidden');
  document.getElementById('match-content')?.classList.remove('hidden');
  document.getElementById('roadmap-section')?.classList.remove('hidden');

  // Animate match score
  const scoreEl = document.getElementById('match-score-display');
  if (scoreEl) animateNum(scoreEl, data.match_score || 72);

  // Verdict badge
  const verdictEl = document.getElementById('match-verdict');
  if (verdictEl) {
    const score = data.match_score || 72;
    const verdict = score >= 85 ? { label: '🟢 Excellent Match', bg: 'rgba(16,185,129,0.15)', color: '#10b981' }
      : score >= 70 ? { label: '🟡 Good Match', bg: 'rgba(245,158,11,0.15)', color: '#f59e0b' }
      : { label: '🔴 Needs Improvement', bg: 'rgba(239,68,68,0.15)', color: '#ef4444' };
    verdictEl.style.background = verdict.bg;
    verdictEl.style.color = verdict.color;
    verdictEl.textContent = verdict.label;
  }

  // Matching skills
  const matchingEl = document.getElementById('matching-skills-display');
  if (matchingEl) {
    matchingEl.innerHTML = (data.matching_skills || []).map(s => `<span class="skill-tag matched">✓ ${s}</span>`).join('') ||
      '<span style="color:var(--text-muted);font-size:0.85rem;">No strong matches found.</span>';
  }

  // Missing skills
  const missingEl = document.getElementById('missing-skills-display');
  if (missingEl) {
    missingEl.innerHTML = (data.missing_skills || []).map(s => `<span class="skill-tag missing">✗ ${s}</span>`).join('') ||
      '<span style="color:var(--accent-emerald);font-size:0.85rem;">🎉 No critical skills missing!</span>';
  }

  // Recommended skills
  const recEl = document.getElementById('recommended-skills-display');
  if (recEl) {
    recEl.innerHTML = (data.recommended_skills || []).map(s => `<span class="skill-tag recommended">⭐ ${s}</span>`).join('') || '';
  }

  // Render roadmap
  renderRoadmap(targetRole || 'cloud_engineer');
}

function renderRoadmap(role) {
  const roadmap = ROADMAPS[role] || DEFAULT_ROADMAP;
  const nameEl = document.getElementById('roadmap-role-name');
  if (nameEl) nameEl.textContent = roadmap.name;

  // Visual roadmap
  const visual = document.getElementById('roadmap-visual');
  if (visual) {
    visual.innerHTML = roadmap.steps.map((step, i) => `
      <div style="display:flex;align-items:flex-start;gap:0;">
        <div style="display:flex;flex-direction:column;align-items:center;gap:8px;min-width:80px;">
          <div class="roadmap-node ${step.status}" title="${step.label}">
            ${step.icon}
          </div>
          <div class="roadmap-label">${step.label}</div>
        </div>
        ${i < roadmap.steps.length - 1 ? `
          <div class="roadmap-connector" style="width:40px;display:flex;align-items:center;padding-bottom:30px;">
            <div style="width:100%;height:2px;background:linear-gradient(90deg,var(--accent-cyan),var(--accent-purple));opacity:${step.status === 'completed' ? '0.8' : '0.3'};"></div>
          </div>
        ` : ''}
      </div>
    `).join('');
  }

  // Steps detail cards
  const stepsEl = document.getElementById('roadmap-steps');
  if (stepsEl) {
    stepsEl.innerHTML = roadmap.steps.map(step => `
      <div class="card card-sm" style="border-color:${
        step.status === 'completed' ? 'rgba(16,185,129,0.3)' :
        step.status === 'current' ? 'rgba(6,182,212,0.3)' : 'rgba(255,255,255,0.06)'};">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
          <span style="font-size:1.2rem;">${step.icon}</span>
          <div>
            <div style="font-size:0.875rem;font-weight:700;color:var(--text-primary);">${step.label}</div>
            <span class="badge ${step.status === 'completed' ? 'badge-emerald' : step.status === 'current' ? 'badge-cyan' : 'badge-purple'}">${
              step.status === 'completed' ? '✓ Completed' : step.status === 'current' ? '▶ In Progress' : '🔒 Next'
            }</span>
          </div>
        </div>
        <p style="font-size:0.78rem;color:var(--text-secondary);">${step.desc}</p>
      </div>
    `).join('');
  }
}

async function loadDemoMatch() {
  document.getElementById('job-desc-match').value = `We are looking for a Cloud Engineer with 3+ years of experience. 

Requirements:
- Proficient in AWS (EC2, S3, Lambda, VPC, IAM)
- Experience with Kubernetes and Docker
- Infrastructure as Code using Terraform
- CI/CD pipeline experience (Jenkins, GitHub Actions)
- Strong Linux/Unix skills
- Python scripting for automation
- Monitoring with Grafana/Prometheus
- Knowledge of networking and security`;

  document.getElementById('current-skills').value = 'Python, AWS, Docker, SQL, Git, Linux, REST APIs, Agile, Bash scripting';
  document.getElementById('target-role').value = 'cloud_engineer';
  updateSkillsPreview();
  await runMatching();
}

function animateNum(el, target) {
  let current = 0;
  const step = target / 50;
  const interval = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = Math.round(current);
    if (current >= target) clearInterval(interval);
  }, 20);
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

window.runMatching = runMatching;
window.loadDemoMatch = loadDemoMatch;
