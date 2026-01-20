// OMNIVISION CYBER CORE //
document.addEventListener('DOMContentLoaded', () => {

    // STATE
    const state = {
        domain: null,
        imgBase64: null,
        prediction: null
    };

    // DOM ELEMENTS
    const els = {
        domainGrid: document.getElementById('domain-grid'),
        domainSelector: document.getElementById('domain-selector'),
        appInterface: document.getElementById('app-interface'),

        // Nav
        navItems: document.querySelectorAll('.nav-item'),
        resetBtn: document.getElementById('reset-btn'),

        // Hero
        initBtn: document.getElementById('init-btn'),
        moduleTitle: document.getElementById('module-title'),
        moduleSub: document.getElementById('module-subtitle'),
        heroBg: document.getElementById('hero-bg'),

        // Vision
        dropZone: document.getElementById('drop-zone'),
        fileInput: document.getElementById('file-input'),
        previewImg: document.getElementById('preview-img'),
        scanLine: document.getElementById('scan-line'),
        uploadContent: document.getElementById('upload-content'), // Hidden content inside drop-zone

        // Results
        resultContent: document.getElementById('result-content'),
        resultLabel: document.getElementById('result-label'),
        confFill: document.getElementById('confidence-fill'),
        confVal: document.getElementById('confidence-val'),
        statusLog: document.getElementById('status-log'),

        // Feedback
        feedConfirm: document.getElementById('feed-confirm'),
        feedReject: document.getElementById('feed-reject'),
        correctionModal: document.getElementById('correction-modal'),
        submitCorrection: document.getElementById('submit-correction'),
        cancelCorrection: document.getElementById('cancel-correction'),
        correctionInput: document.getElementById('correction-input'),

        // Metrics
        metricsModal: document.getElementById('metrics-modal') // Ensure this exists in HTML or specific ID
    };

    // CONFIG
    const DOMAIN_DATA = {
        cars: { title: "AUTOMOTIVE", sub: "VEHICLE ID", bg: "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=2560" },
        fashion: { title: "FASHION", sub: "LUXURY AUDIT", bg: "https://images.unsplash.com/photo-1496747611176-843222e1e57c?q=80&w=2560" },
        laliga: { title: "LALIGA", sub: "CLUB RECON", bg: "https://images.unsplash.com/photo-1522778119026-d647f0565c6d?q=80&w=2560" },
        tech: { title: "BIG TECH", sub: "CORP IDENTITY", bg: "https://images.unsplash.com/photo-1597733336794-12d05021d510?q=80&w=2560" },
        food: { title: "FAST FOOD", sub: "CHAIN DETECT", bg: "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?q=80&w=2560" }
    };

    // --- INIT ---
    initEvents();

    function initEvents() {
        // Domain Selection
        if (els.domainGrid) {
            els.domainGrid.addEventListener('click', (e) => {
                const card = e.target.closest('.cyber-card');
                if (card) selectDomain(card.dataset.domain);
            });
        }

        // Navigation
        els.navItems.forEach(item => {
            item.addEventListener('click', () => switchSection(item.dataset.target));
        });

        if (els.resetBtn) els.resetBtn.addEventListener('click', resetSystem);
        if (els.initBtn) els.initBtn.addEventListener('click', () => switchSection('playground'));

        // File Handling
        if (els.dropZone) els.dropZone.addEventListener('click', () => els.fileInput.click());
        if (els.fileInput) els.fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));

        // Drag & Drop
        if (els.dropZone) {
            els.dropZone.addEventListener('dragover', (e) => { e.preventDefault(); els.dropZone.style.borderColor = 'var(--accent)'; });
            els.dropZone.addEventListener('dragleave', (e) => { els.dropZone.style.borderColor = ''; });
            els.dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                els.dropZone.style.borderColor = '';
                if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
            });
        }

        // Feedback
        if (els.feedConfirm) els.feedConfirm.addEventListener('click', () => handleFeedback(true));
        if (els.feedReject) els.feedReject.addEventListener('click', () => {
            if (els.correctionModal) els.correctionModal.classList.remove('hidden');
        });

        if (els.submitCorrection) els.submitCorrection.addEventListener('click', submitManualCorrection);
        if (els.cancelCorrection) els.cancelCorrection.addEventListener('click', () => els.correctionModal.classList.add('hidden'));
    }

    // --- LOGIC ---

    function selectDomain(domain) {
        state.domain = domain;
        document.body.className = `theme-${domain}`;

        const conf = DOMAIN_DATA[domain];
        if (conf) {
            if (els.moduleTitle) els.moduleTitle.innerText = conf.title;
            if (els.moduleSub) els.moduleSub.innerText = conf.sub;
            if (els.heroBg) els.heroBg.style.backgroundImage = `url('${conf.bg}')`;
        }

        // Transition
        if (els.domainSelector) els.domainSelector.classList.add('hidden');
        if (els.appInterface) els.appInterface.classList.remove('hidden');
        log(`MODULE ${domain.toUpperCase()} ONLINE`);
    }

    function switchSection(targetId) {
        document.querySelectorAll('.cyber-section').forEach(sec => sec.classList.remove('active'));
        const target = document.getElementById(targetId);
        if (target) target.classList.add('active');

        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        const navItem = document.querySelector(`.nav-item[data-target="${targetId}"]`);
        if (navItem) navItem.classList.add('active');
    }

    function resetSystem() {
        state.domain = null;
        state.imgBase64 = null;
        state.prediction = null;

        if (els.fileInput) els.fileInput.value = '';
        if (els.previewImg) els.previewImg.classList.add('hidden');
        if (els.resultContent) els.resultContent.classList.add('hidden');
        if (els.scanLine) els.scanLine.classList.add('hidden');

        // Show upload placeholder
        const ph = document.querySelector('.placeholder-content');
        if (ph) ph.classList.remove('hidden');

        if (els.appInterface) els.appInterface.classList.add('hidden');
        if (els.domainSelector) els.domainSelector.classList.remove('hidden');
        document.body.className = 'theme-default';
    }

    function handleFile(file) {
        if (!file || !file.type.startsWith('image/')) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            state.imgBase64 = e.target.result;
            if (els.previewImg) {
                els.previewImg.src = state.imgBase64;
                els.previewImg.classList.remove('hidden');
            }
            if (els.scanLine) els.scanLine.classList.remove('hidden'); // Start scan

            // Hide placeholder/upload text (CRITICAL FOR VISUAL REGRESSION TEST)
            const ph = document.querySelector('.placeholder-content');
            // Or assume the test checks #upload-content if defined.
            // In index.html, it's .placeholder-content.
            if (ph) ph.classList.add('hidden');

            // Also hide results primarily
            if (els.resultContent) els.resultContent.classList.add('hidden');

            processImage(file);
        };
        reader.readAsDataURL(file);
    }

    async function processImage(file) {
        log("UPLOADING DATA PACKET...");
        const formData = new FormData();
        formData.append('file', file);

        try {
            await delay(800);
            log("ANALYZING NEURAL PATTERNS...");

            const res = await fetch(`/predict?domain=${state.domain}`, {
                method: 'POST',
                body: formData
            });

            const data = await res.json();

            if (els.scanLine) els.scanLine.classList.add('hidden'); // Stop scan

            if (res.ok) {
                displayResult(data);
                log("IDENTIFICATION SUCCESSFUL", true);
            } else {
                log(`ERROR: ${data.detail}`, false, true);
            }

        } catch (e) {
            if (els.scanLine) els.scanLine.classList.add('hidden');
            log("CONNECTION FAILURE", false, true);
            console.error(e);
        }
    }

    function displayResult(data) {
        state.prediction = data.label;
        if (els.resultContent) els.resultContent.classList.remove('hidden');
        if (els.resultLabel) els.resultLabel.innerText = data.label.toUpperCase();

        let conf = data.confidence;
        if (conf <= 1.0) conf = conf * 100;
        conf = Math.round(conf);

        if (els.confVal) els.confVal.innerText = `${conf}%`;
        if (els.confFill) els.confFill.style.width = `${conf}%`;
    }

    // --- METRICS ---
    // Exposed global for onclick in HTML if needed, but better event listener
    // Note: index.html has button onclick="openModal()" ? No, likely removed or needs listener.
    // The previous index.html had <button ... onclick="openModal()">
    // We should bind it if we find the button.

    // Check if openModal is called by HTML attribute
    window.openModal = async function () {
        // We use the ID 'metrics' section to find the button? 
        // Actually the button is inside #metrics section.
        // Let's ensure the modal logic works either way.
        const modal = document.getElementById('diagnostics-modal') || document.getElementById('metrics-modal') || document.getElementById('correction-modal');
        // Wait, diagnostics-modal is the one for metrics in previous versions.
        // Let's look for a generic modal for metrics.
        // In the LAST index.html write (id 371), we didn't explicitly see the modal HTML for metrics?
        // Step 362 output shows:
        // <div id="metrics" ...> ... <h2>NEURAL DIAGNOSTICS</h2> ... <div id="confusion-matrix-plot"> ... </div>
        // It seems the metrics are INLINE in the section #metrics, NOT in a modal.
        // So openModal might be obsolete if we just scroll to metrics?
        // Ah, the Requirement was "System Diagnostics modal".
        // But the layout in 362 shows it in a section #metrics.
        // If it's a section, we just switch to it. 
        // We have: switchSection('metrics').
        // So we load metrics when we switch to that section?
        // Let's add that hook.

        switchSection('metrics');
        await loadConfusionMatrix();
    };

    window.closeModal = function () {
        // If there was a modal...
    };

    async function loadConfusionMatrix() {
        const domain = state.domain || 'cars';
        const url = `static/metrics_data.json`;

        try {
            const res = await fetch(url);
            if (!res.ok) throw new Error("Matrix data unavailable");

            const allData = await res.json();
            const data = allData[domain];

            if (data) {
                renderPlotlyMatrix(data);
            } else {
                throw new Error("No data for this domain");
            }
        } catch (e) {
            console.warn("Could not load matrix json", e);
            document.getElementById('confusion-matrix-plot').innerHTML =
                "<div style='display:flex;justify-content:center;align-items:center;height:100%;color:var(--text-muted);'>[ NO METRICS FOUND FOR MODULE ]</div>";
        }
    }

    function renderPlotlyMatrix(data) {
        const zData = data.matrix || [];
        const xData = data.classes || [];
        const yData = data.classes || [];

        if (zData.length === 0) return;

        const plotData = [{
            z: zData,
            x: xData,
            y: yData,
            type: 'heatmap',
            colorscale: state.domain === 'fashion' ? 'YlOrRd' : 'Electric',
            hoverongaps: false
        }];

        const layout = {
            title: { text: 'CONFUSION MATRIX', font: { color: '#fff', family: 'Orbitron' } },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            xaxis: { tickfont: { color: '#a0a0a0' } },
            yaxis: { tickfont: { color: '#a0a0a0' } },
            margin: { t: 50, b: 100, l: 100, r: 50 },
            font: { family: 'Montserrat' }
        };

        const config = { responsive: true, displayModeBar: false };
        if (window.Plotly) Plotly.newPlot('confusion-matrix-plot', plotData, layout, config);
    }


    // --- FEEDBACK & UTILS ---

    async function handleFeedback(isCorrect, newLabel = null) {
        if (!state.imgBase64) return;

        const payload = {
            image_base64: state.imgBase64,
            label: state.prediction,
            is_correct: isCorrect,
            new_brand_name: newLabel
        };

        log("SENDING AUDIT DATA...");
        try {
            await fetch(`/feedback?domain=${state.domain}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            log(isCorrect ? "INTEGRITY CONFIRMED" : "CORRECTION APPLIED", true);
        } catch (e) {
            log("FEEDBACK FAILED", false, true);
        }
    }

    function submitManualCorrection() {
        if (!els.correctionInput) return;
        const val = els.correctionInput.value.trim();
        if (val) {
            handleFeedback(false, val);
            if (els.correctionModal) els.correctionModal.classList.add('hidden');
            els.correctionInput.value = "";
        }
    }

    function log(msg, success = false, error = false) {
        if (!els.statusLog) return;
        els.statusLog.innerText = msg;
        if (success) els.statusLog.style.color = "var(--success)"; // Assuming var defined
        else if (error) els.statusLog.style.color = "var(--error)";
        else els.statusLog.style.color = "#888";
    }

    function delay(ms) { return new Promise(r => setTimeout(r, ms)); }
});
