let selectedRowID = null;

// Function to handle row click
function rowClicked(rowID) {
    // update hidden input
    selectedRowID = rowID;
    document.getElementById('row-id').value = rowID;

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
    if (!selectedRowID) {
        alert("Please select a row first!");
        return false;
    }
}