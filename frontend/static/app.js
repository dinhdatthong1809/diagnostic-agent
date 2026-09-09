const API = "/api";
let currentPatientId = null;
let bpChart = null;
let glucoseChart = null;

// ---------- Tabs ----------
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    if (btn.dataset.tab === "history") loadHistory();
  });
});

// ---------- Patients ----------
async function loadPatients() {
  const res = await fetch(`${API}/patients/`);
  const patients = await res.json();
  const select = document.getElementById("patientSelect");
  select.innerHTML = "";
  if (patients.length === 0) {
    select.innerHTML = '<option value="">(Chưa có bệnh nhân)</option>';
    currentPatientId = null;
    return;
  }
  patients.forEach((p) => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = `${p.name} (${p.age ?? "?"} tuổi)`;
    select.appendChild(opt);
  });
  currentPatientId = Number(select.value);
  await loadChatHistory();
}

document.getElementById("patientSelect").addEventListener("change", async (e) => {
  currentPatientId = Number(e.target.value);
  await loadChatHistory();
});

document.getElementById("newPatientBtn").addEventListener("click", () => {
  document.getElementById("newPatientForm").classList.toggle("hidden");
});

document.getElementById("saveNewPatientBtn").addEventListener("click", async () => {
  const payload = {
    name: document.getElementById("npName").value.trim(),
    age: Number(document.getElementById("npAge").value) || null,
    gender: document.getElementById("npGender").value || null,
    address: document.getElementById("npAddress").value || null,
    conditions: document.getElementById("npConditions").value || null,
  };
  if (!payload.name) {
    alert("Vui lòng nhập họ tên bệnh nhân.");
    return;
  }
  await fetch(`${API}/patients/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  document.getElementById("newPatientForm").classList.add("hidden");
  ["npName", "npAge", "npAddress", "npConditions"].forEach((id) => (document.getElementById(id).value = ""));
  await loadPatients();
});

// ---------- Chat ----------
function appendMessage(role, content) {
  const win = document.getElementById("chatWindow");
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = content;
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}

async function loadChatHistory() {
  const win = document.getElementById("chatWindow");
  win.innerHTML = "";
  if (!currentPatientId) return;
  const res = await fetch(`${API}/chat/${currentPatientId}`);
  const messages = await res.json();
  messages.forEach((m) => appendMessage(m.role, m.content));
}

document.getElementById("chatForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!currentPatientId) {
    alert("Vui lòng chọn hoặc tạo bệnh nhân trước.");
    return;
  }
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;
  appendMessage("user", message);
  input.value = "";
  appendMessage("assistant", "Đang phân tích...");

  const res = await fetch(`${API}/chat/${currentPatientId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  const data = await res.json();
  const win = document.getElementById("chatWindow");
  win.lastChild.remove();
  appendMessage("assistant", data.answer);
});

// ---------- Vitals ----------
document.getElementById("submitVitalBtn").addEventListener("click", async () => {
  if (!currentPatientId) {
    alert("Vui lòng chọn hoặc tạo bệnh nhân trước.");
    return;
  }
  const payload = {
    patient_id: currentPatientId,
    systolic: numOrNull("vSystolic"),
    diastolic: numOrNull("vDiastolic"),
    glucose: numOrNull("vGlucose"),
    heart_rate: numOrNull("vHeartRate"),
    weight: numOrNull("vWeight"),
  };
  const res = await fetch(`${API}/vitals/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  renderAlerts(data.alerts);
  ["vSystolic", "vDiastolic", "vGlucose", "vHeartRate", "vWeight"].forEach((id) => (document.getElementById(id).value = ""));
});

function numOrNull(id) {
  const v = document.getElementById(id).value;
  return v === "" ? null : Number(v);
}

function renderAlerts(alerts) {
  const container = document.getElementById("vitalAlerts");
  container.innerHTML = "";
  if (!alerts || alerts.length === 0) {
    container.innerHTML = '<div class="alert normal">Đã lưu chỉ số. Không phát hiện bất thường.</div>';
    return;
  }
  alerts.forEach((a) => {
    const div = document.createElement("div");
    div.className = `alert ${a.severity}`;
    div.textContent = a.message;
    container.appendChild(div);
  });
}

// ---------- History ----------
async function loadHistory() {
  if (!currentPatientId) return;
  const res = await fetch(`${API}/vitals/${currentPatientId}`);
  const records = await res.json();

  const labels = records.map((r) => new Date(r.measured_at).toLocaleString("vi-VN"));
  const systolic = records.map((r) => r.systolic);
  const diastolic = records.map((r) => r.diastolic);
  const glucose = records.map((r) => r.glucose);

  if (bpChart) bpChart.destroy();
  bpChart = new Chart(document.getElementById("bpChart"), {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Tâm thu", data: systolic, borderColor: "#c0392b", tension: 0.2 },
        { label: "Tâm trương", data: diastolic, borderColor: "#2874a6", tension: 0.2 },
      ],
    },
    options: { responsive: true, plugins: { title: { display: true, text: "Huyết áp theo thời gian (mmHg)" } } },
  });

  if (glucoseChart) glucoseChart.destroy();
  glucoseChart = new Chart(document.getElementById("glucoseChart"), {
    type: "line",
    data: {
      labels,
      datasets: [{ label: "Đường huyết (mg/dL)", data: glucose, borderColor: "#d68910", tension: 0.2 }],
    },
    options: { responsive: true, plugins: { title: { display: true, text: "Đường huyết theo thời gian" } } },
  });

  const tbody = document.querySelector("#historyTable tbody");
  tbody.innerHTML = "";
  [...records].reverse().forEach((r) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${new Date(r.measured_at).toLocaleString("vi-VN")}</td>
      <td>${r.systolic ?? "-"}/${r.diastolic ?? "-"}</td>
      <td>${r.glucose ?? "-"}</td>
      <td>${r.heart_rate ?? "-"}</td>
      <td>${r.severity}</td>`;
    tbody.appendChild(tr);
  });
}

loadPatients();
