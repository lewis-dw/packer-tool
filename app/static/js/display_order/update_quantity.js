let isUpdating = false;
document.addEventListener('input', function (event) {
    // Exit if updates are in progress (to avoid re triggering this recursively)
    if (isUpdating) return;
    isUpdating = true;

    // Get the group and index for the changed input
    const group = event.target.dataset.group;
    const product_id = event.target.dataset.product_id;
    if (!group || !product_id) return;

    // find all inputs with the same group and index and for each input that isnt the changed one, update with the new value
    const newValue = parseFloat(event.target.value) || 0;
    document.querySelectorAll(`input[data-group="${group}"][data-product_id="${product_id}"]`).forEach(input => {
        if (input !== event.target) input.value = newValue;
    });

    // If the group is quantity then we want to update the related quantity in the items to the new value multiplied by the number per parent
    if (group == 'quantity') {
        document.querySelectorAll(`input[id="item-qty"][data-product_id="${product_id}"]`).forEach(input => {
            const perOneParent = parseFloat(input.dataset.per_one_parent) || 1;
            input.value = newValue * perOneParent;
        });
    };

    // Reset the flag after updates
    isUpdating = false;
});