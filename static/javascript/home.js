// Exibindo os dados JSON na tela
function exibirPlaca(placa) {
    var placaDiv = document.getElementById("placa-div");
    
    if (placa.id) {
        var idStatusText = "";
        var idStatusClass = "";

        if (placa.id_status === 1) {
            idStatusText = "Autorizado";
            idStatusClass = "status-autorizado";
        } else if (placa.id_status === 0 || placa.id_status === null) {
            idStatusText = "Não autorizado";
            idStatusClass = "status-nao-autorizado";
        }

        placaDiv.innerHTML = 
            "<p>Placa: <span class='placa-var'>" + placa.Placa + "</span></p>" +
            "<p>Data Hora: <span class='data-var'>" + placa["Data Hora"] + "</span></p>" +
            "<p>Status: <span class='status-var " + idStatusClass + "'>" + idStatusText + "</span></p>";
    } else {
        placaDiv.innerHTML = "<p>Nenhuma placa encontrada</p>";
    }
}

// Fazer a requisição AJAX e obter os dados JSON
function obterPlacaMaisRecente() {
    var request = new XMLHttpRequest();
    request.open('GET', 'http://localhost:5000/maxid_placa', true);
    request.onload = function() {
        if (this.status >= 200 && this.status < 400) {
            var data = JSON.parse(this.response);
            exibirPlaca(data);
        } else {
            console.log("Erro ao obter a placa");
        }
    };
    request.onerror = function() {
        console.log("Erro na requisição");
    };
    request.send();
}

obterPlacaMaisRecente();
setInterval(obterPlacaMaisRecente, 1000);
