DROP DATABASE IF EXISTS stock;
CREATE DATABASE stock;
USE stock;


CREATE TABLE info (
    id int NOT NULL primary key AUTO_INCREMENT,
    latest_date DATETIME
);


CREATE TABLE broker (
    id int NOT NULL primary key AUTO_INCREMENT,
    code VARCHAR(10),
    name VARCHAR(50),
    address VARCHAR(200),
    focus TINYINT
);


CREATE TABLE company (
    id int NOT NULL primary key AUTO_INCREMENT,
    code VARCHAR(10),
    name VARCHAR(50),
    focus TINYINT
);


CREATE TABLE tran (
    id int NOT NULL primary key AUTO_INCREMENT,
    date DATETIME,

    company_code VARCHAR(10),
    broker_code VARCHAR(10),

    buy_price FLOAT,
    buy_amount INT,
    sell_price FLOAT,
    sell_amount INT
);


CREATE TABLE price (
    id int NOT NULL primary key AUTO_INCREMENT,
    date DATETIME,

    company_code VARCHAR(10),

    open_price FLOAT,
    close_price FLOAT,
    lowest_price FLOAT,
    highest_price FLOAT,

    amount INT
);


CREATE TABLE detail_tran (
    id int NOT NULL primary key AUTO_INCREMENT,
    date DATETIME,

    company_code VARCHAR(10),
    broker_code VARCHAR(10),

    buy_sell INT,
    price FLOAT,
    amount INT
);



