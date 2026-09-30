// -----------------------------------------------------------------------------
// SweepFood AI — Frontend Application Logic (Tailwind CSS v4 + Smart Input)
// -----------------------------------------------------------------------------

let currentPantry = [];
let presetsList = [];
let activePresetId = null;
let selectedItemCode = null;

// Smart Input State
let ocrDetectedItems = [];
let asrDetectedItems = [];
let speechRecognizer = null;
let isRecordingSpeech = false;

// DOM Elements: Recommendation
const presetsContainer = document.getElementById("presetsContainer");
const pantryCounter = document.getElementById("pantryCounter");
const pantryItemsList = document.getElementById("pantryItemsList");
const btnClearPantry = document.getElementById("btnClearPantry");
const inputIngredient = document.getElementById("inputIngredient");
const inputQty = document.getElementById("inputQty");
const selectExpiry = document.getElementById("selectExpiry");
const btnAddItem = document.getElementById("btnAddItem");
const autoDropdown = document.getElementById("autoDropdown");

const sliderTime = document.getElementById("sliderTime");
const timeDisplay = document.getElementById("timeDisplay");
const sliderServings = document.getElementById("sliderServings");
const servingsDisplay = document.getElementById("servingsDisplay");

const btnRecommend = document.getElementById("btnRecommend");
const loadingState = document.getElementById("loadingState");
const emptyState = document.getElementById("emptyState");
const recommendationsList = document.getElementById("recommendationsList");
const latencyStat = document.getElementById("latencyStat");

// DOM Elements: OCR
const ocrFileInput = document.getElementById("ocrFileInput");
const ocrRawText = document.getElementById("ocrRawText");
const ocrStatusMsg = document.getElementById("ocrStatusMsg");
const ocrDetectedCount = document.getElementById("ocrDetectedCount");
const ocrItemsContainer = document.getElementById("ocrItemsContainer");
const btnPushOcrToFridge = document.getElementById("btnPushOcrToFridge");

// DOM Elements: ASR
const btnMicRecord = document.getElementById("btnMicRecord");
const micStatusText = document.getElementById("micStatusText");
const asrTranscript = document.getElementById("asrTranscript");
const asrStatusMsg = document.getElementById("asrStatusMsg");
const asrDetectedCount = document.getElementById("asrDetectedCount");
const asrItemsContainer = document.getElementById("asrItemsContainer");
const btnPushAsrToFridge = document.getElementById("btnPushAsrToFridge");


// -----------------------------------------------------------------------------
// Initialization
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  checkSystemGpuStatus();
  // Start with empty, clean pantry
  currentPantry = [];
  updatePantryUI();
});

async function checkSystemGpuStatus() {
  try {
    const res = await fetch("/api/system/status");
    const data = await res.json();
    const badge = document.getElementById("gpuStatusBadge");
    const text = document.getElementById("gpuStatusText");
    if (badge && text) {
      if (data.cuda_available) {
        badge.className = "flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-100/90 text-emerald-950 border border-emerald-300/80 shadow-xs";
        text.innerHTML = `🟢 <strong>${data.device_name}</strong> (VRAM: ${data.vram_allocated_mb}MB)`;
        badge.title = `XGBoost: ${data.xgb_device.toUpperCase()} | OCR: ${data.ocr_device} | Không độ trễ khởi động!`;
      } else {
        text.textContent = `⚡ XGBoost CPU Inference`;
      }
    }
  } catch (err) {
    console.debug("Status check silent fallback:", err);
  }
}

function setupEventListeners() {
  // Sliders
  sliderTime.addEventListener("input", (e) => {
    timeDisplay.textContent = `${e.target.value} phút`;
  });

  sliderServings.addEventListener("input", (e) => {
    servingsDisplay.textContent = `${e.target.value} người`;
  });

  // Autocomplete
  let debounceTimer = null;
  inputIngredient.addEventListener("input", (e) => {
    selectedItemCode = null;
    clearTimeout(debounceTimer);
    const q = e.target.value.trim();
    if (q.length < 1) {
      autoDropdown.classList.add("hidden");
      return;
    }
    debounceTimer = setTimeout(() => searchAutocomplete(q), 200);
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest("#inputIngredient") && !e.target.closest("#autoDropdown")) {
      autoDropdown.classList.add("hidden");
    }
  });

  // Add Item Button
  btnAddItem.addEventListener("click", () => {
    const name = inputIngredient.value.trim();
    const qty = parseFloat(inputQty.value) || 200;
    const hours = parseFloat(selectExpiry.value) || 48;

    if (!name) {
      alert("Vui lòng nhập tên nguyên liệu!");
      inputIngredient.focus();
      return;
    }

    addItemToPantry(name, qty, hours, selectedItemCode);
    inputIngredient.value = "";
    selectedItemCode = null;
    inputIngredient.focus();
  });

  inputIngredient.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      btnAddItem.click();
    }
  });

  // Clear Pantry
  btnClearPantry.addEventListener("click", () => {
    if (currentPantry.length === 0) return;
    if (confirm("Bạn có chắc chắn muốn xóa toàn bộ nguyên liệu trong tủ lạnh?")) {
      currentPantry = [];
      activePresetId = null;
      updatePantryUI();
      emptyState.classList.remove("hidden");
      recommendationsList.classList.add("hidden");
    }
  });
}


// -----------------------------------------------------------------------------
// Tab Navigation (Recommendation • Smart OCR • Smart ASR)
// -----------------------------------------------------------------------------
function switchAppTab(tab) {
  const tabs = ["recommend", "ocr", "asr"];
  const navBtns = {
    recommend: document.getElementById("tabNavRecommend"),
    ocr: document.getElementById("tabNavOcr"),
    asr: document.getElementById("tabNavAsr")
  };
  const contents = {
    recommend: document.getElementById("tabContentRecommend"),
    ocr: document.getElementById("tabContentOcr"),
    asr: document.getElementById("tabContentAsr")
  };

  tabs.forEach(t => {
    if (t === tab) {
      contents[t].classList.remove("hidden");
      navBtns[t].classList.add("bg-white", "text-teal-800", "shadow-xs", "font-bold");
      navBtns[t].classList.remove("text-slate-600");
    } else {
      contents[t].classList.add("hidden");
      navBtns[t].classList.remove("bg-white", "text-teal-800", "shadow-xs", "font-bold");
      navBtns[t].classList.add("text-slate-600");
    }
  });
}


// -----------------------------------------------------------------------------
// Presets (Optional Helper)
// -----------------------------------------------------------------------------
function renderPresets() {
  if (presetsContainer && presetsList.length > 0) {
    presetsContainer.innerHTML = "";
  }
}



// -----------------------------------------------------------------------------
// Autocomplete
// -----------------------------------------------------------------------------
async function searchAutocomplete(q) {
  try {
    const res = await fetch(`/api/autocomplete?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    const list = data.results || [];
    if (list.length === 0) {
      autoDropdown.classList.add("hidden");
      return;
    }
    autoDropdown.innerHTML = list.map(item => `
      <div onclick="chooseAutocomplete('${item.name.replace(/'/g, "\\'")}', '${item.code}')"
        class="px-3 py-2 text-xs text-slate-800 hover:bg-teal-50 hover:text-teal-800 flex items-center justify-between cursor-pointer border-b border-slate-100 last:border-0">
        <span class="font-medium">${item.name}</span>
        <span class="text-[10px] font-mono text-slate-400">#${item.code}</span>
      </div>
    `).join("");
    autoDropdown.classList.remove("hidden");
  } catch (err) {
    console.error("Autocomplete error:", err);
  }
}

function chooseAutocomplete(name, code) {
  inputIngredient.value = name;
  selectedItemCode = code;
  autoDropdown.classList.add("hidden");
}


// -----------------------------------------------------------------------------
// Pantry Management
// -----------------------------------------------------------------------------
function addItemToPantry(name, quantity_g, hours_to_expire, code = null) {
  const existing = currentPantry.find(it => it.name.toLowerCase() === name.toLowerCase());
  if (existing) {
    existing.quantity_g += quantity_g;
    if (code && !existing.code) existing.code = code;
  } else {
    currentPantry.push({
      name: name,
      code: code || null,
      quantity_g: quantity_g,
      hours_to_expire: hours_to_expire,
      is_staple: hours_to_expire >= 300
    });
  }
  activePresetId = null;
  renderPresets();
  updatePantryUI();
}

function removeItem(index) {
  currentPantry.splice(index, 1);
  activePresetId = null;
  renderPresets();
  updatePantryUI();
}

function updatePantryUI() {
  pantryCounter.textContent = `${currentPantry.length} nguyên liệu đang có`;

  if (currentPantry.length === 0) {
    pantryItemsList.innerHTML = `<p class="text-xs text-slate-400 text-center py-6">Tủ lạnh đang trống. Hãy thêm nguyên liệu để bắt đầu!</p>`;
    return;
  }

  pantryItemsList.innerHTML = currentPantry.map((it, idx) => {
    const isUrgent = it.hours_to_expire <= 24 && !it.is_staple;
    return `
      <div class="flex items-center justify-between p-2.5 rounded-lg border text-xs transition-all ${
        isUrgent
          ? 'bg-rose-50/70 border-rose-200 text-rose-900'
          : 'bg-white border-slate-200 text-slate-800'
      }">
        <div class="flex items-center gap-2">
          <span class="font-bold">${it.name}</span>
          <span class="text-[11px] text-slate-500 font-mono bg-slate-100 px-1.5 py-0.5 rounded">${it.quantity_g}g</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${
            isUrgent ? 'bg-rose-200 text-rose-800 animate-pulse' : 'bg-slate-100 text-slate-600'
          }">
            ${isUrgent ? `🔥 < ${it.hours_to_expire}h` : `${it.hours_to_expire}h`}
          </span>
          <button type="button" onclick="removeItem(${idx})" class="text-slate-400 hover:text-rose-600 font-bold px-1 text-sm cursor-pointer" title="Xóa món">&times;</button>
        </div>
      </div>
    `;
  }).join("");
}


// -----------------------------------------------------------------------------
// Recommendation Execution
// -----------------------------------------------------------------------------
async function handleRecommend() {
  if (currentPantry.length === 0) {
    alert("Vui lòng thêm ít nhất 1 nguyên liệu vào tủ lạnh!");
    return;
  }

  emptyState.classList.add("hidden");
  recommendationsList.classList.add("hidden");
  loadingState.classList.remove("hidden");

  const payload = {
    items: currentPantry,
    household_size: parseFloat(sliderServings.value),
    max_cooking_time_min: parseFloat(sliderTime.value),
    scenario_type: activePresetId || "custom"
  };

  try {
    const res = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    loadingState.classList.add("hidden");

    if (data.status !== "success" || !data.recommendations || data.recommendations.length === 0) {
      emptyState.classList.remove("hidden");
      latencyStat.textContent = `Không tìm thấy món phù hợp (${data.total_latency_ms || 0}ms)`;
      return;
    }

    latencyStat.textContent = `XGBoost đánh giá ${data.candidates_evaluated} ứng viên trong ${data.xgboost_inference_ms}ms (Tổng: ${data.total_latency_ms}ms)`;
    renderRecommendations(data.recommendations);
    recommendationsList.classList.remove("hidden");

  } catch (err) {
    loadingState.classList.add("hidden");
    emptyState.classList.remove("hidden");
    console.error("Recommendation error:", err);
    alert("Lỗi kết nối tới AI Backend. Hãy đảm bảo web server đang chạy!");
  }
}

function renderRecommendations(recs) {
  recommendationsList.innerHTML = recs.map((dish, idx) => {
    const isTop1 = idx === 0;
    const rankLabel = isTop1 ? "#1 Khuyên Dùng Tối Ưu" : `#${idx + 1} Lựa Chọn`;

    let badgeClass = "bg-emerald-50 text-emerald-800 border-emerald-200";
    if (dish.status_badge === "elastic") badgeClass = "bg-sky-50 text-sky-800 border-sky-200";
    if (dish.status_badge === "shopping") badgeClass = "bg-amber-50 text-amber-800 border-amber-200";

    return `
      <article class="p-5 rounded-2xl border transition-all bg-white shadow-xs hover:shadow-md ${
        isTop1 ? 'border-teal-500 ring-2 ring-teal-500/20' : 'border-slate-200'
      }">
        <div class="flex items-center justify-between mb-2.5">
          <span class="px-2.5 py-0.5 rounded-full text-xs font-extrabold uppercase tracking-wide ${
            isTop1 ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-slate-100 text-slate-700'
          }">${rankLabel}</span>

          ${dish.is_zero_waste_hero ? `
            <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300 animate-flame">
              🔥 Giải cứu: ${dish.rescued_items.join(", ")}
            </span>
          ` : ''}
        </div>

        <h3 class="font-serif text-xl font-bold text-slate-900 mb-2">${dish.name}</h3>

        <!-- Meta Pills Row -->
        <div class="flex flex-wrap gap-2 items-center text-xs text-slate-600 mb-3">
          <span class="px-2.5 py-1 rounded-md bg-slate-100 font-semibold">⏱️ ${dish.cooking_time_min} phút</span>
          <span class="px-2.5 py-1 rounded-md bg-slate-100 font-semibold">🍲 ${dish.cooking_method}</span>
          <span class="px-2.5 py-1 rounded-md bg-slate-100 font-semibold">🍽️ ${dish.dish_type}</span>
          <span class="px-2.5 py-1 rounded-md font-bold ${dish.is_scaled ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-slate-100'}"
            title="${dish.is_scaled ? `Đã tự động co giãn từ công thức gốc ${dish.default_servings} người` : 'Khẩu phần chuẩn'}">
            👥 ${dish.servings} người ${dish.is_scaled ? `(gốc: ${dish.default_servings})` : ''}
          </span>
          <span class="px-2.5 py-1 rounded-md font-bold border ${badgeClass}">${dish.status_text}</span>
        </div>

        <!-- Serving Scale Banner -->
        ${dish.is_scaled ? `
          <div class="p-2.5 mb-3 bg-emerald-50/80 border border-dashed border-emerald-300 rounded-xl text-xs text-emerald-900 flex items-center gap-1.5 font-medium">
            <span>⚡</span>
            <span>Đã tự động căn chỉnh định lượng & calo theo <strong>${dish.servings} người</strong> (công thức gốc: ${dish.default_servings} người, tỷ lệ x${dish.scale_factor})</span>
          </div>
        ` : ''}

        <!-- Nutrition Macro Bar -->
        <div class="grid grid-cols-4 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-100 text-center mb-3.5">
          <div>
            <div class="text-base font-extrabold text-teal-900">${dish.calories_total}</div>
            <div class="text-[10px] uppercase font-bold text-slate-400">Tổng Kcal (${dish.servings} người)</div>
          </div>
          <div>
            <div class="text-base font-bold text-slate-800">${dish.protein_g}g</div>
            <div class="text-[10px] uppercase font-bold text-slate-400">Đạm tổng</div>
          </div>
          <div>
            <div class="text-base font-bold text-slate-800">${dish.fat_g}g</div>
            <div class="text-[10px] uppercase font-bold text-slate-400">Béo tổng</div>
          </div>
          <div>
            <div class="text-base font-bold text-slate-800">${dish.carbs_g}g</div>
            <div class="text-[10px] uppercase font-bold text-slate-400">Carbs tổng</div>
          </div>
        </div>
        <div class="text-[11px] text-slate-400 text-right -mt-2 mb-3 font-medium">
          💡 ~${dish.calories_per_serving} kcal/người
        </div>

        <!-- Ingredient Checklist -->
        <div class="space-y-1.5 mb-3">
          <div class="text-xs font-bold text-slate-700">Kiểm tra nguyên liệu:</div>
          <div class="flex flex-wrap gap-1.5">
            ${dish.matched_ingredients.map(ing => `
              <span class="px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200" title="Đã có trong tủ">
                ✓ ${ing.display || ing.name}
              </span>
            `).join("")}
            ${(dish.staple_ingredients || []).map(ing => `
              <span class="px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200" title="Gia vị bếp có sẵn">
                🧂 ${ing.display || ing.name}
              </span>
            `).join("")}
            ${dish.missing_ingredients.map(ing => `
              <span class="px-2.5 py-1 rounded-md text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200" title="Cần đi chợ mua thêm">
                🛒 Cần mua: ${ing.display || ing.name}
              </span>
            `).join("")}
          </div>
        </div>

        <!-- Cooking Steps Accordion -->
        <button type="button" onclick="toggleInstructions(${idx})"
          class="w-full text-left py-2.5 px-3.5 bg-slate-50 hover:bg-slate-100/90 rounded-xl text-xs font-bold text-slate-700 flex items-center justify-between transition-all cursor-pointer border border-slate-200/70">
          <span class="flex items-center gap-2">
            <span>📖</span>
            <span>Xem hướng dẫn nấu chi tiết</span>
            ${dish.instructions_steps && dish.instructions_steps.length > 0 ? `
              <span class="px-2 py-0.5 bg-teal-100 text-teal-800 rounded-full text-[10px] font-bold">
                ${dish.instructions_steps.length} bước
              </span>
            ` : ''}
          </span>
          <span id="instructIcon-${idx}" class="text-slate-400 font-bold text-[10px]">▼</span>
        </button>
        <div class="instructions-body" id="instruct-${idx}">
          <div class="p-3 bg-slate-50/70 rounded-b-xl border-x border-b border-slate-200/70 text-xs text-slate-700 mt-1">
            ${renderInstructionContent(dish)}
          </div>
        </div>

      </article>
    `;
  }).join("");
}

function renderInstructionContent(dish) {
  let html = "";
  if (dish.instructions_steps && Array.isArray(dish.instructions_steps) && dish.instructions_steps.length > 0) {
    html += `<div class="space-y-2 mb-3">`;
    dish.instructions_steps.forEach(st => {
      const stepTitle = escapeHtml(st.title || `Bước ${st.step}`);
      const stepContent = escapeHtml(st.content || "");
      html += `
        <div class="flex items-start gap-2.5 p-2.5 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
          <span class="shrink-0 px-2.5 py-0.5 rounded-md bg-teal-50 text-teal-800 border border-teal-200 font-bold text-[11px]">${stepTitle}</span>
          <p class="text-xs text-slate-700 leading-relaxed">${stepContent}</p>
        </div>
      `;
    });
    html += `</div>`;
  } else if (dish.instructions && dish.instructions !== "Chưa có hướng dẫn chi tiết.") {
    html += `<div class="whitespace-pre-line text-xs text-slate-700 mb-3 bg-white p-3 rounded-xl border border-slate-200/80 leading-relaxed">${escapeHtml(dish.instructions)}</div>`;
  } else {
    html += `<div class="text-xs text-slate-400 italic py-2 text-center mb-2">Chưa có hướng dẫn chi tiết dạng từng bước. Bạn có thể mở liên kết công thức gốc bên dưới.</div>`;
  }

  if (dish.source_url) {
    const platform = escapeHtml(dish.source_platform || "Cookpad Việt Nam");
    html += `
      <div class="pt-2.5 border-t border-slate-200 flex items-center justify-between text-[11px] text-slate-500">
        <span>Nguồn tham khảo: <strong class="text-slate-700 font-medium">${platform}</strong></span>
        <a href="${escapeHtml(dish.source_url)}" target="_blank" rel="noopener noreferrer"
           class="inline-flex items-center gap-1 text-teal-700 hover:text-teal-900 font-bold hover:underline">
          <span>🔗 Mở công thức gốc</span>
          <span class="text-[10px]">↗</span>
        </a>
      </div>
    `;
  }

  return html;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function toggleInstructions(idx) {
  const el = document.getElementById(`instruct-${idx}`);
  const icon = document.getElementById(`instructIcon-${idx}`);
  if (el) {
    el.classList.toggle("open");
    if (icon) {
      icon.textContent = el.classList.contains("open") ? "▲" : "▼";
    }
  }
}


// =============================================================================
// SMART INPUT — OCR RECEIPT & LABEL SCANNER (PaddleOCR + VietOCR + Live Camera)
// =============================================================================
let cameraStream = null;

function setOcrInputMode(mode) {
  const uploadBox = document.getElementById("ocrUploadContainer");
  const cameraBox = document.getElementById("ocrCameraContainer");
  const btnUpload = document.getElementById("btnModeUpload");
  const btnCamera = document.getElementById("btnModeCamera");

  if (mode === "camera") {
    uploadBox.classList.add("hidden");
    cameraBox.classList.remove("hidden");
    btnCamera.classList.add("bg-white", "text-sky-800", "shadow-xs");
    btnCamera.classList.remove("text-slate-600");
    btnUpload.classList.remove("bg-white", "text-sky-800", "shadow-xs");
    btnUpload.classList.add("text-slate-600");
    startCameraStream();
  } else {
    stopCameraStream();
    uploadBox.classList.remove("hidden");
    cameraBox.classList.add("hidden");
    btnUpload.classList.add("bg-white", "text-sky-800", "shadow-xs");
    btnUpload.classList.remove("text-slate-600");
    btnCamera.classList.remove("bg-white", "text-sky-800", "shadow-xs");
    btnCamera.classList.add("text-slate-600");
  }
}

async function startCameraStream() {
  const video = document.getElementById("ocrVideoFeed");
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false
    });
    video.srcObject = cameraStream;
  } catch (err) {
    console.error("Camera access error:", err);
    alert("Không thể truy cập camera: " + err.message + ". Bạn có thể tải ảnh lên thay thế.");
    setOcrInputMode("upload");
  }
}

function stopCameraStream() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
  }
}

function compressImageFile(file, maxDim = 1600, quality = 0.85) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = reject;
    reader.onload = (e) => {
      const img = new Image();
      img.onerror = reject;
      img.onload = () => {
        let w = img.width;
        let h = img.height;
        let scale = 1.0;
        if (Math.max(w, h) > maxDim) {
          scale = maxDim / Math.max(w, h);
          w = Math.round(w * scale);
          h = Math.round(h * scale);
        }

        const canvas = document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = "high";
        ctx.drawImage(img, 0, 0, w, h);

        const dataUrl = canvas.toDataURL("image/jpeg", quality);
        const originalKb = (file.size / 1024).toFixed(1);
        const compKb = ((dataUrl.length * 0.75) / 1024).toFixed(1);
        const savingsPct = Math.max(0, Math.round((1 - compKb / Math.max(1, originalKb)) * 100));

        resolve({
          dataUrl,
          originalKb,
          compKb,
          savingsPct,
          width: w,
          height: h
        });
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

function captureCameraSnapshot() {
  const video = document.getElementById("ocrVideoFeed");
  const canvas = document.getElementById("ocrCanvasCapture");
  if (!video || !video.videoWidth) {
    alert("Camera chưa sẵn sàng, vui lòng đợi giây lát!");
    return;
  }

  let w = video.videoWidth;
  let h = video.videoHeight;
  const maxDim = 1280;
  if (Math.max(w, h) > maxDim) {
    const scale = maxDim / Math.max(w, h);
    w = Math.round(w * scale);
    h = Math.round(h * scale);
  }

  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = "high";
  ctx.drawImage(video, 0, 0, w, h);
  const dataUrl = canvas.toDataURL("image/jpeg", 0.82);
  const compKb = ((dataUrl.length * 0.75) / 1024).toFixed(1);

  ocrStatusMsg.textContent = `📸 Đã chụp & nén frame ảnh (${w}x${h}, ~${compKb} KB). Đang quét OCR...`;
  fetch("/api/smart-input/ocr", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_base64: dataUrl })
  })
  .then(res => res.json())
  .then(data => handleOcrResponse(data, { savingsPct: 65, compKb }))
  .catch(err => {
    console.error("Snapshot scan error:", err);
    ocrStatusMsg.textContent = "Lỗi khi quét ảnh từ camera.";
  });
}

async function loadSampleReceipt(sampleId) {
  ocrStatusMsg.textContent = "Đang tải mẫu và phân tích thực phẩm...";
  try {
    const res = await fetch("/api/smart-input/ocr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sample_id: sampleId })
    });
    const data = await res.json();
    handleOcrResponse(data);
  } catch (err) {
    console.error("OCR sample error:", err);
    ocrStatusMsg.textContent = "Lỗi khi tải mẫu hóa đơn.";
  }
}

async function handleOcrFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  ocrStatusMsg.textContent = `⚡ Đang tối ưu nén ảnh (${(file.size / 1024).toFixed(0)} KB)...`;
  try {
    const compressed = await compressImageFile(file, 1600, 0.85);
    ocrStatusMsg.textContent = `🚀 Đã nén: ${compressed.originalKb} KB → ${compressed.compKb} KB (-${compressed.savingsPct}%). Đang nhận diện OCR...`;

    const res = await fetch("/api/smart-input/ocr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_base64: compressed.dataUrl,
        filename: file.name
      })
    });
    const data = await res.json();
    handleOcrResponse(data, compressed);
  } catch (err) {
    console.error("OCR upload error:", err);
    ocrStatusMsg.textContent = "Lỗi khi nén hoặc quét ảnh hóa đơn.";
  }
}

async function executeOcrParse() {
  const text = ocrRawText.value.trim();
  if (!text) {
    alert("Vui lòng tải ảnh hóa đơn hoặc dán nội dung chữ vào ô!");
    return;
  }

  ocrStatusMsg.textContent = "Đang phân tích cú pháp thực phẩm từ text...";
  try {
    const res = await fetch("/api/smart-input/ocr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ receipt_text: text })
    });
    const data = await res.json();
    handleOcrResponse(data);
  } catch (err) {
    console.error("OCR text parse error:", err);
    ocrStatusMsg.textContent = "Lỗi khi phân tích hóa đơn.";
  }
}

function updateOcrStats(text, engine) {
  const metaEl = document.getElementById("ocrRawMeta");
  if (!metaEl) return;
  const clean = (text || "").trim();
  if (!clean) {
    metaEl.textContent = "Chưa có text • Sẵn sàng nhận diện";
    return;
  }
  const lines = clean.split("\n").filter(l => l.trim().length > 0).length;
  const chars = clean.length;
  const eng = engine || "PaddleOCR + VietOCR (CUDA)";
  metaEl.textContent = `${eng} • ${lines} dòng text • ${chars} ký tự`;
}

function copyOcrRawText() {
  const text = ocrRawText.value;
  if (!text || !text.trim()) {
    alert("Chưa có nội dung chữ để sao chép!");
    return;
  }
  navigator.clipboard.writeText(text).then(() => {
    const btnText = document.getElementById("btnCopyOcrText");
    if (btnText) {
      const orig = btnText.textContent;
      btnText.textContent = "✓ Đã Chép!";
      setTimeout(() => { btnText.textContent = orig; }, 1500);
    }
  }).catch(() => {
    // Fallback for clipboard
    ocrRawText.select();
    document.execCommand("copy");
    alert("Đã sao chép text vào clipboard!");
  });
}

function clearOcrText() {
  ocrRawText.value = "";
  ocrDetectedItems = [];
  updateOcrStats("", "");
  ocrStatusMsg.textContent = "Đã xóa nội dung. Sẵn sàng quét ảnh mới.";
  const cnt = document.getElementById("ocrDetectedCount");
  if (cnt) cnt.textContent = "Bóc tách tự động: 0 món thực phẩm";
  if (ocrItemsContainer) {
    ocrItemsContainer.innerHTML = "";
    ocrItemsContainer.classList.add("hidden");
  }
}

function handleOcrResponse(data, clientStats) {
  const raw = (data.raw_text || "").trim();
  if (raw) {
    ocrRawText.value = raw;
    updateOcrStats(raw, data.engine);
  }

  if (data.status !== "success" && !raw) {
    ocrStatusMsg.textContent = data.message || "Không phát hiện thấy văn bản nào trong ảnh.";
    return;
  }

  let statsInfo = "";
  if (clientStats && clientStats.savingsPct > 0) {
    statsInfo = ` (Ảnh nén -${clientStats.savingsPct}% dung lượng)`;
  } else if (data.preprocess_stats && data.preprocess_stats.savings_percent > 0) {
    statsInfo = ` (Tối ưu file -${data.preprocess_stats.savings_percent}%)`;
  }

  const linesCount = raw ? raw.split("\n").filter(l => l.trim()).length : 0;
  ocrStatusMsg.textContent = `✅ Nhận diện thành công ${linesCount} dòng chữ từ ảnh!${statsInfo}`;

  if (data.items && data.items.length > 0) {
    ocrDetectedItems = data.items;
    const cnt = document.getElementById("ocrDetectedCount");
    if (cnt) cnt.textContent = `Bóc tách tự động: ${ocrDetectedItems.length} món thực phẩm`;
    renderOcrItems();
  }
}

function renderOcrItems() {
  if (ocrDetectedItems.length === 0) {
    if (ocrItemsContainer) ocrItemsContainer.classList.add("hidden");
    return;
  }

  if (ocrItemsContainer) {
    ocrItemsContainer.classList.remove("hidden");
    ocrItemsContainer.innerHTML = ocrDetectedItems.map(it => `
      <div class="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 bg-slate-50/70 text-xs">
        <div class="space-y-0.5">
          <span class="font-bold text-slate-900 text-xs block">${it.name}</span>
          <span class="text-[10px] text-slate-400 line-clamp-1">Gốc: "${it.raw_receipt_line || it.name}"</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 bg-white border border-slate-200 rounded font-mono font-bold text-slate-700 text-xs">
            ${it.quantity_g}g
          </span>
          <span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-semibold text-[10px]">
            Hạn ${it.hours_to_expire}h
          </span>
        </div>
      </div>
    `).join("");
  }
}

function pushOcrItemsToFridge() {
  if (ocrDetectedItems.length === 0) return;
  ocrDetectedItems.forEach(it => {
    addItemToPantry(it.name, it.quantity_g, it.hours_to_expire);
  });
  switchAppTab("recommend");
  handleRecommend();
  alert(`Đã thêm ${ocrDetectedItems.length} thực phẩm vào Tủ Lạnh!`);
}


// =============================================================================
// SMART INPUT — ASR DUAL STREAM (Groq Whisper Turbo & Gipformer FLAC)
// =============================================================================
let currentAsrEngine = "groq_whisper";
let mediaRecorderInstance = null;
let recordedAudioChunks = [];
let recordingTimer = null;
let recordingSeconds = 0;

function setAsrEngine(engine) {
  currentAsrEngine = engine;
  const badge = document.getElementById("asrEngineBadge");
  const labelGroq = document.getElementById("labelEngineGroq");
  const labelGip = document.getElementById("labelEngineGipformer");
  const micSubText = document.getElementById("micSubText");

  if (engine === "groq_whisper") {
    if (badge) {
      badge.textContent = "⚡ Groq Whisper Turbo";
      badge.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800";
    }
    if (labelGroq) labelGroq.className = "flex flex-col p-2 rounded-lg border-2 border-amber-500 bg-white cursor-pointer transition-all";
    if (labelGip) labelGip.className = "flex flex-col p-2 rounded-lg border-2 border-slate-200 bg-white/60 cursor-pointer transition-all";
    if (micSubText) micSubText.textContent = "Tiếng Việt • Groq Cloud Whisper Large V3 Turbo (<500ms)";
  } else {
    if (badge) {
      badge.textContent = "🚀 Gipformer Local (FLAC)";
      badge.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-sky-100 text-sky-800";
    }
    if (labelGip) labelGip.className = "flex flex-col p-2 rounded-lg border-2 border-sky-500 bg-white cursor-pointer transition-all";
    if (labelGroq) labelGroq.className = "flex flex-col p-2 rounded-lg border-2 border-slate-200 bg-white/60 cursor-pointer transition-all";
    if (micSubText) micSubText.textContent = "Tiếng Việt • ffmpeg 16kHz mono FLAC • Gipformer Local";
  }
}

async function handleAsrAudioUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const engineName = currentAsrEngine === "groq_whisper" ? "Groq Whisper Turbo" : "Gipformer FLAC";
  asrStatusMsg.textContent = `Đang gửi file âm thanh (${file.name}, ${(file.size / 1024).toFixed(0)} KB) tới engine ${engineName}...`;
  
  const formData = new FormData();
  formData.append("audio", file);
  formData.append("engine", currentAsrEngine);

  try {
    const res = await fetch("/api/smart-input/asr-upload", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    handleAsrResponse(data);
  } catch (err) {
    console.error("Audio upload error:", err);
    asrStatusMsg.textContent = "Lỗi khi gửi file âm thanh tới server: " + err.message;
  }
}

async function toggleAudioRecording() {
  if (isRecordingSpeech) {
    stopAudioRecording();
  } else {
    startAudioRecording();
  }
}

async function startAudioRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordedAudioChunks = [];

    let mimeType = "";
    if (typeof MediaRecorder !== "undefined") {
      if (MediaRecorder.isTypeSupported("audio/webm")) mimeType = "audio/webm";
      else if (MediaRecorder.isTypeSupported("audio/ogg")) mimeType = "audio/ogg";
      else if (MediaRecorder.isTypeSupported("audio/mp4")) mimeType = "audio/mp4";
    }
    const options = mimeType ? { mimeType } : {};
    mediaRecorderInstance = new MediaRecorder(stream, options);

    mediaRecorderInstance.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) {
        recordedAudioChunks.push(e.data);
      }
    };

    mediaRecorderInstance.onstop = async () => {
      // Release microphone hardware immediately
      stream.getTracks().forEach(t => t.stop());

      const mime = mediaRecorderInstance.mimeType || "audio/webm";
      const audioBlob = new Blob(recordedAudioChunks, { type: mime });

      if (audioBlob.size < 500) {
        asrStatusMsg.textContent = "Âm thanh quá ngắn hoặc không phát hiện tiếng nói. Vui lòng nói lại!";
        return;
      }

      const engineName = currentAsrEngine === "groq_whisper" ? "Groq Whisper Turbo" : "Gipformer";
      asrStatusMsg.textContent = `⚡ Đang gửi audio (${(audioBlob.size / 1024).toFixed(0)} KB) tới ${engineName}...`;

      const formData = new FormData();
      const ext = mime.includes("ogg") ? "ogg" : (mime.includes("mp4") ? "m4a" : "webm");
      formData.append("audio", audioBlob, `speech_recording.${ext}`);
      formData.append("engine", currentAsrEngine);

      try {
        const res = await fetch("/api/smart-input/asr-upload", {
          method: "POST",
          body: formData
        });
        const data = await res.json();
        handleAsrResponse(data);
      } catch (err) {
        console.error("ASR upload error:", err);
        asrStatusMsg.textContent = "Lỗi kết nối khi gửi âm thanh tới server: " + err.message;
      }
    };

    mediaRecorderInstance.start(250);
    isRecordingSpeech = true;
    recordingSeconds = 0;
    btnMicRecord.classList.add("animate-recording", "from-rose-500", "to-red-600");
    btnMicRecord.classList.remove("from-amber-500", "to-orange-600");
    micStatusText.textContent = `🎙️ Đang thu âm... (0s - Bấm lại để dừng)`;

    recordingTimer = setInterval(() => {
      recordingSeconds++;
      micStatusText.textContent = `🎙️ Đang thu âm... (${recordingSeconds}s - Bấm lại để dừng)`;
      if (recordingSeconds >= 45) {
        stopAudioRecording();
      }
    }, 1000);

  } catch (err) {
    console.error("Microphone access error:", err);
    alert("Không thể truy cập Microphone: " + err.message + ".\nVui lòng cấp quyền micro cho trang web hoặc tải file âm thanh lên thay thế.");
  }
}

function stopAudioRecording() {
  if (mediaRecorderInstance && mediaRecorderInstance.state !== "inactive") {
    mediaRecorderInstance.stop();
  }
  isRecordingSpeech = false;
  clearInterval(recordingTimer);
  btnMicRecord.classList.remove("animate-recording", "from-rose-500", "to-red-600");
  btnMicRecord.classList.add("from-amber-500", "to-orange-600");
  micStatusText.textContent = "Đã dừng thu âm. Đang chuyển đổi FLAC 16kHz...";
}

async function loadSampleVoice(sampleId) {
  asrStatusMsg.textContent = "Đang nạp câu mẫu...";
  try {
    const res = await fetch("/api/smart-input/asr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sample_id: sampleId })
    });
    const data = await res.json();
    handleAsrResponse(data);
  } catch (err) {
    console.error("ASR sample error:", err);
    asrStatusMsg.textContent = "Lỗi khi nạp câu khẩu ngữ mẫu.";
  }
}

async function executeAsrParse() {
  const text = asrTranscript.value.trim();
  if (!text) {
    alert("Vui lòng thu âm hoặc dán nội dung lời nói vào ô trước!");
    return;
  }

  asrStatusMsg.textContent = "Đang phân tích thực thể ẩm thực & quy đổi gram...";
  try {
    const res = await fetch("/api/smart-input/asr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript: text })
    });
    const data = await res.json();
    handleAsrResponse(data);
  } catch (err) {
    console.error("ASR parse error:", err);
    asrStatusMsg.textContent = "Lỗi khi phân tích giọng nói.";
  }
}

function updateAsrStats(text, engine, latency) {
  const metaEl = document.getElementById("asrRawMeta");
  if (!metaEl) return;
  const clean = (text || "").trim();
  if (!clean) {
    metaEl.textContent = "Chưa có dữ liệu • Sẵn sàng nhận diện";
    return;
  }
  const words = clean.split(/\s+/).filter(Boolean).length;
  const chars = clean.length;
  const eng = engine || (currentAsrEngine === "groq_whisper" ? "Groq Whisper Turbo" : "Gipformer Local");
  const lat = latency ? ` • ${latency}ms` : "";
  metaEl.textContent = `${eng} • ${words} từ • ${chars} ký tự${lat}`;
}

function copyAsrTranscript() {
  const text = asrTranscript.value;
  if (!text || !text.trim()) {
    alert("Chưa có nội dung lời nói để sao chép!");
    return;
  }
  navigator.clipboard.writeText(text).then(() => {
    const btnText = document.getElementById("btnCopyAsrText");
    if (btnText) {
      const orig = btnText.textContent;
      btnText.textContent = "✓ Đã Chép!";
      setTimeout(() => { btnText.textContent = orig; }, 1500);
    }
  }).catch(() => {
    asrTranscript.select();
    document.execCommand("copy");
    alert("Đã sao chép transcript vào clipboard!");
  });
}

let currentAsrData = null;
let asrViewMode = "corrected";

function toggleAsrTextView(mode) {
  asrViewMode = mode;
  const btnCorr = document.getElementById("btnAsrShowCorrected");
  const btnRaw = document.getElementById("btnAsrShowRaw");
  if (!currentAsrData) return;

  if (mode === "corrected") {
    asrTranscript.value = (currentAsrData.transcript || currentAsrData.corrected_transcript || currentAsrData.raw_transcript || "").trim();
    if (btnCorr) {
      btnCorr.className = "px-2 py-1 rounded-md font-semibold bg-white text-slate-800 shadow-2xs cursor-pointer";
    }
    if (btnRaw) {
      btnRaw.className = "px-2 py-1 rounded-md font-medium text-slate-500 hover:text-slate-800 cursor-pointer";
    }
  } else {
    asrTranscript.value = (currentAsrData.raw_transcript || currentAsrData.transcript || "").trim();
    if (btnRaw) {
      btnRaw.className = "px-2 py-1 rounded-md font-semibold bg-white text-slate-800 shadow-2xs cursor-pointer";
    }
    if (btnCorr) {
      btnCorr.className = "px-2 py-1 rounded-md font-medium text-slate-500 hover:text-slate-800 cursor-pointer";
    }
  }
  updateAsrStats(asrTranscript.value, currentAsrData.engine, currentAsrData.latency_ms);
}

function clearAsrText() {
  currentAsrData = null;
  asrTranscript.value = "";
  asrDetectedItems = [];
  updateAsrStats("", "", 0);
  asrStatusMsg.textContent = "Đã xóa transcript. Sẵn sàng thu âm mới.";
  const cnt = document.getElementById("asrDetectedCount");
  if (cnt) cnt.textContent = "Bóc tách tự động: 0 món thực phẩm";
  const asrBadge = document.getElementById("asrCorrectorBadge");
  const asrViewGroup = document.getElementById("asrViewModeGroup");
  if (asrBadge) asrBadge.classList.add("hidden");
  if (asrViewGroup) asrViewGroup.classList.add("hidden");
  if (asrItemsContainer) {
    asrItemsContainer.innerHTML = "";
    asrItemsContainer.classList.add("hidden");
  }
}

function handleAsrResponse(data) {
  currentAsrData = data;
  const text = (data.transcript || data.corrected_transcript || data.raw_transcript || data.raw_text || "").trim();
  if (text) {
    asrTranscript.value = text;
    updateAsrStats(text, data.engine, data.latency_ms);
  }

  // Handle ProtonX Corrector badge & toggles
  const asrBadge = document.getElementById("asrCorrectorBadge");
  const asrViewGroup = document.getElementById("asrViewModeGroup");
  if (data.correction_applied) {
    if (asrBadge) asrBadge.classList.remove("hidden");
    if (asrViewGroup) asrViewGroup.classList.remove("hidden");
  } else {
    if (asrBadge) asrBadge.classList.add("hidden");
    if (asrViewGroup) asrViewGroup.classList.add("hidden");
  }

  if (data.status !== "success" && !text) {
    asrStatusMsg.textContent = data.message || "Không nhận diện được giọng nói.";
    return;
  }

  let statsInfo = "";
  if (data.preprocess_stats && data.preprocess_stats.savings_percent > 0) {
    statsInfo = ` (Nén FLAC 16kHz: -${data.preprocess_stats.savings_percent}% dung lượng)`;
  }
  if (data.correction_applied) {
    statsInfo += ` • ✨ Đã sửa dấu & chính tả bằng ProtonX`;
  }
  const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
  asrStatusMsg.textContent = `✅ Nhận diện thành công lời nói (${words} từ, ${data.latency_ms || 0}ms)!${statsInfo}`;

  if (data.items && data.items.length > 0) {
    asrDetectedItems = data.items;
    const cnt = document.getElementById("asrDetectedCount");
    if (cnt) cnt.textContent = `Bóc tách tự động: ${asrDetectedItems.length} món thực phẩm`;
    renderAsrItems();
  }
}

function renderAsrItems() {
  if (asrDetectedItems.length === 0) {
    if (asrItemsContainer) asrItemsContainer.classList.add("hidden");
    return;
  }

  if (asrItemsContainer) {
    asrItemsContainer.classList.remove("hidden");
    asrItemsContainer.innerHTML = asrDetectedItems.map(it => `
      <div class="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 bg-slate-50/70 text-xs">
        <div class="space-y-0.5">
          <span class="font-bold text-slate-900 text-xs block">${it.name}</span>
          <span class="text-[10px] text-amber-800 bg-amber-100/60 px-1.5 py-0.5 rounded inline-block">
            "${it.spoken_phrase}"
          </span>
        </div>
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 bg-white border border-slate-200 rounded font-mono font-bold text-slate-700 text-xs">
            ${it.quantity_g}g
          </span>
          <span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-semibold text-[10px]">
            Hạn ${it.hours_to_expire}h
          </span>
        </div>
      </div>
    `).join("");
  }
}

function pushAsrItemsToFridge() {
  if (asrDetectedItems.length === 0) return;
  asrDetectedItems.forEach(it => {
    addItemToPantry(it.name, it.quantity_g, it.hours_to_expire);
  });
  switchAppTab("recommend");
  handleRecommend();
  alert(`Đã thêm ${asrDetectedItems.length} thực phẩm vào Tủ Lạnh!`);
}
