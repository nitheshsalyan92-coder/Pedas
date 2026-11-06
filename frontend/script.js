// ===== CONFIG =====
// Change this to your Flask backend URL when Member 2's server is running
const API_BASE = 'http://localhost:5000';

// ===== DEMO DATA (used when backend is not connected) =====
const DEMO_RESULT = {
  pedestrians_detected: 39,
  vehicles_detected: 0,
  conflicts_detected: 0,
  risk_level: "LOW",
  safety_score: 98,
  alerts: [
    "39 pedestrian(s) observed. No vehicles detected; pedestrian conflict risk is low.",
    "Not enough track history to estimate direction or speed for 1 object(s)."
  ],
  conflicts: [],
  conflict_details: [],
  summary: {
    total_records: 1613,
    duration_seconds: 2.03,
    critical_conflicts: 0,
    warning_conflicts: 0,
    caution_conflicts: 0
  }
};

// ===== STORAGE =====
function saveResult(result) {
  localStorage.setItem('pedas_last_result', JSON.stringify(result));
}
function loadResult() {
  const raw = localStorage.getItem('pedas_last_result');
  return raw ? JSON.parse(raw) : null;
}

// ===== ANALYSIS PAGE =====
let selectedFile = null;

if (document.getElementById('uploadZone')) {
  const fileInput = document.getElementById('fileInput');
  const uploadZone = document.getElementById('uploadZone');

  // Drag & drop
  uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
  uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
  uploadZone.addEventListener('drop', e => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFileSelect(fileInput.files[0]);
  });
}

function handleFileSelect(file) {
  selectedFile = file;
  document.getElementById('uploadZone').style.display = 'none';
  document.getElementById('selectedFile').style.display = 'flex';
  document.getElementById('fileName').textContent = file.name;
  document.getElementById('fileSize').textContent = formatBytes(file.size);
}

function resetUpload() {
  selectedFile = null;
  document.getElementById('uploadZone').style.display = 'block';
  document.getElementById('selectedFile').style.display = 'none';
  document.getElementById('loadingCard').style.display = 'none';
  document.getElementById('errorCard').style.display = 'none';
  document.getElementById('resultsSection').style.display = 'none';
  document.getElementById('uploadCard').style.display = 'block';
  if (document.getElementById('fileInput')) document.getElementById('fileInput').value = '';
}

async function startAnalysis() {
  if (!selectedFile) return;

  document.getElementById('uploadCard').style.display = 'none';
  document.getElementById('loadingCard').style.display = 'block';
  document.getElementById('errorCard').style.display = 'none';
  document.getElementById('resultsSection').style.display = 'none';

  // Animate progress
  animateProgress();

  try {
    const formData = new FormData();
    formData.append('video', selectedFile);

    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error(`Server error: ${response.status}`);
    const result = await response.json();
    saveResult(result);
    showResults(result);
  } catch (err) {
    // Backend not connected — use demo data with a notice
    console.warn('Backend not reachable, using demo data:', err.message);
    await delay(2500); // simulate processing
    const result = { ...DEMO_RESULT, _demo: true };
    saveResult(result);
    showResults(result);
  }
}

function showResults(result) {
  document.getElementById('loadingCard').style.display = 'none';
  document.getElementById('resultsSection').style.display = 'block';

  // Risk banner
  const banner = document.getElementById('riskBanner');
  banner.className = 'risk-banner';
  if (result.risk_level === 'MEDIUM') banner.classList.add('medium');
  if (result.risk_level === 'HIGH') banner.classList.add('high');

  document.getElementById('riskLabel').textContent = result.risk_level + ' RISK';
  document.getElementById('safetyScore').textContent = result.safety_score;

  // Stats
  document.getElementById('pedCount').textContent = result.pedestrians_detected;
  document.getElementById('vehCount').textContent = result.vehicles_detected;
  document.getElementById('conflictCount').textContent = result.conflicts_detected;
  document.getElementById('duration').textContent = result.summary.duration_seconds.toFixed(1) + 's';

  // Alerts
  const alertsList = document.getElementById('alertsList');
  alertsList.innerHTML = '';
  if (result._demo) {
    const li = document.createElement('li');
    li.style.background = '#ede9fe';
    li.style.borderColor = '#a78bfa';
    li.style.color = '#5b21b6';
    li.textContent = '⚡ Demo mode — connect Flask backend to analyze real videos';
    alertsList.appendChild(li);
  }
  (result.alerts || []).forEach(alert => {
    const li = document.createElement('li');
    li.textContent = alert;
    alertsList.appendChild(li);
  });

  // Conflicts
  const conflicts = result.conflicts || result.conflict_details || [];
  if (conflicts.length > 0) {
    document.getElementById('conflictsCard').style.display = 'block';
    const cl = document.getElementById('conflictsList');
    cl.innerHTML = '';
    conflicts.forEach(c => {
      const div = document.createElement('div');
      div.className = 'conflict-item';
      div.textContent = JSON.stringify(c);
      cl.appendChild(div);
    });
  }

  // Summary
  const sg = document.getElementById('summaryGrid');
  sg.innerHTML = '';
  const summaryFields = {
    'Total Records': result.summary.total_records,
    'Duration': result.summary.duration_seconds.toFixed(2) + 's',
    'Critical Conflicts': result.summary.critical_conflicts,
    'Warning Conflicts': result.summary.warning_conflicts,
    'Caution Conflicts': result.summary.caution_conflicts,
  };
  Object.entries(summaryFields).forEach(([k, v]) => {
    const div = document.createElement('div');
    div.className = 'summary-item';
    div.innerHTML = `<div class="summary-key">${k}</div><div class="summary-val">${v}</div>`;
    sg.appendChild(div);
  });
}

// ===== DASHBOARD PAGE =====
if (document.getElementById('dashboardContent')) {
  const result = loadResult() || DEMO_RESULT;
  renderDashboard(result);
}

function renderDashboard(result) {
  // Risk banner
  const banner = document.getElementById('dashRiskBanner');
  banner.className = 'risk-banner';
  if (result.risk_level === 'MEDIUM') banner.classList.add('medium');
  if (result.risk_level === 'HIGH') banner.classList.add('high');
  document.getElementById('dashRiskLabel').textContent = result.risk_level + ' RISK';
  document.getElementById('dashSafetyScore').textContent = result.safety_score;

  // Gauge
  updateGauge(result.safety_score);

  // Metrics
  document.getElementById('dashPed').textContent = result.pedestrians_detected;
  document.getElementById('dashVeh').textContent = result.vehicles_detected;
  document.getElementById('dashConflict').textContent = result.conflicts_detected;
  document.getElementById('dashCritical').textContent = result.summary.critical_conflicts;
  document.getElementById('dashWarning').textContent = result.summary.warning_conflicts;
  document.getElementById('dashDuration').textContent = result.summary.duration_seconds.toFixed(1) + 's';

  // Alerts
  const al = document.getElementById('dashAlertsList');
  al.innerHTML = '';
  (result.alerts || []).forEach(a => {
    const li = document.createElement('li');
    li.textContent = a;
    al.appendChild(li);
  });

  // Bar chart
  const max = Math.max(result.summary.critical_conflicts, result.summary.warning_conflicts, result.summary.caution_conflicts, 1);
  const scale = (v) => Math.max(4, (v / max) * 90) + 'px';
  document.getElementById('barCritical').style.height = scale(result.summary.critical_conflicts);
  document.getElementById('barWarning').style.height = scale(result.summary.warning_conflicts);
  document.getElementById('barCaution').style.height = scale(result.summary.caution_conflicts);

  const hasConflicts = result.summary.critical_conflicts + result.summary.warning_conflicts + result.summary.caution_conflicts > 0;
  document.getElementById('noConflictNote').style.display = hasConflicts ? 'none' : 'block';
}

function updateGauge(score) {
  // Arc length for semicircle ≈ 251
  const arcLen = 251;
  const offset = arcLen - (score / 100) * arcLen;
  const arc = document.getElementById('gaugeArc');
  if (!arc) return;
  arc.setAttribute('stroke-dashoffset', offset);
  arc.setAttribute('stroke', score >= 85 ? '#22c55e' : score >= 60 ? '#eab308' : '#ef4444');
  document.getElementById('gaugeNum').textContent = score;
}

// ===== UTILS =====
function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

function animateProgress() {
  const fill = document.getElementById('progressFill');
  const status = document.getElementById('loadingStatus');
  if (!fill) return;

  const steps = [
    [15, 'Running YOLOv8 detection...'],
    [35, 'ByteTrack: tracking objects across frames...'],
    [60, 'Computing CPA (Closest Point of Approach)...'],
    [80, 'Calculating risk scores and safety metrics...'],
    [95, 'Generating report...'],
  ];

  let i = 0;
  const interval = setInterval(() => {
    if (i >= steps.length) { clearInterval(interval); return; }
    fill.style.width = steps[i][0] + '%';
    status.textContent = steps[i][1];
    i++;
  }, 500);
}
