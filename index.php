<?php
require 'vendor/autoload.php';

use Slim\Factory\AppFactory;

// Criar a instância do aplicativo Slim
$app = AppFactory::create();

// Configurar middleware de roteamento
$app->get('/extrair-informacoes', function ($request, $response) {
    $url = "https://canaisplay.com/categoria/futebol-ao-vivo/";

    // Usar a função file_get_contents com stream_context_create para evitar erros de SSL
    $context = stream_context_create(['ssl' => ['verify_peer' => false, 'verify_peer_name' => false]]);
    $html = file_get_contents($url, false, $context);

    $dom = new DOMDocument;
    @$dom->loadHTML($html);

    $xpath = new DOMXPath($dom);

    // Encontrar os títulos
    $titles = $xpath->query('//div[contains(@class, "bg-black")]/a');
    $titleArray = [];

    foreach ($titles as $title) {
        $titleArray[] = $title->nodeValue;
    }

    // Encontrar os URLs
    $urls = $xpath->query('//div[contains(@class, "bg-black")]/a/@href');
    $urlArray = [];

    foreach ($urls as $url) {
        $urlArray[] = $url->nodeValue;
    }

    $result = [];

    for ($i = 0; $i < count($titleArray); $i++) {
        $result[] = [
            'title' => $titleArray[$i],
            'url' => $urlArray[$i],
        ];
    }

    // Configurar o cabeçalho Content-Type para JSON
    $response = $response->withHeader('Content-Type', 'application/json');

    // Retornar uma resposta JSON
    $response->getBody()->write(json_encode($result));

    return $response;
});

// Executar o aplicativo Slim
$app->run();
