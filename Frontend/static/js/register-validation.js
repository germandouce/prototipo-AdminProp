// Reglas de validación
const rules = [
    {
        test: pwd => pwd.length >= 8,
        message: 'Mínimo 8 caracteres'
    },
    {
        test: pwd => /[A-Z]/.test(pwd),
        message: 'Al menos una letra mayúscula'
    },
    {
        test: pwd => /\d/.test(pwd),
        message: 'Al menos un número'
    },
    {
        test: pwd => /[^A-Za-z0-9]/.test(pwd),
        message: 'Al menos un caracter especial'
    }
];

const passwordInput = document.getElementById('password-input');
const repeatPasswordInput = document.getElementById('repeat-password-input');
const passwordContainer = document.getElementById('password-input-container');

// Crear contenedor de mensajes si no existe
let validationList = document.getElementById('password-validation-list');
if (!validationList) {
    validationList = document.createElement('ul');
    validationList.id = 'password-validation-list';
    validationList.style.listStyle = 'none';
    validationList.style.padding = '0';
    validationList.style.width = '80%';
    validationList.style.textAlign = 'start';
    passwordContainer.parentNode.insertBefore(validationList, passwordContainer);
    // Crear los items
    rules.forEach((rule, i) => {
        const li = document.createElement('li');
        li.id = 'rule-' + i;
        li.textContent = rule.message;
        li.style.color = 'red';
        validationList.appendChild(li);
    });
}

// Validación en tiempo real de la contraseña
passwordInput.addEventListener('input', function() {
    const pwd = passwordInput.value;
    rules.forEach((rule, i) => {
        const li = document.getElementById('rule-' + i);
        if (rule.test(pwd)) {
            li.style.color = 'green';
        } else {
            li.style.color = 'red';
        }
    });
    // También actualiza la coincidencia de contraseñas si ya hay valor en repetir
    checkPasswordMatch();
});

// Validación en tiempo real de coincidencia de contraseñas
repeatPasswordInput.addEventListener('input', checkPasswordMatch);
passwordInput.addEventListener('input', checkPasswordMatch);

function checkPasswordMatch() {
    const password = passwordInput.value;
    const repeatPassword = repeatPasswordInput.value;
    let msg = document.getElementById('password-match-message');
    if (!msg) {
        msg = document.createElement('p');
        msg.id = 'password-match-message';
        msg.style.color = 'red';
        repeatPasswordInput.parentNode.appendChild(msg);
    }
    if (repeatPassword && password !== repeatPassword) {
        msg.textContent = 'Las contraseñas no coinciden.';
        msg.style.color = 'red';
    } else if (repeatPassword && password === repeatPassword) {
        msg.textContent = 'Las contraseñas coinciden.';
        msg.style.color = 'green';
    } else {
        msg.textContent = '';
    }
}

// Validación al enviar el formulario
const registerForm = document.getElementById('register-form');
registerForm.addEventListener('submit', function(event) {
    const pwd = passwordInput.value;
    const repeatPwd = repeatPasswordInput.value;
    let valid = true;

    // Verifica todas las reglas
    rules.forEach((rule, i) => {
        if (!rule.test(pwd)) {
            valid = false;
        }
    });

    // Verifica coincidencia de contraseñas
    if (pwd !== repeatPwd) {
        valid = false;
    }

    if (!valid) {
        event.preventDefault();
        alert('La contraseña no cumple los requisitos o las contraseñas no coinciden.');
    }
});
