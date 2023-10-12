// Função para atualizar a tabela
function atualizarTabela(resultados) {
    let tableHtml = `
        <table>
            <thead>
                <tr>
                    <th>Placa</th>
                    <th>Status</th>
                    <th>Ação</th> <!-- Cabeçalho da coluna de ação -->
                </tr>
            </thead>
            <tbody>
    `;

    resultados.forEach((resultado) => {
        const statusColor = resultado.id_status === 1 ? '#016438' : '#c00';
        const statusText = resultado.id_status === 1 ? 'Autorizado' : (resultado.id_status === 0 ? 'Não Autorizado' : '');
        tableHtml += `
            <tr>
                <td>${resultado.placa_nome}</td>
                <td style="color: ${statusColor}; font-weight:bold;">${statusText}</td>
                <td><button class="btn-delete" data-placa="${resultado.placa_nome}">Excluir</button></td> <!-- Botão delete com atributo data para armazenar a placa -->
            </tr>
        `;
    });

    tableHtml += `
            </tbody>
        </table>
    `;

    $('#table-container').html(tableHtml);
    addDeleteHandlers();
}

// Função que define a ação dos botões Excluir
function addDeleteHandlers() {
    $('.btn-delete').click(function () {
        const placa = $(this).data('placa');
        $.ajax({
            url: `/delete/${placa}`,
            method: 'POST',
            success: function (data) {
                console.log(data.message);
                location.reload();
            },
            error: function (error) {
                console.log('Erro ao excluir veículo:', error);
            }
        });
    });
}

// Função para fazer a requisição AJAX ao clicar no botão de Pesquisar
$('#search-form').submit(function (event) {
    event.preventDefault();
    const pesquisa = $('#search').val();

    $.ajax({
        url: 'http://localhost:5000/tabela_placa',
        method: 'GET',
        data: { pesquisa },
        success: function (data) {
            atualizarTabela(data);
        },
        error: function (error) {
            console.log('Erro ao obter os dados da tabela:', error);
        }
    });
});

// Função para fazer a requisição AJAX para exibir a tabela com todos os resultados
$.ajax({
    url: 'http://localhost:5000/tabela_placa',
    method: 'GET',
    success: function (data) {
        atualizarTabela(data);
    },
    error: function (error) {
        console.log('Erro ao obter os dados da tabela:', error);
    }
});

// Função que define a ação do botão Cadastrar
const modal = document.getElementById('modal');
const cadastraPlacaButton = document.getElementById('cadastraPlaca');
const closeModalButton = document.getElementsByClassName('close')[0];

cadastraPlacaButton.onclick = function() {
    modal.style.display = 'block';
}

closeModalButton.onclick = function() {
    modal.style.display = 'none';
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}
