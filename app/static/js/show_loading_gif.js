// event listener for when the page is loaded
window.addEventListener('pageshow', function (event) {
    // Check if the page is loaded from the cache (persisted state)
    if (event.persisted) {
        document.getElementById('loading-gif').style.display = 'none'; // Hide the loading div
        document.body.style.overflow = ''; // Re-enable scrolling
    }
});

// need some separate code for setting the gif to be visible due to display flexbox
function showGif() {
    const section = document.getElementById('loading-gif');
    section.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}