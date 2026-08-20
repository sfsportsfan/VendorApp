// Animation for Progress Bar
document.addEventListener('DOMContentLoaded', function () {
    const indicator = document.getElementById('progress-indicator');
    const targetWidth = indicator.dataset.targetWidth;

    console.log('targetWidth:', targetWidth); // check this in browser console

    // Start at 0%, then transition to the real width shortly after
    indicator.style.width = '0%';

    setTimeout(() => {
        indicator.style.width = targetWidth + '%';
    }, 100); // slight delay so the browser registers the starting state first
});


document.addEventListener('DOMContentLoaded', function () {
    const loader = document.getElementById('page-loader');

    // Show loader on link clicks
    document.querySelectorAll('a, button').forEach(el => {
        el.addEventListener('click', function (e) {
            // Ignore links that open in new tab or are anchors
            if (el.target === "_blank" || el.href?.startsWith('#')) return;

            loader?.classList.remove('hidden');
        });
    });
});

window.addEventListener('load', function () {
    setTimeout(() => {
    document.getElementById('page-loader')?.classList.add('hidden');
   }, 500);
});