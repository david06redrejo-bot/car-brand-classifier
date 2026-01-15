const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const imagePreview = document.getElementById('image-preview');
const clearBtn = document.getElementById('clear-btn');
const resultContainer = document.getElementById('result-container');
const resultLabel = document.getElementById('result-label');
const resultConfidence = document.getElementById('result-confidence');
const loader = document.getElementById('loader');

// Drag & Drop Events
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
});

dropZone.addEventListener('drop', handleDrop, false);
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFiles);
clearBtn.addEventListener('click', resetUI);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles({ target: { files: files } });
}

function handleFiles(e) {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
        previewFile(file);
        uploadFile(file);
    }
}

function previewFile(file) {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = function() {
        imagePreview.src = reader.result;
        previewContainer.hidden = false;
        dropZone.hidden = true;
    }
}

async function uploadFile(file) {
    resetResult();
    loader.hidden = false;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('API Error');

        const data = await response.json();
        showResult(data);

    } catch (error) {
        console.error('Error:', error);
        alert('Prediction failed. Is the backend running?');
    } finally {
        loader.hidden = true;
    }
}

function showResult(data) {
    resultLabel.textContent = data.label;
    resultConfidence.textContent = `Confidence: ${data.confidence}`;
    resultContainer.hidden = false;
}

function resetResult() {
    resultContainer.hidden = true;
    resultLabel.textContent = '';
    resultConfidence.textContent = '';
}

function resetUI() {
    fileInput.value = '';
    previewContainer.hidden = true;
    dropZone.hidden = false;
    resetResult();
}
