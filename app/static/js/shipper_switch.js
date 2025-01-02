// List of shippers
const shippers = [
    { value: "", text: "Select a shipper" },
    { value: "josh", text: "Josh" },
    { value: "webby", text: "Webby" },
    { value: "hayden", text: "Hayden" },
    { value: "matt", text: "Matt" },
    { value: "other", text: "Other" }
];

// Populate the dropdown with shipper options
function populateShippers() {
    const dropdown = document.getElementById('current-shipper');
    dropdown.innerHTML = ""; // Clear existing options

    shippers.forEach(shipper => {
        const option = document.createElement('option');
        option.value = shipper.value;
        option.textContent = shipper.text;
        dropdown.appendChild(option);
    });

    // Set the dropdown to the current shipper from the cookie
    const currentShipper = getCookie("currentShipper");
    if (currentShipper) {
        dropdown.value = currentShipper;
    }
}





// Send an AJAX request to Flask backend to log the event
function logEvent(logLoc, eventMessage) {
    fetch('/log_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ location: logLoc, event: eventMessage }),
    }).then(response => {
        if (!response.ok) {
            console.error('Failed to log event');
        }
    }).catch(error => {
        console.error('Error logging event:', error);
    });
}





// Set the dropdown to the current shipper on page load
document.addEventListener("DOMContentLoaded", function() {
    // First populate the shipper options
    populateShippers();

    // Then change the option currently selected
    const currentShipper = getCookie("current_shipper");
    if (currentShipper) {
        const dropdown = document.getElementById('current-shipper');
        dropdown.value = currentShipper;
    }
});





// Update the current shipper cookie
function updateShipper() {
    const dropdown = document.getElementById('current-shipper');
    const selectedShipper = dropdown.value;
    setCookie("current_shipper", selectedShipper, 1);

    // Log the shipper update event
    logEvent(`actions`, `Shipper updated to: ${selectedShipper}`);
}