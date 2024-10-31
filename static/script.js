document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const pdfFileInput = document.getElementById('pdfFile');
    const messageDiv = document.getElementById('message');
    const analyzeButton = document.getElementById('analyzeButton');
    const loadingSpinner = document.getElementById('loadingSpinner');

    function toggleLoading(isLoading) {
        loadingSpinner.style.display = isLoading ? 'block' : 'none';
    }

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();
        toggleLoading(true);

        const formData = new FormData();
        formData.append('pdf', pdfFileInput.files[0]);

        fetch('/process-msds', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            toggleLoading(false);
            if (data.error) {
                messageDiv.innerHTML = data.error;
                analyzeButton.style.display = 'none';
            } else {
                messageDiv.innerHTML = data.Response;
                analyzeButton.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageDiv.textContent = 'An unexpected error occurred.';
            toggleLoading(false);
        });
    });

    analyzeButton.addEventListener('click', function() {
        toggleLoading(true);

        fetch('/analyze-msds', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            toggleLoading(false);
            if (data.Response) {
                messageDiv.innerHTML = parseAndRenderMessage(data.Response);
                analyzeButton.style.display = 'none';
            } else {
                messageDiv.textContent = 'Failed to process document.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageDiv.textContent = 'An unexpected error occurred.';
            toggleLoading(false);
        });
    });

    function parseAndRenderMessage(message) {
        const lines = message.split('\n');
        let htmlContent = '';
        
        lines.forEach(line => {
            if (line.startsWith('# ')) {
                htmlContent += `<h1>${line.slice(2)}</h1>`;
            } else if (line.startsWith('## ')) {
                htmlContent += `<h2>${line.slice(3)}</h2>`;
            } else if (line.startsWith('* ')) {
                htmlContent += `<li>${line.slice(2)}</li>`;
            } else {
                htmlContent += `<p>${line}</p>`;
            }
        });

        return htmlContent;
    }
});
