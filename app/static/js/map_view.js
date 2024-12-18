function showAddress(address) {
    // format the address
    const encodedAddress = encodeURIComponent(address);

    // construct url and open in new tab
    const mapsUrl = `https://www.google.com/maps?q=${encodedAddress}`;
    window.open(mapsUrl, '_blank');
}
