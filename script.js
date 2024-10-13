document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form');
    const loaderContainer = document.querySelector('.loader-container');
    const inputField = document.getElementById('link');

    inputField.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent form submission
            
            const input = inputField.value.trim();
            if (input !== '') {
                loaderContainer.classList.add('show-animation'); // Show animation

                // Simulate loading for demonstration purposes
                setTimeout(function () {
                    loaderContainer.classList.remove('show-animation'); // Hide animation
                }, 3000); // Adjust the time according to your actual loading time
            }
        }
    });
});