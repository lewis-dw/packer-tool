// List of shippers
const shippers = [
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
function logEvent(eventName) {
    fetch('/log_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ event: eventName }),
    }).then(response => {
        if (!response.ok) {
            console.error('Failed to log event');
        }
    }).catch(error => {
        console.error('Error logging event:', error);
    });
}



// Set a cookie
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    value = encodeURIComponent(value || "");
    document.cookie = `${name}=${value};${expires};path=/`;
}

// Update the current shipper cookie
function updateShipper() {
    const dropdown = document.getElementById('current-shipper');
    const selectedShipper = dropdown.value;
    setCookie("current_shipper", selectedShipper, 1);

    // Log the shipper update event
    logEvent(`Shipper updated to: ${selectedShipper}`);
}



// Get a cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
    return null;
}

// Set the dropdown to the current shipper on page load
window.onload = function() {
    // First populate the shipper options
    populateShippers();

    // Then change the option currently selected
    const currentShipper = getCookie("current_shipper");
    if (currentShipper) {
        const dropdown = document.getElementById('current-shipper');
        dropdown.value = currentShipper;
    }
};
