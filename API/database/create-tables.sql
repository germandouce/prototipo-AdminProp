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
    tenant VARCHAR(25) DEFAULT NULL,
    rent_value DECIMAL(10,2) NOT NULL DEFAULT 0.00,
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
    description VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (consortium) REFERENCES consortiums(id),
    FOREIGN KEY (functional_unit) REFERENCES functional_units(id)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AGREGAR DOS USUARIOS
INSERT INTO users (name, surname, email, password, verified)
SELECT 'John', 'Doe', 'usuario@dominio.com', 'pbkdf2:sha256:600000$5awvOCLwNzLQmVlq$73fef6846f25d4e137e495578a92c8f876273e64d4f35e0a8553d97322589bde', TRUE -- Abcde.12345 hasheado
    WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'usuario@dominio.com'
);

INSERT INTO users (name, surname, email, password, verified)
SELECT 'Martin', 'Fowler', 'martinfowler@gmail.com', 'pbkdf2:sha256:600000$DBqEiZaiRnqMemr4$5eb6adc4fdfbbc7aa49952707bb9e0deb554ce77e18cac70ffec05ef20a4fe24', TRUE -- StrongP@ssw0rd hasheado
    WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'martinfowler@gmail.com'
);

-- AGREGAR UN CONSORCIO CON UNIDADES FUNCIONALES DE EJEMPLO
INSERT INTO consortiums (name, address, owner_name, admin_commission, user_id)
SELECT 'Galerías pacífico', 'Av. Corrientes 1234, CABA', 'Juan Pérez', 10.00, 1
    WHERE NOT EXISTS (
    SELECT 1 FROM consortiums WHERE name = 'Galerías pacífico');

INSERT INTO functional_units (unit_number, unit_name, surface, consortium, tenant, rent_value)
SELECT 1, '1A', 50.00, 1, 'Zoilo', 50000.00
    WHERE NOT EXISTS (
    SELECT 1 FROM functional_units WHERE unit_name = '1B' AND consortium = 1
);

INSERT INTO functional_units (unit_number, unit_name, surface, consortium, tenant, rent_value)
SELECT 2, '1B', 25.00, 1, 'Carlos López', 350000.00
    WHERE NOT EXISTS (
    SELECT 1 FROM functional_units WHERE unit_name = '1B' AND consortium = 1
);

-- AGREGAR OTRO CONSORCIO CON UNIDADES FUNCIONALES DE EJEMPLO
INSERT INTO consortiums (name, address, owner_name, admin_commission, user_id)
SELECT 'Condominio La Plata', 'Calle 50 Nro 1234, La Plata', 'María Gómez', 8.00, 1
    WHERE NOT EXISTS (
    SELECT 1 FROM consortiums WHERE name = 'Condominio La Plata');

INSERT INTO functional_units (unit_number, unit_name, surface, consortium, tenant, rent_value)
SELECT 1, '1C', 80.00, 2, 'José', 90000.00
    WHERE NOT EXISTS (
    SELECT 1 FROM functional_units WHERE unit_name = '1C' AND consortium = 2
);

INSERT INTO common_expenses (description, amount, date, consortium)
VALUES ('Luz de pasillo (Prueba de Evento)', 10000.00, '2025-10-15', 1);

INSERT INTO common_expenses (description, amount, date, consortium)
VALUES ('Seguridad (Prueba de Evento)', 5000.00, '2025-10-15', 1);

-- CAMBIO 1: Cambia el delimitador
DELIMITER //

CREATE EVENT IF NOT EXISTS ev_process_monthly_expenses
ON SCHEDULE EVERY 1 MONTH
    -- Se ejecuta el día 1 de cada mes, a la 1:00 AM
    STARTS (LAST_DAY(CURDATE()) + INTERVAL 1 DAY + INTERVAL 1 HOUR)
DO
BEGIN
    -- Alquiler mensual
    INSERT INTO payments (functional_unit, consortium, tenant, description, amount, date)
    SELECT
        fu.id AS functional_unit,
        fu.consortium AS consortium,
        fu.tenant AS tenant,

        -- Descripción dinámica, ej: "Expensas Ordinarias - Octubre 2025"
        CONCAT('Alquiler - ', DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%M %Y')) AS description,

        fu.rent_value AS amount,

        -- Fecha en que se genera el pago (hoy)
        CURDATE() AS date
    FROM
        functional_units AS fu;
    -- Insertar en 'payments' el cálculo del mes anterior
    INSERT INTO payments (functional_unit, consortium, tenant, description, amount, date)
    SELECT
        fu.id AS functional_unit,
        fu.consortium AS consortium,
        fu.tenant AS tenant,

        -- Descripción dinámica, ej: "Expensas Ordinarias - Octubre 2025"
        CONCAT('Expensas Ordinarias - ', DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%M %Y')) AS description,

        -- CÁLCULO PROPORCIONAL:
        -- (Total Gastos Consorcio * (Superficie UF / SUMA(Superficies de todas las UF)))
        (expenses.total_monthly_expense * (fu.surface / surface_calc.total_consortium_surface)) AS amount,

        -- Fecha en que se genera el pago (hoy)
        CURDATE() AS date
    FROM
        functional_units AS fu
    JOIN
        -- Subconsulta 1: Gasto total del mes anterior POR consorcio
        (SELECT
            consortium,
            SUM(amount) AS total_monthly_expense
         FROM common_expenses
         WHERE
            -- Filtra solo los gastos del mes pasado
            YEAR(date) = YEAR(CURDATE() - INTERVAL 1 MONTH) AND
            MONTH(date) = MONTH(CURDATE() - INTERVAL 1 MONTH)
         GROUP BY consortium
        ) AS expenses ON fu.consortium = expenses.consortium
    JOIN
        -- Subconsulta 2: Superficie total (calculada por SUMA) POR consorcio
        (SELECT
            consortium,
            SUM(surface) AS total_consortium_surface
         FROM functional_units
         GROUP BY consortium
        ) AS surface_calc ON fu.consortium = surface_calc.consortium
    WHERE
        -- Cláusula de seguridad para evitar división por cero
        surface_calc.total_consortium_surface > 0;
END
//

-- CAMBIO 3: Restaura el delimitador original
DELIMITER ;