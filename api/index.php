<?php

// Verifica se a requisição é do tipo POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Recebe os dados do POST
    $novoItem = array(
        'tvg-name' => $_POST['Título'],
        'tvg-logo' => $_POST['logo'],
        'group-title' => $_POST['categoria'],
        'url' => $_POST['URL'],
        'senha' => $_POST['senha'],
    );

    // Caminho do arquivo JSON
    $arquivoJSON = 'TioChannels.json';

    // Lê o conteúdo do arquivo JSON existente
    $jsonContent = file_get_contents($arquivoJSON);

    // Converte o JSON para array PHP
    $data = json_decode($jsonContent, true);

    // Adiciona o novo item ao array
    $data[] = $novoItem;

    // Converte de volta para JSON com formatação e caracteres Unicode não escapados
    $jsonNovo = json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);

    // Escreve o JSON atualizado de volta ao arquivo
    file_put_contents($arquivoJSON, $jsonNovo);

    // Mensagem de sucesso
    echo "Item adicionado com sucesso!";
} else {
    // Se a requisição não for POST, exibe uma mensagem de erro
    echo "Acesso negado.";
}

?>
