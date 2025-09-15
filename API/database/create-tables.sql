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
    functional_units INT NOT NULL
);

CREATE TABLE IF NOT EXISTS functional_units (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_number INT NOT NULL,
    unit_name VARCHAR (15) NOT NULL,
    consortium INT NOT NULL,
    FOREIGN KEY (consortium) REFERENCES consortiums(id)
);

CREATE TABLE IF NOT EXISTS administrations_and_ownerships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_or_owner INT NOT NULL,
    consortium INT NOT NULL,
    FOREIGN KEY (admin_or_owner) REFERENCES users(id),
    FOREIGN KEY (consortium) REFERENCES consortiums(id)
);