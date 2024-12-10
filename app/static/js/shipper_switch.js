// List of shippers
const shippers = [
    { value: "user1", text: "User 1" },
    { value: "user2", text: "User 2" },
    { value: "user3", text: "User 3" }
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



// Set a cookie
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + encodeURIComponent(value || "") + expires + "; path=/";
}

// Update the current shipper cookie
function updateShipper() {
    const dropdown = document.getElementById('current-shipper');
    const selectedShipper = dropdown.value;
    setCookie("currentShipper", selectedShipper, 1);
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
    const currentShipper = getCookie("currentShipper");
    if (currentShipper) {
        const dropdown = document.getElementById('current-shipper');
        dropdown.value = currentShipper;
    }
};
