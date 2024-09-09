document.getElementById('pesquisa_id').addEventListener('click', function() {
    const modal = document.getElementById('modal_pesquisa');
    // Alternar a visibilidade do modal
    if (modal.style.display === 'none' || modal.style.display === '') {
        modal.style.display = 'block';
    } else {
        modal.style.display = 'none';
    }
});

document.getElementById('pesquisar_btn').addEventListener('click', function() {
    const id = document.getElementById('id_input').value;
    if (id) {
        // Redireciona para a URL com os parâmetros de pesquisa
        window.location.href = `/pesquisar_gestor?pagina=1&globalId=${id}`;
    } else {
        alert('Por favor, insira um ID válido.');
    }
});



