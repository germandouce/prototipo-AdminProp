CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    surname VARCHAR(80) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS consortiums (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    address VARCHAR(500) NOT NULL,
    owner_name VARCHAR(80) NOT NULL,
    admin_comission DECIMAL(10,2) NOT NULL,
    -- user_in_charge INT NOT NULL,
    -- FOREIGN KEY (user_in_charge) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS functional_units (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_number INT NOT NULL, -- e.g., 001
    unit_name VARCHAR(15) NOT NULL, -- e.g., 1A
    surface_percentage DECIMAL(10,2) NOT NULL,
    tentan VARCHAR(25),
    debt DECIMAL(10,2) DEFAULT 0,
    consortium INT NOT NULL,
    FOREIGN KEY (consortium) REFERENCES consortiums(id)
);

CREATE TABLE IF NOT EXISTS common_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    consortium INT NOT NULL,
    FOREIGN KEY (consortium) REFERENCES consortiums(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    functional_unit INT NOT NULL,
    tentant VARCHAR(25) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (functional_unit) REFERENCES functional_units(id)
);

INSERT INTO users (name, surname, email, password)
SELECT 'John', 'Doe', 'usuario@dominio.com', 'abc123'
    WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'usuario@dominio.com'
);