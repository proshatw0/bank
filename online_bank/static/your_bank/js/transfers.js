document.querySelector('.data-phone').addEventListener('submit', function(event) {
    event.preventDefault();
    const form = this;
    const formData = new FormData();

    formData.append('phone_number', form.querySelector('#phone_number').value);

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    document.getElementById('loading-screen').style.display = 'flex';
    document.getElementById('telephone-area').style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.2)';

    const requestOptions = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            phone_number: form.querySelector('#phone_number').value,
        })
    };

    const startTime = Date.now();

    fetch(form.action, requestOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const elapsed = Date.now() - startTime;
            const delay = Math.max(3000 - elapsed, 0);
            setTimeout(() => {
                document.getElementById('loading-screen').style.display = 'none';
                if (data.status === 'success') {
                    window.location.href = data.message;
                } else {
                    document.getElementById('telephone-area').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
                }
            }, delay);
        })
        .catch(error => {
            const elapsed = Date.now() - startTime;
            const delay = Math.max(3000 - elapsed, 0);
            setTimeout(() => {
                document.getElementById('loading-screen').style.display = 'none';
                document.getElementById('telephone-area').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
            }, delay);
        });
});