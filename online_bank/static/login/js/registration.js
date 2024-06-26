var error_element;
var error_email;
var form = document.getElementById('registration-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault(); 
        document.getElementById('error').textContent = ""
        if (error_element != null){
            document.getElementById(error_element).style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.25)';
            if (error_email != null){
                document.getElementById(error_email).style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.25)';
            }
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
                document.getElementById('error').textContent = 'Ошибка отправки формы, перезагрузите страницу';
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
                if (data.or_error_elemenet == 'email'){
                    error_email = 'email'
                    document.getElementById('email').style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
                }
                document.getElementById(error_element).style.boxShadow = '0 0 10px rgba(144, 0, 32, 1)';
            }
        })
    });