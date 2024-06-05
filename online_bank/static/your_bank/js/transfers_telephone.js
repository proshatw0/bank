document.querySelector('.data-debit').addEventListener('submit', function(event) {
    event.preventDefault();
    const form = this;
    const formData = new FormData();

    formData.append('phone', form.querySelector('#phone').value);
    formData.append('subscription', form.querySelector('#card-select option:checked').value);
    formData.append('cost', form.querySelector('#cost').value);
    console.log(form.querySelector('#phone').value)
    console.log(form.querySelector('#card-select option:checked').value)
    console.log(form.querySelector('#cost').value)

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    document.getElementById('loading-screen').style.display = 'flex';
    document.getElementById('error').textContent = '';
    document.getElementById('cost').style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.25)';

    const requestOptions = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            phone: form.querySelector('#phone').value,
            subscription: form.querySelector('#card-select option:checked').value,
            cost: form.querySelector('#cost').value
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
                    document.getElementById('accountInfo').textContent = data.message.accountInfo;
                    document.getElementById('amountInfo').textContent = data.message.amountInfo;
                    document.getElementById('bankLogo').textContent = data.message.bankLogo;
                    document.getElementById('transactionAmount').textContent = data.message.transactionAmount;
                    document.getElementById('cardNumber').textContent = data.message.cardNumber;
                    document.getElementById("transactionModal").style.display = "block";
                } else {
                    document.getElementById('error').textContent = data.message;
                    document.getElementById('number_card').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
                    document.getElementById('cost').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
                }
            }, delay);
        })
        .catch(error => {
            const elapsed = Date.now() - startTime;
            const delay = Math.max(3000 - elapsed, 0);
            setTimeout(() => {
                document.getElementById('loading-screen').style.display = 'none';
                document.getElementById('error').textContent = data.message;
                document.getElementById('cost').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
            }, delay);
        });
});