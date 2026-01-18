// script.js

// --- NAVIGATION ---
function scrollToSection(id) {
    document.getElementById(id).scrollIntoView({ behavior: 'smooth' });
}

// --- STATE ---
let currentImageBase64 = null;
let currentPredictionLabel = null;
let knownClasses = [];

// --- INIT ---
document.addEventListener('DOMContentLoaded', async () => {
    // Fetch classes for dropdown
    try {
        const res = await fetch('/classes');
        const data = await res.json();
        knownClasses = data.classes;
        populateDropdown();
    } catch (e) {
        console.error("Failed to load classes", e);
    }
});

function populateDropdown() {
    const select = document.getElementById('correct-label-select');
    select.innerHTML = '<option value="" disabled selected>Select Correct Brand</option>';
    knownClasses.forEach(cls => {
        const opt = document.createElement('option');
        opt.value = cls;
        opt.textContent = cls.toUpperCase();
        select.appendChild(opt);
    });
    // Add "Other"
    const other = document.createElement('option');
    other.value = "__other__";
    other.textContent = "Other (Add New)";
    select.appendChild(other);

    select.addEventListener('change', (e) => {
        const input = document.getElementById('new-brand-input');
        if (e.target.value === '__other__') {
            input.classList.remove('hidden');
        } else {
            input.classList.add('hidden');
        }
    });
}


// --- DRAG & DROP & UPLOAD ---
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewImg = document.getElementById('preview-img');
const uploadContent = document.getElementById('upload-content');

dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

function handleFileSelect(e) {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) return;

    // Show Preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        currentImageBase64 = e.target.result; // Keep for feedback
        document.getElementById('preview-wrapper').style.display = 'block';
        uploadContent.classList.add('hidden');

        // Auto predict
        uploadAndPredict(file);
    };
    reader.readAsDataURL(file);
}

document.getElementById('remove-btn').addEventListener('click', (e) => {
    e.stopPropagation();
    resetUI();
});

function resetUI() {
    fileInput.value = '';
    previewImg.src = '';
    document.getElementById('preview-wrapper').style.display = 'none';
    uploadContent.classList.remove('hidden');
    document.getElementById('result-panel').classList.add('hidden');
    resetFeedbackUI();
}

async function uploadAndPredict(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('/predict', { method: 'POST', body: formData });
        const data = await res.json();

        if (res.ok) {
            displayResult(data);
        } else {
            alert("Error: " + data.detail);
        }
    } catch (e) {
        console.error(e);
        alert("Prediction failed.");
    }
}

function displayResult(data) {
    const panel = document.getElementById('result-panel');
    const brand = document.getElementById('result-brand');
    const confBar = document.getElementById('confidence-bar');
    const confVal = document.getElementById('confidence-value');

    panel.classList.remove('hidden');
    brand.textContent = data.label;
    currentPredictionLabel = data.label;

    // Confidence logic
    let conf = data.confidence;
    // Adapt range if needed (SVM output depends on calibration)
    if (conf <= 1.0) conf = conf * 100;

    conf = Math.round(conf);
    confVal.textContent = conf + "%";
    confBar.style.width = conf + "%";

    // Reset feedback
    resetFeedbackUI();
}

// --- FEEDBACK LOOP ---

function resetFeedbackUI() {
    document.getElementById('correction-ui').classList.add('hidden');
    document.querySelectorAll('.feed-btn').forEach(b => b.disabled = false);
}

async function handleFeedback(isCorrect) {
    if (!currentImageBase64) return;

    const payload = {
        image_base64: currentImageBase64,
        label: currentPredictionLabel,
        is_correct: isCorrect,
        new_brand_name: null
    };

    if (isCorrect) {
        await sendFeedback(payload);
        alert("Thanks! Feedback recorded.");
    }
}

function showCorrectionUI() {
    document.getElementById('correction-ui').classList.remove('hidden');
}

async function submitCorrection() {
    const select = document.getElementById('correct-label-select');
    let label = select.value;
    let newBrand = null;

    if (label === '__other__') {
        newBrand = document.getElementById('new-brand-input').value;
        if (!newBrand) {
            alert("Please enter the brand name.");
            return;
        }
        label = newBrand; // For consistency, though backend checks new_brand_name
    } else if (!label) {
        alert("Please select a brand.");
        return;
    }

    const payload = {
        image_base64: currentImageBase64,
        label: label, // This is the CORRECT label now
        is_correct: false,
        new_brand_name: newBrand
    };

    await sendFeedback(payload);
    alert("Correction submitted. Retraining started in background.");
    resetFeedbackUI();
}

async function sendFeedback(payload) {
    try {
        const res = await fetch('/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const d = await res.json();
        console.log(d);
    } catch (e) {
        console.error("Feedback failed", e);
    }
}
