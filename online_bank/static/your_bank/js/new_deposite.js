document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('card-select').addEventListener('change', function() {
        const selectedCard = this.value;
        console.log(selectedCard);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        document.getElementById('error').textContent = '';

        fetch('/your_bank/update-deposite-info/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ deposite_name: selectedCard })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('procent').innerText = `Процентная ставка: ${data.procent} %`;
            document.getElementById('period').innerText = `Период: ${data.period} месяцев`;
            document.getElementById('close').innerText = `Возможность досрочного закрытия: ${data.close}`;
        })
        .catch(error => {
            document.getElementById('error').textContent = 'Error fetching card info';
            console.error('Error fetching card info:', error);
        });
    });
});

document.querySelector('.data-debit').addEventListener('submit', function(event) {
    event.preventDefault();
    const form = this;
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    document.getElementById('loading-screen').style.display = 'flex';
    document.getElementById('error').textContent = '';

    const requestOptions = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    };

    const startTime = Date.now();

    let requestCompleted = false;

    fetch(form.action, requestOptions)
        .then(response => response.json())
        .then(data => {
            requestCompleted = true;
            const elapsed = Date.now() - startTime;
            const delay = Math.max(3000 - elapsed, 0);
            setTimeout(() => {
                document.getElementById('loading-screen').style.display = 'none';
                if (data.status === 'success') {
                    window.location.href = data.message;
                } else {
                    document.getElementById('error').textContent = data.message;
                }
            }, delay);
        })
        .catch(error => {
            requestCompleted = true;
            const elapsed = Date.now() - startTime;
            const delay = Math.max(3000 - elapsed, 0);
            setTimeout(() => {
                document.getElementById('loading-screen').style.display = 'none';
                document.getElementById('error').textContent = 'Произошла ошибка при отправке данных';
            }, delay);
        });

    setTimeout(() => {
        if (!requestCompleted) {
            const checkCompletion = setInterval(() => {
                if (requestCompleted) {
                    clearInterval(checkCompletion);
                    document.getElementById('loading-screen').style.display = 'none';
                }
            }, 100);
        }
    }, 3000);
});