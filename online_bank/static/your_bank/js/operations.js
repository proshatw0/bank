function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function createTransaction(name, amount) {
    const transaction = document.createElement('div');
    transaction.className = 'transaction';

    const icon = document.createElement('div');
    icon.className = 'transaction-icon';

    const description = document.createElement('div');
    description.textContent = 'Перевод';

    const nameElement = document.createElement('div');
    nameElement.textContent = name;

    const amountElement = document.createElement('div');
    amountElement.textContent = `${amount} ₽`;

    transaction.appendChild(icon);
    transaction.appendChild(description);
    transaction.appendChild(nameElement);
    transaction.appendChild(amountElement);

    return transaction;
}

function loadTransactions() {
    document.getElementById('loading-screen').style.display = 'flex'; 
    const token = getCookie('csrftoken');

    fetch('/your_bank/operations/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': token
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        const transactionList = document.getElementById('transaction-list');
        data.reverse();
        data.forEach(item => {
            if (item.subscription){
                na = item.subscription
            } else {
                na = 'Сберегательный'
            }
            let nam = `${na} ${item.name.slice(-4)}`;
            const transaction = createTransaction(nam, item.amount);
            transactionList.appendChild(transaction);
        });
        document.getElementById('loading-screen').style.display = 'none'; 
    })
    .catch(error => console.error('Error loading transactions:', error));
}

window.onload = loadTransactions();