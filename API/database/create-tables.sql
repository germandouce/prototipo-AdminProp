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
    functional_units INT NOT NULL,
    user_in_charge INT NOT NULL,
    FOREIGN KEY (user_in_charge) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS functional_units (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_number INT NOT NULL,
    unit_name VARCHAR (15) NOT NULL,
    consortium INT NOT NULL,
    FOREIGN KEY (consortium) REFERENCES consortiums(id)
);