function toggleDropdown() {
    var dropdown = document.getElementById('dropdownMenu');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

window.onclick = function(event) {
    if (!event.target.matches('.profile-button') && !event.target.matches('.profile-button *')) {
        var dropdowns = document.getElementsByClassName('dropdown-menu');
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.style.display === 'block') {
                openDropdown.style.display = 'none';
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
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

    const csrftoken = getCookie('csrftoken');


    function sendRequest(typeCard, numberCard) {
        const params = {
            type_card: typeCard,
            number_card: numberCard
        };

        fetch('/your_bank/get-card-info/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(params)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            document.getElementById('type').value = data.message.type;
            document.getElementById('balance').value = data.message.balance;
            document.getElementById('number_hidden').value = data.message.number.replace(/(\d{4})(?=\d)/g, '$1 ');
            document.getElementById('number').value = data.message.number.replace(/\d{12}(\d{4})/, '**** **** **** $1');
            document.getElementById('date_hidden').value = data.message.date;
            document.getElementById('cvv_hidden').value = data.message.cvv;
            if (data.message.is_frozen){
                document.getElementById('freez').textContent = 'Разморозить';
            }
            document.getElementById('overlay').style.display = 'flex'
        })
        .catch(error => console.error('Error:', error));
    }

    const buttons = document.querySelectorAll('.debit-card');
    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const typeCard = this.querySelector('.type-card').innerText.trim();
            const numberCard = this.querySelector('.number-card').innerText.trim();
            sendRequest(typeCard, numberCard);
        });
    });
});

function closeOverlay() {
    document.getElementById("overlay").style.display = "none";
    document.getElementById('button_hidden').innerText = 'Показать'
}

function toggleRequisites() {
    a = document.getElementById('number').value;
    document.getElementById('number').value = document.getElementById('number_hidden').value;
    document.getElementById('number_hidden').value = a;

    a = document.getElementById('date').value;
    document.getElementById('date').value = document.getElementById('date_hidden').value;
    document.getElementById('date_hidden').value = a;

    a = document.getElementById('cvv').value;
    document.getElementById('cvv').value = document.getElementById('cvv_hidden').value;
    document.getElementById('cvv_hidden').value = a;

    if (document.getElementById('button_hidden').innerText == 'Показать'){
        document.getElementById('button_hidden').innerText = 'Скрыть'
    } else{
        document.getElementById('button_hidden').innerText = 'Показать'
    }
}