const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const port = 3000; // Escolha a porta que preferir

app.get('/search/:anime', async (req, res) => {
    const animeName = req.params.anime.trim().toLowerCase();
    
    if (animeName) {
        const searchUrl = `https://animefire.plus/pesquisar/${encodeURIComponent(animeName)}`;

        try {
            const response = await axios.get(searchUrl);
            const $ = cheerio.load(response.data);

            const animes = $('article.cardUltimosEps');
            let animeList = [];

            if (animes.length > 0) {
                animes.each((index, anime) => {
                    const title = $(anime).find('h3.animeTitle').text().trim();
                    const link = $(anime).find('a').attr('href');
                    const fullLink = link.startsWith('http') ? link : `https://animefire.plus${link}`;
                    
                    animeList.push({
                        title: title,
                        link: fullLink
                    });
                });

                res.json({ status: 'success', results: animeList });
            } else {
                res.json({ status: 'no_results', message: 'Nenhum anime encontrado.' });
            }
        } catch (error) {
            res.status(500).json({ status: 'error', message: 'Erro ao buscar os animes.' });
        }
    } else {
        res.status(400).json({ status: 'error', message: 'Nome do anime inválido.' });
    }
});

app.listen(port, () => {
    console.log(`Servidor rodando em http://localhost:${port}`);
});
