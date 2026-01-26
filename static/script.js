document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewImage = document.getElementById('preview-image');
    const placeholder = document.querySelector('.placeholder-content');
    const analyzeBtn = document.getElementById('analyze-btn');
    const scanBeam = document.getElementById('scan-beam');

    const resultsContainer = document.getElementById('results-container');
    const idleState = document.getElementById('idle-state');
    const brandName = document.getElementById('brand-name');
    const confidenceValue = document.getElementById('confidence-value');
    const probGrid = document.getElementById('prob-grid');

    let currentFile = null;

    // --- Drag & Drop ---
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file (JPG, PNG).');
            return;
        }
        currentFile = file;

        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.classList.remove('hidden');
            placeholder.classList.add('hidden');
            analyzeBtn.disabled = false;

            // Reset UI
            scanBeam.classList.add('hidden');
            resultsContainer.classList.add('hidden');
            idleState.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }

    // --- Analysis ---
    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI: Start Scanning
        scanBeam.classList.remove('hidden');
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="btn-text">SCANNING...</span>';

        try {
            const formData = new FormData();
            formData.append('file', currentFile);

            const start = Date.now();
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Prediction failed');
            }

            const data = await response.json();
            const latency = Date.now() - start;
            document.getElementById('latency').innerText = `${latency}ms`;

            // Display Results
            displayResults(data);

        } catch (error) {
            console.error(error);
            alert('Error: ' + error.message);
        } finally {
            scanBeam.classList.add('hidden');
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span class="btn-text">RUN DIAGNOSTIC</span><span class="btn-glitch"></span>';
        }
    });

    function displayResults(data) {
        idleState.classList.add('hidden');
        resultsContainer.classList.remove('hidden');

        // Brand Name
        brandName.innerText = data.label;
        brandName.setAttribute('data-text', data.label);

        // Confidence
        const confPercent = Math.round(data.confidence * 100);
        confidenceValue.innerText = `${confPercent}%`;

        // Colorize based on confidence
        if (data.confidence > 0.8) {
            confidenceValue.style.color = 'var(--neon-green)';
        } else if (data.confidence > 0.5) {
            confidenceValue.style.color = 'var(--neon-blue)';
        } else {
            confidenceValue.style.color = 'var(--alert-red)';
        }

        // Mock Probability Bars (Since API currently returns top 1, we simulate others or fetch from backend if updated)
        // Ideally backend should return Top K. 
        // For visual flair, we will just show the top one as full and others random low if not provided,
        // or just show the top 1 bar.
        // Let's make it look cool with just the main one for now, or fake it for "Cyber" feel unless we update API.
        // Actually, let's just show the top one.

        probGrid.innerHTML = `
            <div class="prob-row">
                <span class="prob-label">${data.label}</span>
                <div class="prob-bar-track">
                    <div class="prob-bar-fill" style="width: ${confPercent}%"></div>
                </div>
                <span>${confPercent}%</span>
            </div>
        `;
    }
});
