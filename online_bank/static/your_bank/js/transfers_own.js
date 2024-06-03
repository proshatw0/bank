document.querySelector('.data-debit').addEventListener('submit', function(event) {
    event.preventDefault();
    const form = this;

    const subscription1 = form.querySelector('#card-select1 option:checked').value;
    const subscription2 = form.querySelector('#card-select2 option:checked').value;
    const cost = form.querySelector('#cost').value;

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    document.getElementById('loading-screen').style.display = 'flex';
    document.getElementById('error').textContent = '';
    document.getElementById('card-select1').style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.25)';
    document.getElementById('card-select2').style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.25)';
    document.getElementById('cost').style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.25)';

    const formData = new FormData();
    formData.append('subscription1', subscription1);
    formData.append('subscription2', subscription2);
    formData.append('cost', cost);

    const requestOptions = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Accept': 'application/json'
        },
        body: formData
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
                    document.getElementById('accountInfo').textContent = data.message.accountInfo;
                    document.getElementById('amountInfo').textContent = data.message.amountInfo;
                    document.getElementById('transactionAmount').textContent = data.message.transactionAmount;
                    document.getElementById('cardNumber').textContent = data.message.cardNumber;
                    document.getElementById("transactionModal").style.display = "block";
                } else {
                    document.getElementById('error').textContent = data.message;
                    document.getElementById('card-select1').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
                    document.getElementById('card-select2').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
                    document.getElementById('cost').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
                }
            }, delay);
        })
        .catch(error => {
            const elapsed = Date.now() - startTime;
            const delay = Math.max(3000 - elapsed, 0);
            setTimeout(() => {
                document.getElementById('loading-screen').style.display = 'none';
                document.getElementById('error').textContent = 'Произошла ошибка при отправке данных';
                document.getElementById('card-select1').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
                document.getElementById('card-select2').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
                document.getElementById('cost').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
            }, delay);
        });
});