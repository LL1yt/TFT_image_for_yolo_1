document.addEventListener("DOMContentLoaded", function () {
    // При нажатии на элементы меню, отправлять AJAX запрос
    document.querySelectorAll('.nav-links a').forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault(); // Предотвращаем стандартное действие перехода по ссылке
            var pageName = this.getAttribute('href').replace('/', ''); // Получаем имя страницы из href

            // Выполняем AJAX запрос
            fetch('/ajax/' + pageName)
                .then(response => response.text()) // Преобразуем ответ в текст
                .then(html => {
                    document.getElementById('content').innerHTML = html; // Заменяем HTML в контентном блоке
                })
                .catch(error => console.log('Ошибка загрузки страницы: ', error));
        });
    });
});
