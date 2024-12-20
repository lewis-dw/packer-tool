// Function for toggling the visibility of a div
function toggleSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.style.display = 'none');

    // Show the selected section
    const section = document.getElementById(sectionId);
    section.style.display = 'block';
}

// Function for closing a section
function closeSection() {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.style.display = 'none');
}



// submit clickup report task
function submitReport() {
    const report_url = "{{ url_for('orders.report_issue') }}";
    const sku = document.getElementById('report-product-sku').value;
    const message = document.getElementById('report-message').value;

    fetch(report_url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            sku: sku,
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').innerText = `Server response: ${data.response}`;
    })
}