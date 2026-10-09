// ===== File Upload Handling =====
const uploadBox = document.getElementById('uploadBox');
const resumeInput = document.getElementById('resumeInput');
const fileInfo = document.getElementById('fileInfo');
const submitBtn = document.getElementById('submitBtn');

if (resumeInput) {
    resumeInput.addEventListener('change', handleFileSelect);
}

if (uploadBox) {
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.classList.add('dragover');
    });

    uploadBox.addEventListener('dragleave', () => {
        uploadBox.classList.remove('dragover');
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            resumeInput.files = files;
            handleFileSelect();
        }
    });
}

function handleFileSelect() {
    const file = resumeInput.files[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();

    if (!['pdf', 'docx'].includes(ext)) {
        fileInfo.textContent = '❌ Only PDF and DOCX files allowed';
        fileInfo.style.color = '#c0392b';
        submitBtn.disabled = true;
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        fileInfo.textContent = '❌ File too large (max 5 MB)';
        fileInfo.style.color = '#c0392b';
        submitBtn.disabled = true;
        return;
    }

    fileInfo.textContent = `✅ ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    fileInfo.style.color = '#27ae60';
    submitBtn.disabled = false;
}

const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', () => {
        submitBtn.textContent = '⏳ Analyzing...';
        submitBtn.disabled = true;
    });
}