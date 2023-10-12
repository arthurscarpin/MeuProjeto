document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('alterarSenhaForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Impede o envio normal do formulário

        // Faz a requisição usando fetch
        fetch('/login_alterar_senha', {
            method: 'POST',
            body: new FormData(form)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('alerta-sucesso').textContent = data.message;
                document.getElementById('alerta-erro').textContent = '';
            } else {
                document.getElementById('alerta-erro').textContent = data.message;
                document.getElementById('alerta-sucesso').textContent = '';
            }
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
        });
    });
});