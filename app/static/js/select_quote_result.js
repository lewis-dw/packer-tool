let selectedRowId = null;

// Function to handle row click
function rowClicked(rowID, courier, shipping_code, sat_indicator, cost) {
    // update hidden values
    selectedRowId = rowID;
    document.getElementById('courier').value = courier;
    document.getElementById('shipping-code').value = shipping_code;
    document.getElementById('sat-indicator').value = sat_indicator;
    document.getElementById('cost').value = cost;


    // remove any previously selected row
    const previouslySelectedRow = document.querySelector('.highlighted-row');
    if (previouslySelectedRow) {
        previouslySelectedRow.classList.remove('highlighted-row');
    }

    // add the highlight to the clicked row
    const currentRow = document.querySelector(`[data-row-id="${rowID}"]`);
    if (currentRow) {
        currentRow.classList.add('highlighted-row');
    }
}

// Function to handle button click
function setAction(actionType) {
    // save the action type pressed
    document.getElementById('action').value = actionType;

    // alert user if no row is selected
    if (!selectedRowId) {
        alert("Please select a row first!");
        return false;
    }

    // if it has proceeded fine then show loading gif
    showGif()
}