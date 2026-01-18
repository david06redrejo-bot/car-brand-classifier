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
        correctionInput: document.getElementById('correction-input')
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
        els.domainGrid.addEventListener('click', (e) => {
            const card = e.target.closest('.cyber-card');
            if (card) selectDomain(card.dataset.domain);
        });

        // Navigation
        els.navItems.forEach(item => {
            item.addEventListener('click', () => switchSection(item.dataset.target));
        });

        els.resetBtn.addEventListener('click', resetSystem);
        els.initBtn.addEventListener('click', () => switchSection('playground'));

        // File Handling
        els.dropZone.addEventListener('click', () => els.fileInput.click());
        els.fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));

        // Drag & Drop
        els.dropZone.addEventListener('dragover', (e) => { e.preventDefault(); els.dropZone.style.borderColor = 'var(--accent)'; });
        els.dropZone.addEventListener('dragleave', (e) => { els.dropZone.style.borderColor = ''; });
        els.dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            els.dropZone.style.borderColor = '';
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        });

        // Feedback
        els.feedConfirm.addEventListener('click', () => handleFeedback(true));
        els.feedReject.addEventListener('click', () => {
            els.correctionModal.classList.remove('hidden');
        });

        els.submitCorrection.addEventListener('click', submitManualCorrection);
        els.cancelCorrection.addEventListener('click', () => els.correctionModal.classList.add('hidden'));
    }

    // --- LOGIC ---

    function selectDomain(domain) {
        state.domain = domain;
        document.body.className = `theme-${domain}`;

        const conf = DOMAIN_DATA[domain];
        if (conf) {
            els.moduleTitle.innerText = conf.title;
            els.moduleSub.innerText = conf.sub;
            els.heroBg.style.backgroundImage = `url('${conf.bg}')`;
        }

        // Transition
        els.domainSelector.classList.add('hidden');
        els.appInterface.classList.remove('hidden');
        log(`MODULE ${domain.toUpperCase()} ONLINE`);
    }

    function switchSection(targetId) {
        document.querySelectorAll('.cyber-section').forEach(sec => sec.classList.remove('active'));
        document.getElementById(targetId).classList.add('active');

        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        document.querySelector(`.nav-item[data-target="${targetId}"]`).classList.add('active');
    }

    function resetSystem() {
        state.domain = null;
        state.imgBase64 = null;
        state.prediction = null;

        els.fileInput.value = '';
        els.previewImg.classList.add('hidden');
        els.resultContent.classList.add('hidden');
        els.scanLine.classList.add('hidden');

        els.appInterface.classList.add('hidden');
        els.domainSelector.classList.remove('hidden');
        document.body.className = 'theme-default';
    }

    function handleFile(file) {
        if (!file || !file.type.startsWith('image/')) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            state.imgBase64 = e.target.result;
            els.previewImg.src = state.imgBase64;
            els.previewImg.classList.remove('hidden');
            els.scanLine.classList.remove('hidden'); // Start scan animation

            // Hide previous results
            els.resultContent.classList.add('hidden');

            processImage(file);
        };
        reader.readAsDataURL(file);
    }

    async function processImage(file) {
        log("UPLOADING DATA PACKET...");
        const formData = new FormData();
        formData.append('file', file);

        try {
            await delay(800); // UI Effect
            log("ANALYZING NEURAL PATTERNS...");

            const res = await fetch(`/predict?domain=${state.domain}`, {
                method: 'POST',
                body: formData
            });

            const data = await res.json();

            els.scanLine.classList.add('hidden'); // Stop scan

            if (res.ok) {
                displayResult(data);
                log("IDENTIFICATION SUCCESSFUL", true);
            } else {
                log(`ERROR: ${data.detail}`, false, true);
            }

        } catch (e) {
            els.scanLine.classList.add('hidden');
            log("CONNECTION FAILURE", false, true);
            console.error(e);
        }
    }

    function displayResult(data) {
        state.prediction = data.label;
        els.resultContent.classList.remove('hidden');
        els.resultLabel.innerText = data.label.toUpperCase();

        let conf = data.confidence;
        // Handle float vs string
        if (conf <= 1.0) conf = conf * 100;
        conf = Math.round(conf);

        els.confVal.innerText = `${conf}%`;
        els.confFill.style.width = `${conf}%`;
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
        const val = els.correctionInput.value.trim();
        if (val) {
            handleFeedback(false, val);
            els.correctionModal.classList.add('hidden');
            els.correctionInput.value = "";
        }
    }

    function log(msg, success = false, error = false) {
        els.statusLog.innerText = msg;
        if (success) els.statusLog.style.color = "var(--neon-green)";
        else if (error) els.statusLog.style.color = "var(--neon-red)";
        else els.statusLog.style.color = "#888";
    }

    function delay(ms) { return new Promise(r => setTimeout(r, ms)); }
});
