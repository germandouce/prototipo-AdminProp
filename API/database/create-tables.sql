SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    surname VARCHAR(80) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    verified BOOLEAN DEFAULT FALSE
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS consortiums (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    address VARCHAR(500) NOT NULL,
    owner_name VARCHAR(80) NOT NULL,
    admin_commission DECIMAL(10,2) NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS functional_units (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_number INT NOT NULL, -- e.g., 001
    unit_name VARCHAR(15) NOT NULL, -- e.g., 1A
    surface DECIMAL(10,2) NOT NULL,
    surface_percentage DECIMAL(10,2) NOT NULL,
    tenant VARCHAR(25) DEFAULT NULL,
    debt DECIMAL(10,2) DEFAULT 0,
    consortium INT NOT NULL,
    FOREIGN KEY (consortium) REFERENCES consortiums(id)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS common_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    consortium INT NOT NULL,
    FOREIGN KEY (consortium) REFERENCES consortiums(id)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    functional_unit INT NOT NULL,
    consortium INT NOT NULL,
    tenant VARCHAR(25) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (consortium) REFERENCES consortiums(id),
    FOREIGN KEY (functional_unit) REFERENCES functional_units(id)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AGREGAR DOS USUARIOS
INSERT INTO users (name, surname, email, password)
SELECT 'John', 'Doe', 'usuario@dominio.com', 'pbkdf2:sha256:600000$5awvOCLwNzLQmVlq$73fef6846f25d4e137e495578a92c8f876273e64d4f35e0a8553d97322589bde' -- Abcde.12345 hasheado
    WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'usuario@dominio.com'
);

INSERT INTO users (name, surname, email, password)
SELECT 'Martin', 'Fowler', 'martinfowler@gmail.com', 'pbkdf2:sha256:600000$DBqEiZaiRnqMemr4$5eb6adc4fdfbbc7aa49952707bb9e0deb554ce77e18cac70ffec05ef20a4fe24' -- StrongP@ssw0rd hasheado
    WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'martinfowler@gmail.com'
);

-- AGREGAR UN CONSORCIO CON UNIDADES FUNCIONALES DE EJEMPLO
INSERT INTO consortiums (name, address, owner_name, admin_commission, user_id)
SELECT 'Galerías pacífico', 'Av. Corrientes 1234, CABA', 'Juan Pérez', 10.00, 1
    WHERE NOT EXISTS (
    SELECT 1 FROM consortiums WHERE name = "Galerías pacífico");

INSERT INTO functional_units (unit_number, unit_name, surface, surface_percentage, consortium)
SELECT 1, '1A', 50.00, 5.00, 1
    WHERE NOT EXISTS (
    SELECT 1 FROM functional_units WHERE unit_name = "1A" AND consortium = 1
);

INSERT INTO functional_units (unit_number, unit_name, surface, surface_percentage, consortium, tenant, debt)
SELECT 2, '1B', 25.00, 2.50, 1, 'Carlos López', 1500.00
    WHERE NOT EXISTS (
    SELECT 1 FROM functional_units WHERE unit_name = "1B" AND consortium = 1
);

-- AGREGAR OTRO CONSORCIO CON UNIDADES FUNCIONALES DE EJEMPLO
INSERT INTO consortiums (name, address, owner_name, admin_commission, user_id)
SELECT 'Condominio La Plata', 'Calle 50 Nro 1234, La Plata', 'María Gómez', 8.00, 1
    WHERE NOT EXISTS (
    SELECT 1 FROM consortiums WHERE name = "Condominio La Plata");

INSERT INTO functional_units (unit_number, unit_name, surface, surface_percentage, consortium)
SELECT 1, '1A', 75.00, 7.50,2
    WHERE NOT EXISTS (
    SELECT 1 FROM functional_units WHERE unit_name = "2A" AND consortium = 2
);