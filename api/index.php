<?php

require 'vendor/autoload.php'; // Certifique-se de que o autoload está correto

use SimpleHtmlDom\HtmlWeb;

function searchAnime($searchTerm) {
    // Converter o termo de busca para minúsculas
    $searchTerm = strtolower($searchTerm);
    $searchUrl = "https://animefire.plus/pesquisar/" . urlencode($searchTerm);

    // Inicializar o Simple HTML DOM
    $client = new HtmlWeb();
    $html = $client->load($searchUrl);

    // Verificar se a página foi carregada corretamente
    if (!$html) {
        return ['error' => 'Não foi possível carregar a página'];
    }

    $animeList = [];

    // Puxar os artigos com as informações dos animes
    foreach ($html->find('article.cardUltimosEps') as $anime) {
        $title = $anime->find('h3.animeTitle', 0)->plaintext ?? 'Sem título';
        $link = $anime->find('a', 0)->href ?? '';
        $fullLink = (strpos($link, 'http') === 0) ? $link : 'https://animefire.plus' . $link;

        $animeList[] = [
            'title' => trim($title),
            'link' => $fullLink
        ];
    }

    return $animeList;
}

// Exemplo de uso da API
header('Content-Type: application/json');
$searchTerm = isset($_GET['q']) ? $_GET['q'] : 'Naruto';
$animes = searchAnime($searchTerm);
echo json_encode($animes, JSON_PRETTY_PRINT);
