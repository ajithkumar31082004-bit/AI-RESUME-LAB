/**
 * AI RESUME LAB — Interview Preparation Module
 */

const QUESTION_BANK = {
  'Cloud Engineer': {
    technical: [
      "Explain the difference between containers and virtual machines. When would you use each?",
      "How does Kubernetes handle service discovery and load balancing?",
      "Describe the AWS shared responsibility model. Who is responsible for what?",
      "What is the difference between AWS EC2 Auto Scaling and ELB?",
      "How would you design a highly available, multi-region architecture on AWS?",
      "Explain how Terraform state management works. What are the risks?",
      "What is the difference between blue-green and canary deployments?",
      "How does IAM work in AWS? Explain roles, policies, and users.",
      "What is a VPC and how do you secure resources within it?",
      "Explain the purpose of AWS Lambda and when you'd use it over EC2.",
    ],
    behavioral: [
      "Tell me about a time you had to troubleshoot a critical production outage.",
      "Describe a situation where you had to learn a new technology quickly.",
      "How do you prioritize tasks when multiple urgent issues arise simultaneously?",
      "Tell me about a time you improved a CI/CD pipeline. What was the impact?",
      "Describe a conflict with a team member and how you resolved it.",
    ],
    scenario: [
      "Your application's response time suddenly spikes 10x at 2 AM. Walk me through your incident response.",
      "A deployment to production caused database corruption affecting 20% of users. What steps do you take?",
      "You need to migrate a monolithic application to microservices. How do you approach this?",
      "Your S3 costs increased 300% unexpectedly. How do you investigate and resolve this?",
      "A security audit reveals an open S3 bucket containing customer data. What's your immediate response?",
    ],
    hr: [
      "Why are you interested in this Cloud Engineer role specifically?",
      "Where do you see yourself in 3–5 years?",
      "What is your biggest professional achievement in cloud infrastructure?",
      "How do you stay current with rapidly changing cloud technologies?",
      "What's your approach to documentation and knowledge sharing?",
    ],
  },
  'DevOps Engineer': {
    technical: [
      "Explain GitFlow vs trunk-based development. Which do you prefer and why?",
      "How do you implement zero-downtime deployments?",
      "Describe how you'd set up monitoring for a microservices application.",
      "What is the difference between Prometheus and Datadog? When would you use each?",
      "How does Kubernetes Horizontal Pod Autoscaler work?",
      "Explain how you'd implement secrets management in a CI/CD pipeline.",
      "What is service mesh and when would you use Istio or Linkerd?",
      "How do you handle database migrations in a CI/CD pipeline?",
    ],
    behavioral: [
      "Tell me about a time you automated a manual process. What was the ROI?",
      "Describe your experience with on-call rotations and incident management.",
      "How do you handle technical debt in a fast-moving team?",
      "Tell me about the most challenging infrastructure problem you've solved.",
    ],
    scenario: [
      "Your CI/CD pipeline is taking 45 minutes to run. How do you optimize it?",
      "A container is using 100% CPU in production. How do you diagnose and fix this?",
      "You need to implement zero-trust security for a microservices platform. Where do you start?",
    ],
    hr: [
      "Why DevOps? What drew you to this discipline?",
      "How do you balance developer experience with security requirements?",
      "Describe your ideal engineering culture.",
    ],
  },
  'Backend Developer': {
    technical: [
      "Explain REST vs GraphQL. When would you choose GraphQL?",
      "How do you design an API for high throughput? What are the bottlenecks?",
      "What is N+1 query problem and how do you solve it?",
      "Explain database indexing. When should you use composite indexes?",
      "How does Redis work? What data structures does it support?",
      "What is the CAP theorem and how does it influence system design?",
      "Explain event-driven architecture. What are the trade-offs?",
      "How do you implement rate limiting in an API?",
      "What is database connection pooling and why is it important?",
      "Explain SOLID principles with examples.",
    ],
    behavioral: [
      "Tell me about a complex API you've designed. What decisions did you make?",
      "Describe a performance issue you've debugged and resolved.",
      "How do you approach code reviews?",
    ],
    scenario: [
      "Your database is receiving 10,000 writes per second. How do you scale it?",
      "A user reports that their data is inconsistent. How do you investigate?",
      "You need to add a new feature that requires a breaking API change. How do you handle it?",
    ],
    hr: [
      "What's your preferred programming language and why?",
      "How do you keep your backend skills up to date?",
      "Describe your approach to writing testable code.",
    ],
  },
};

function getQuestions(role) {
  return QUESTION_BANK[role] || QUESTION_BANK['Cloud Engineer'];
}

let mockSession = null;
let mockTimer = null;
let currentQuestionIdx = 0;
let mockQuestions = [];
let scores = [];

function generateQuestions() {
  const role = document.getElementById('int-role')?.value || 'Cloud Engineer';
  const level = document.getElementById('int-level')?.value || 'mid';
  const showTech = document.getElementById('qt-technical')?.checked;
  const showBeh = document.getElementById('qt-behavioral')?.checked;
  const showScen = document.getElementById('qt-scenario')?.checked;
  const showHr = document.getElementById('qt-hr')?.checked;

  const btn = document.getElementById('gen-questions-btn');
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Generating...'; }

  setTimeout(() => {
    const qs = getQuestions(role);

    // Update role label
    const roleLabel = document.getElementById('questions-role-label');
    if (roleLabel) roleLabel.textContent = role;

    // Populate tabs
    if (showTech) populateQuestionList('tc-technical', qs.technical || [], '⚙️', 'Technical');
    if (showBeh) populateQuestionList('tc-behavioral', qs.behavioral || [], '🤝', 'Behavioral');
    if (showScen) populateQuestionList('tc-scenario', qs.scenario || [], '🎭', 'Scenario');
    if (showHr) populateQuestionList('tc-hr', qs.hr || [], '💼', 'HR');

    // Show content
    document.getElementById('questions-placeholder')?.classList.add('hidden');
    document.getElementById('questions-content')?.classList.remove('hidden');

    // Init tabs
    const tabContainer = document.getElementById('question-tabs');
    if (tabContainer) Tabs.init(tabContainer);

    if (btn) { btn.disabled = false; btn.innerHTML = '🤖 Generate Questions'; }
    Toast.success('Questions Ready', `Generated interview questions for ${role}`);
  }, 1000);
}

function populateQuestionList(containerId, questions, icon, category) {
  const el = document.getElementById(containerId);
  if (!el) return;

  el.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:10px;">
      ${questions.map((q, i) => `
        <div style="display:flex;gap:12px;padding:14px;background:var(--bg-glass);border-radius:var(--radius-md);border:var(--border-glass);transition:var(--transition-fast);" onmouseover="this.style.background='var(--bg-glass-hover)'" onmouseout="this.style.background='var(--bg-glass)'">
          <div style="width:28px;height:28px;border-radius:50%;background:var(--gradient-btn);display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;color:white;flex-shrink:0;">${i + 1}</div>
          <div style="flex:1;">
            <p style="font-size:0.875rem;color:var(--text-primary);line-height:1.6;">${q}</p>
            <button onclick="showHint(${i}, '${category}')" style="margin-top:8px;font-size:0.75rem;color:var(--accent-cyan);background:none;border:none;cursor:pointer;padding:0;font-family:inherit;">💡 Show answer tip</button>
          </div>
          <button onclick="addToMock(${i},'${category}')" class="btn btn-ghost btn-sm" style="font-size:0.7rem;flex-shrink:0;align-self:flex-start;" title="Add to mock interview">+</button>
        </div>
      `).join('')}
    </div>
  `;
}

function showHint(idx, category) {
  const hints = {
    Technical: "Be specific. Mention concrete tools, numbers, and trade-offs. Think aloud.",
    Behavioral: "Use the STAR method: Situation → Task → Action → Result. Quantify the result.",
    Scenario: "Show your systematic thinking. Cover: detect → diagnose → mitigate → resolve → post-mortem.",
    HR: "Be authentic. Research the company. Show enthusiasm and cultural fit.",
  };
  Toast.info('💡 Answer Tip', hints[category] || "Be specific and concise.");
}

function addToMock(idx, category) {
  Toast.info('Added', 'Question added to mock interview queue.');
}

function startMockInterview() {
  const role = document.getElementById('int-role')?.value || 'Cloud Engineer';
  const qs = getQuestions(role);
  mockQuestions = [
    ...(qs.technical || []).slice(0, 3),
    ...(qs.behavioral || []).slice(0, 2),
    ...(qs.scenario || []).slice(0, 2),
    ...(qs.hr || []).slice(0, 2),
  ].slice(0, 9);

  scores = [];
  currentQuestionIdx = 0;

  const countEl = document.getElementById('mock-question-count');
  if (countEl) countEl.textContent = mockQuestions.length;

  Modal.open('mock-interview-modal');
  showSection('mock-intro');
}

function startSession() {
  currentQuestionIdx = 0;
  scores = [];
  showSection('mock-session');
  loadQuestion(currentQuestionIdx);
}

function loadQuestion(idx) {
  if (idx >= mockQuestions.length) {
    finishSession();
    return;
  }

  const q = mockQuestions[idx];
  const categories = ['Technical', 'Technical', 'Technical', 'Behavioral', 'Behavioral', 'Scenario', 'Scenario', 'HR', 'HR'];
  const cat = categories[idx] || 'Technical';
  const catColors = { Technical: 'badge-cyan', Behavioral: 'badge-purple', Scenario: 'badge-amber', HR: 'badge-emerald' };

  document.getElementById('mock-question').textContent = q;
  document.getElementById('mock-answer').value = '';
  document.getElementById('mock-progress').textContent = `Question ${idx + 1} of ${mockQuestions.length}`;

  const catBadge = document.getElementById('mock-category-badge');
  if (catBadge) { catBadge.className = `badge ${catColors[cat]}`; catBadge.textContent = cat; }

  // Hide feedback
  const feedback = document.getElementById('mock-feedback');
  if (feedback) feedback.classList.add('hidden');

  // Reset submit button
  const btn = document.getElementById('submit-answer-btn');
  if (btn) { btn.textContent = 'Submit Answer'; btn.onclick = submitMockAnswer; }

  // Start timer (2 minutes)
  startTimer(120);
}

function startTimer(seconds) {
  clearInterval(mockTimer);
  let remaining = seconds;
  const timerEl = document.getElementById('mock-timer');

  const update = () => {
    const m = Math.floor(remaining / 60);
    const s = remaining % 60;
    if (timerEl) {
      timerEl.textContent = `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
      timerEl.style.color = remaining <= 30 ? 'var(--accent-red)' : 'var(--accent-amber)';
    }
    if (remaining <= 0) {
      clearInterval(mockTimer);
      if (timerEl) timerEl.textContent = "Time's up!";
      Toast.warning("Time's Up!", "Moving to next question...");
      setTimeout(() => nextQuestion(), 1500);
    }
    remaining--;
  };

  update();
  mockTimer = setInterval(update, 1000);
}

function submitMockAnswer() {
  const answer = document.getElementById('mock-answer')?.value.trim();
  if (!answer) { Toast.warning('Empty Answer', 'Please type your answer first.'); return; }

  clearInterval(mockTimer);

  // Generate mock AI feedback
  const wordCount = answer.split(' ').length;
  const hasNumbers = /\d+/.test(answer);
  const hasSTAR = /situation|task|action|result|impact|outcome/i.test(answer);

  let score = 50;
  if (wordCount > 50) score += 15;
  if (wordCount > 100) score += 10;
  if (hasNumbers) score += 15;
  if (hasSTAR) score += 10;
  score = Math.min(100, score + Math.floor(Math.random() * 10));
  scores.push(score);

  const feedbackEl = document.getElementById('mock-feedback');
  if (feedbackEl) {
    feedbackEl.classList.remove('hidden');
    const isGood = score >= 75;
    feedbackEl.style.borderColor = isGood ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)';
    feedbackEl.style.background = isGood ? 'rgba(16,185,129,0.08)' : 'rgba(245,158,11,0.08)';
    feedbackEl.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <div style="font-weight:700;font-size:0.875rem;color:${isGood ? 'var(--accent-emerald)' : 'var(--accent-amber)'};">
          ${isGood ? '✅ Good Answer' : '⚠️ Needs Improvement'}
        </div>
        <div style="font-family:var(--font-display);font-weight:700;color:${isGood ? 'var(--accent-emerald)' : 'var(--accent-amber)'};">${score}%</div>
      </div>
      <p style="font-size:0.82rem;color:var(--text-secondary);line-height:1.6;">
        ${!hasNumbers ? '💡 <strong>Tip:</strong> Add specific numbers and metrics to strengthen your answer. ' : ''}
        ${!hasSTAR && currentQuestionIdx >= 3 ? '💡 Use the STAR method to structure your response. ' : ''}
        ${wordCount < 50 ? '💡 Provide more detail — aim for at least 100 words. ' : '✓ Good detail level. '}
        ${isGood ? 'Strong response overall!' : 'Keep practicing to build confidence.'}
      </p>
    `;
  }

  const btn = document.getElementById('submit-answer-btn');
  if (btn) { btn.textContent = 'Next Question →'; btn.onclick = nextQuestion; }
}

function nextQuestion() {
  currentQuestionIdx++;
  loadQuestion(currentQuestionIdx);
}

function skipQuestion() {
  scores.push(0);
  nextQuestion();
}

function finishSession() {
  clearInterval(mockTimer);
  const avgScore = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
  const scoreEl = document.getElementById('mock-final-score');
  if (scoreEl) scoreEl.textContent = avgScore + '%';
  showSection('mock-complete');
  Toast.success('Interview Complete!', `Your average score: ${avgScore}%`);
}

function showSection(id) {
  ['mock-intro', 'mock-session', 'mock-complete'].forEach(s => {
    const el = document.getElementById(s);
    if (el) el.classList.toggle('hidden', s !== id);
  });
}

window.generateQuestions = generateQuestions;
window.showHint = showHint;
window.addToMock = addToMock;
window.startMockInterview = startMockInterview;
window.startSession = startSession;
window.submitMockAnswer = submitMockAnswer;
window.nextQuestion = nextQuestion;
window.skipQuestion = skipQuestion;
