let selectedRowId = null;

// Function to handle row click
function rowClicked(rowId) {
    // update hidden input
    selectedRowId = rowId;
    document.getElementById('row-id').value = rowId; // Update hidden input

    // remove any previously selected row
    const previouslySelectedRow = document.querySelector('.highlighted-row');
    if (previouslySelectedRow) {
        previouslySelectedRow.classList.remove('highlighted-row');
    }

    // add the highlight to the clicked row
    const currentRow = document.querySelector(`[data-row-id="${rowId}"]`);
    if (currentRow) {
        currentRow.classList.add('highlighted-row');
    }
}

// Function to handle button click
function setAction(actionType) {
    if (!selectedRowId) {
        alert("Please select a row first!");
        return;
    }
    document.getElementById('action').value = actionType; // Set action type
}