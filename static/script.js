document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const pdfFileInput = document.getElementById('pdfFile');
    const messageDiv = document.getElementById('message');
    const analyzeButton = document.getElementById('analyzeButton');

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData();
        formData.append('pdf', pdfFileInput.files[0]);

        fetch('/save_n_examine_doc', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                messageDiv.innerHTML = data.error;
                analyzeButton.style.display = 'none';
            } else {
                messageDiv.innerHTML = data.result;
                analyzeButton.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageDiv.textContent = 'An unexpected error occurred.';
        });
    });

    analyzeButton.addEventListener('click', function() {
        fetch('/process-document', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.result) {
                messageDiv.innerHTML = parseAndRenderMessage(data.result);
            } else {
                messageDiv.textContent = 'Failed to process document.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageDiv.textContent = 'An unexpected error occurred.';
        });
    });

    function parseAndRenderMessage(message) {
        const lines = message.split('\n');
        let htmlContent = '';
        
        lines.forEach(line => {
            if (line.startsWith('# ')) {
                htmlContent += `<h1 class="text-xl font-bold my-2">${line.slice(2)}</h1>`;
            } else if (line.startsWith('## ')) {
                htmlContent += `<h2 class="text-lg font-semibold my-2">${line.slice(3)}</h2>`;
            } else if (line.startsWith('* ')) {

                htmlContent += `<li>${line.slice(2)}</li>`;
            } else {
                if (htmlContent.endsWith('</ul>')) {
                    htmlContent += '</ul>';
                }
            }
            htmlContent += `<p class="my-2 text-red-600	">${line}</p>`;
        });

        if (htmlContent.endsWith('</ul>')) {
            htmlContent += '</ul>';
        }

        return htmlContent;
    }
});
