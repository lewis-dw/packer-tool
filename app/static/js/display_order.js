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




// update the corresponding input to a changed input
document.addEventListener('input', function (event) {
    const changedId = event.target.id;
    if (!changedId) {
        return; // Exit if the input does not have an ID
    }

    // Parse through the changed input
    const lastUnderscoreIndex = changedId.lastIndexOf('_');
    const input = changedId.substring(0, lastUnderscoreIndex); // Part before the last underscore
    let id = changedId.substring(lastUnderscoreIndex + 1); // Part after the last underscore

    // Determine the suffix based on the presence of 'ignore' in the ID and remove '-ignore' from the ID if present
    const suffix = id.includes('ignore') ? '' : '-ignore';
    id = id.replace('-ignore', '');

    // Construct the ID to update then try to find it
    const inputToUpdate = `${input}_${id}${suffix}`;
    const targetInput = document.getElementById(inputToUpdate);

    // If the ID exists then it means we should update the other input
    if (targetInput) {
        targetInput.value = event.target.value;
    }
});