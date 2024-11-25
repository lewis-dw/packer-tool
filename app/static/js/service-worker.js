const CACHE_NAME = 'packer-tool-pwa-cache-v1';
const STATIC_CACHE = [
    // Homepage
    '/',

    // icons
    '/static/icons/driftworks_800x800.png',
    '/static/icons/driftworks_512x512.png',
    '/static/icons/driftworks_192x192.png',
    '/static/icons/driftworks_48x48.png',
];

// Install event: Cache all essential static files
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('Caching static assets');
            return cache.addAll(STATIC_CACHE);
        })
    );
});

// Activate event: Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        console.log('Deleting old cache:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Fetch event: Serve cached resources or fetch from network
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Use cache-first strategy for static files
    if (STATIC_CACHE.some((file) => url.pathname.endsWith(file))) {
        event.respondWith(
            caches.match(event.request).then((response) => {
                return (
                    response ||
                    fetch(event.request).then((networkResponse) => {
                        return caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, networkResponse.clone());
                            return networkResponse;
                        });
                    })
                );
            })
        );
    } else {
        // Use network-first strategy for dynamic content
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, response.clone());
                        return response;
                    });
                })
                .catch(() => caches.match(event.request)) // Fallback to cache if offline
        );
    }
});
