const eyeButton = document.getElementById('eye');
const passwordInput = document.getElementById('password-in');

let isButtonPressed = false;

eyeButton.addEventListener('mousedown', () => {
    isButtonPressed = true;
    passwordInput.type = 'text';
});

eyeButton.addEventListener('mouseup', () => {
    isButtonPressed = false;
    passwordInput.type = 'password';
});

eyeButton.addEventListener('mouseleave', () => {
    if (isButtonPressed) {
        isButtonPressed = false;
        passwordInput.type = 'password';
    }
});

var error_element;
var form = document.getElementById('login-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault(); 
        document.getElementById('error').textContent = ""
        if (error_element != null){
            document.getElementById(error_element).style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.25)';
        }
        
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
                document.getElementById('error').textContent = data.error
                error_element=data.error_elemenet
                document.getElementById(error_element).style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
            }
        })
    });
