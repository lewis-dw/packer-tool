// List of user roles
const roles = [
    { value: "", text: "Select a role" },
    { value: "shipping", text: "Shipping" },
    { value: "purchases", text: "Purchases" },
    { value: "admin", text: "Admin" }
];

// Populate the dropdown with user role options
function populateRoles() {
    const dropdown = document.getElementById('user-role');
    dropdown.innerHTML = ""; // Clear existing options

    roles.forEach(role => {
        const option = document.createElement('option');
        option.value = role.value;
        option.textContent = role.text;
        dropdown.appendChild(option);
    });

    // Set the dropdown to the current user role from the cookie
    const userRole = getCookie("user-role");
    if (userRole) {
        dropdown.value = userRole;
    }
}





// Set the dropdown to the current user role on page load
document.addEventListener("DOMContentLoaded", function() {
    populateRoles();

    const userRole = getCookie("user-role");
    if (userRole) {
        const dropdown = document.getElementById('user-role');
        dropdown.value = userRole;
    };
});





function updateRole() {
    const dropdown = document.getElementById('user-role');
    const selectedRole = dropdown.value;
    setCookie("user-role", selectedRole, 1);

    window.location.href = `/`;
}