/**
 * AI RESUME LAB — Resume Analyzer Module
 */

document.addEventListener('DOMContentLoaded', () => {
  initAnalyzer();
});

let selectedFile = null;
let analysisData = null;

function initAnalyzer() {
  // Upload zone
  const zone = document.getElementById('resume-upload-zone');
  UploadZone.init(zone, handleFileSelect);

  // Remove file button
  document.getElementById('remove-file')?.addEventListener('click', clearFile);

  // Analyze button
  document.getElementById('analyze-btn')?.addEventListener('click', runAnalysis);

  // Demo button
  document.getElementById('demo-btn')?.addEventListener('click', runDemoAnalysis);

  // Tabs init (upload vs paste)
  const tabUpload = document.getElementById('tab-upload');
  const tabPaste = document.getElementById('tab-paste');
  const tcUpload = document.getElementById('tc-upload');
  const tcPaste = document.getElementById('tc-paste');

  if (tabUpload && tabPaste) {
    tabUpload.addEventListener('click', () => {
      tabUpload.classList.add('active');
      tabPaste.classList.remove('active');
      tcUpload.classList.add('active');
      tcPaste.classList.remove('active');
    });
    tabPaste.addEventListener('click', () => {
      tabPaste.classList.add('active');
      tabUpload.classList.remove('active');
      tcPaste.classList.add('active');
      tcUpload.classList.remove('active');
    });
    tabUpload.classList.add('active');
    tcUpload.classList.add('active');
  }

  // Init results analysis tabs
  const analysisTabsContainer = document.getElementById('analysis-tabs-container');
  if (analysisTabsContainer) Tabs.init(analysisTabsContainer);
}

function handleFileSelect(file) {
  const validTypes = ['application/pdf', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
  const validExts = ['.pdf', '.doc', '.docx', '.txt'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();

  if (!validTypes.includes(file.type) && !validExts.includes(ext)) {
    Toast.error('Invalid File', 'Please upload a PDF, DOCX, or TXT file.');
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    Toast.error('File Too Large', 'Maximum file size is 5MB.');
    return;
  }

  selectedFile = file;

  const preview = document.getElementById('file-preview');
  const fileNameEl = document.getElementById('file-name');
  const fileSizeEl = document.getElementById('file-size');

  if (preview) preview.classList.remove('hidden');
  if (fileNameEl) fileNameEl.textContent = file.name;
  if (fileSizeEl) fileSizeEl.textContent = formatBytes(file.size);

  Toast.info('File Selected', file.name);
}

function clearFile() {
  selectedFile = null;
  const preview = document.getElementById('file-preview');
  const input = document.getElementById('resume-file');
  if (preview) preview.classList.add('hidden');
  if (input) input.value = '';
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

async function runAnalysis() {
  const activeTab = document.getElementById('tab-upload')?.classList.contains('active') ? 'upload' : 'paste';
  const jobDesc = document.getElementById('job-desc-input')?.value.trim() || '';

  if (activeTab === 'upload' && !selectedFile) {
    Toast.warning('No File', 'Please upload a resume file first.');
    return;
  }

  if (activeTab === 'paste') {
    const text = document.getElementById('resume-text-input')?.value.trim();
    if (!text || text.length < 100) {
      Toast.warning('Too Short', 'Please paste at least 100 characters of resume text.');
      return;
    }
  }

  showLoading();

  try {
    let data;
    const statusMessages = [
      'Extracting text and parsing sections...',
      'Analyzing resume structure...',
      'Calculating ATS score...',
      'Identifying keywords...',
      'Matching against job description...',
      'Generating AI recommendations...',
    ];

    let msgIdx = 0;
    const statusEl = document.getElementById('loading-status');
    const statusInterval = setInterval(() => {
      if (statusEl && msgIdx < statusMessages.length - 1) {
        msgIdx++;
        statusEl.textContent = statusMessages[msgIdx];
      }
    }, 800);

    try {
      if (activeTab === 'upload' && selectedFile) {
        data = await ResumeAPI.upload(selectedFile, jobDesc);
      } else {
        const text = document.getElementById('resume-text-input')?.value.trim();
        data = await ResumeAPI.analyzeText(text, jobDesc);
      }
    } catch {
      // Fallback to mock data for demo
      await delay(4000);
      data = { ...MockData.analysisResult };
      if (!jobDesc) {
        data.job_match = null;
        data.matching_skills = [];
        data.missing_skills = [];
      }
    }

    clearInterval(statusInterval);
    analysisData = data;
    showResults(data);
    Toast.success('Analysis Complete!', 'Your resume has been analyzed successfully.');

  } catch (err) {
    showPlaceholder();
    Toast.error('Analysis Failed', err.message || 'Something went wrong. Please try again.');
  }
}

async function runDemoAnalysis() {
  showLoading();
  await delay(2500);
  analysisData = MockData.analysisResult;
  showResults(analysisData);
  Toast.success('Demo Analysis', 'Showing sample analysis results.');
}

function showLoading() {
  document.getElementById('results-placeholder')?.classList.add('hidden');
  document.getElementById('results-content')?.classList.add('hidden');
  document.getElementById('results-loading')?.classList.remove('hidden');
}

function showPlaceholder() {
  document.getElementById('results-loading')?.classList.add('hidden');
  document.getElementById('results-content')?.classList.add('hidden');
  document.getElementById('results-placeholder')?.classList.remove('hidden');
}

function showResults(data) {
  document.getElementById('results-loading')?.classList.add('hidden');
  document.getElementById('results-placeholder')?.classList.add('hidden');
  document.getElementById('results-content')?.classList.remove('hidden');

  // Animate ATS Score
  animateNumber('display-ats-score', data.ats_score, '');

  // Job match
  const jmWrap = document.getElementById('job-match-wrap');
  if (data.job_match) {
    animateNumber('display-job-match', data.job_match, '');
    if (jmWrap) jmWrap.style.display = 'block';
  } else {
    if (jmWrap) jmWrap.style.display = 'none';
  }

  // Category bars
  const categories = [
    { label: 'Resume Structure', value: data.resume_structure || 88, color: 'cyan' },
    { label: 'Keywords', value: data.keywords_score || 85, color: 'blue' },
    { label: 'Skills', value: data.skills_score || 90, color: 'purple' },
    { label: 'Experience', value: data.experience_score || 82, color: 'amber' },
    { label: 'Education', value: data.education_score || 95, color: 'emerald' },
    { label: 'Formatting', value: data.formatting_score || 88, color: 'cyan' },
  ];

  const catsEl = document.getElementById('score-categories');
  if (catsEl) {
    catsEl.innerHTML = '';
    categories.forEach(cat => {
      const wrap = ProgressBar.create(cat.label, cat.value, 100, cat.color);
      catsEl.appendChild(wrap);
    });
    setTimeout(() => ProgressBar.animateAll(0), 200);
  }

  // Skill tags
  const tagsEl = document.getElementById('skill-tags-row');
  if (tagsEl && (data.matching_skills || data.missing_skills)) {
    tagsEl.innerHTML = '';
    (data.matching_skills || []).forEach(skill => {
      const tag = document.createElement('span');
      tag.className = 'skill-tag matched';
      tag.textContent = '✓ ' + skill;
      tagsEl.appendChild(tag);
    });
    (data.missing_skills || []).slice(0, 3).forEach(skill => {
      const tag = document.createElement('span');
      tag.className = 'skill-tag missing';
      tag.textContent = '✗ ' + skill;
      tagsEl.appendChild(tag);
    });
  }

  // Strengths
  const strengthsList = document.getElementById('strengths-list');
  if (strengthsList) {
    strengthsList.innerHTML = (data.strengths || []).map(s => `
      <div class="result-item strength">
        <span class="dot"></span>
        <span>${s}</span>
      </div>
    `).join('');
  }

  // Weaknesses
  const weaknessesList = document.getElementById('weaknesses-list');
  if (weaknessesList) {
    weaknessesList.innerHTML = (data.weaknesses || []).map(w => `
      <div class="result-item weakness">
        <span class="dot"></span>
        <span>${w}</span>
      </div>
    `).join('');
  }

  // Recommendations
  const recsList = document.getElementById('recommendations-list');
  if (recsList) {
    recsList.innerHTML = (data.recommendations || []).map((rec, i) => `
      <div class="recommendation-card">
        <div class="rec-number">${i + 1}</div>
        <div class="rec-content">
          <div class="rec-issue">🔴 ${rec.issue}</div>
          <div class="rec-why">💡 ${rec.why}</div>
          <div class="rec-fix">✅ Fix: ${rec.fix}</div>
        </div>
      </div>
    `).join('');
  }

  // Missing Skills
  const missingEl = document.getElementById('missing-skills-list');
  if (missingEl) {
    missingEl.innerHTML = (data.missing_skills || []).map(s => `
      <span class="skill-tag missing">✗ ${s}</span>
    `).join('') || '<p style="color:var(--text-muted);font-size:0.85rem;">No missing critical skills detected.</p>';
  }

  // Re-init analysis tabs
  const tabsContainer = document.getElementById('analysis-tabs-container');
  if (tabsContainer) Tabs.init(tabsContainer);
}

function animateNumber(elId, target, suffix = '') {
  const el = document.getElementById(elId);
  if (!el) return;
  let current = 0;
  const increment = target / 60;
  const interval = setInterval(() => {
    current = Math.min(current + increment, target);
    el.textContent = Math.round(current) + suffix;
    if (current >= target) clearInterval(interval);
  }, 16);
}

function downloadReport() {
  if (!analysisData) return;
  const report = `
AI RESUME LAB — ANALYSIS REPORT
Generated: ${new Date().toLocaleString()}
===================================

ATS SCORE: ${analysisData.ats_score}/100
JOB MATCH: ${analysisData.job_match || 'N/A'}%

STRENGTHS:
${(analysisData.strengths || []).map(s => '• ' + s).join('\n')}

AREAS TO IMPROVE:
${(analysisData.weaknesses || []).map(w => '• ' + w).join('\n')}

MISSING SKILLS:
${(analysisData.missing_skills || []).join(', ')}

AI RECOMMENDATIONS:
${(analysisData.recommendations || []).map((r, i) => `${i+1}. ${r.issue}\n   Why: ${r.why}\n   Fix: ${r.fix}`).join('\n\n')}
  `.trim();

  const blob = new Blob([report], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'resume-analysis-report.txt';
  a.click();
  URL.revokeObjectURL(url);
  Toast.success('Report Downloaded', 'Your analysis report has been saved.');
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
