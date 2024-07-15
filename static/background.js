document.addEventListener('DOMContentLoaded', () => {
    const images = [
        '/static/images/cerveja.png',
        '/static/images/garrafa.png',
        '/static/images/lata.png',
        '/static/images/cevada.png',
        '/static/images/lupulo.png'
    ];

    const imageWidth = 50;
    const imageHeight = 50;
    const numCols = Math.ceil(window.innerWidth / imageWidth);
    const numRows = Math.ceil(window.innerHeight / imageHeight);
    const totalImages = numCols * numRows;

    function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    function saveImageArrangement(arrangement) {
        localStorage.setItem('backgroundImageArrangement', JSON.stringify(arrangement));
    }

    function loadImageArrangement() {
        const arrangement = localStorage.getItem('backgroundImageArrangement');
        return arrangement ? JSON.parse(arrangement) : null;
    }

    function createImageDiv(image) {
        const imgDiv = document.createElement('div');
        imgDiv.classList.add('background-image');
        imgDiv.style.backgroundImage = `url(${image})`;
        return imgDiv;
    }

    let arrangement = loadImageArrangement();
    if (!arrangement || arrangement.length !== totalImages) {
        const shuffledImages = shuffle([...images]);
        arrangement = Array.from({ length: totalImages }, (_, i) => shuffledImages[i % shuffledImages.length]);
        saveImageArrangement(arrangement);
    }

    const container = document.createElement('div');
    container.classList.add('background-image-container');
    document.body.appendChild(container);

    arrangement.forEach((image, index) => {
        const imgDiv = createImageDiv(image);

        // Adicionando logs para verificar se as imagens estão sendo carregadas
        const img = new Image();
        img.src = image;
        img.onload = () => console.log(`Imagem ${index + 1} carregada: ${image}`);
        img.onerror = () => console.error(`Erro ao carregar a imagem ${index + 1}: ${image}`);

        container.appendChild(imgDiv);
    });

    // Verificação se o container foi adicionado ao body
    if (document.body.contains(container)) {
        console.log('Container de imagens de fundo adicionado ao body.');
    } else {
        console.error('Falha ao adicionar o container de imagens de fundo ao body.');
    }
});
