function addParcel() {
    // get all parcels
    const allParcels = document.getElementById("all-parcels");
    const parcels = document.querySelectorAll(".parcel");


    // find the ID of the last parcel and extract the last part of the ID which will be the index
    const lastParcelId = parcels[parcels.length - 1].id;
    const lastIndex = parseInt(lastParcelId.split('_').pop(), 10);

    // Calculate the new index
    const nextIndex = lastIndex + 1;


    // Clone the last parcel as a template
    const lastParcel = parcels[parcels.length - 1];
    const newParcel = lastParcel.cloneNode(true);

    // Update the cloned parcel's attributes
    newParcel.id = `parcel_${nextIndex}`; // Update the new parcel's ID
    newParcel.querySelectorAll("input").forEach(input => {
        // for each input field we need to find the base name of it and remove the id to reconstruct it with the new id
        const lastUnderscoreIndex = input.name.lastIndexOf('_');
        const baseName = input.name.substring(0, lastUnderscoreIndex);

        // set new values
        input.name = `${baseName}_${nextIndex}`;
        input.id = `${baseName}_${nextIndex}`;
        input.value = "1";
    });


    // Append the new parcel to the container
    allParcels.appendChild(newParcel);
}


function removeParcel(button) {
    const parcel = button.closest(".parcel");

    // Ensure at least one parcel remains
    if (document.querySelectorAll(".parcel").length > 1) {
        parcel.remove(); // Remove the parcel
    } else {
        alert("At least one parcel is required.");
    }
}
