document.addEventListener('DOMContentLoaded', (event) => {
    // Selecciona todos los mensajes flash
    const flashMessages = document.querySelectorAll('.alert');

    flashMessages.forEach(function(message) {
        // Espera 5 segundos
        setTimeout(function() {
            // Inicia la transición de desvanecimiento
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';

            // Espera a que termine la transición para eliminar el elemento
            setTimeout(function() {
                message.remove();
            }, 500); // 500ms debe coincidir con la duración de la transición
        }, 5000); // 5000ms = 5 segundos
    });
});