const inputs = document.querySelectorAll('.input-pin');

inputs.forEach((input, index) => {
    input.addEventListener('focus', () => {
        input.select();
    });

    input.addEventListener('input', (event) => {
        const value = event.target.value;

        if (value && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }
    });

    input.addEventListener('keydown', (event) => {
        if (event.key === 'Backspace' && !input.value && index > 0) {
            inputs[index - 1].focus();
        }
    });
});
var inputAreas = document.querySelectorAll('.input-area-pin');
var form = document.getElementById('pin-form');
form.addEventListener('submit', function(event) {
    event.preventDefault(); 

    inputAreas.forEach(inputArea => {
        inputArea.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.25)';
    });

    var formData = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка отправки формы');
        }
        return response.json(); 
    })
    .then(data => {
        if (data.success) {
            window.location.href = data.next_url;
        } else {
            let arr = [data.one, data.two, data.three, data.four]
            for (let i = 0; i < arr.length; i++) {
                if (arr[i] === true) {
                    inputAreas[i].style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
                }
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

function checkRedirect() {
    fetch('/login/check-redirect/')
        .then(response => response.json())
        .then(data => {
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        });
}

setInterval(checkRedirect, 5000);