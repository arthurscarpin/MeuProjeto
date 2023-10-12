-- Cria o banco de dados local
CREATE DATABASE PythonSQL

-- Conecta ao banco de dados local
USE PythonSQL

-- Cria tabelas necessárias
CREATE TABLE usuario (
    id INT PRIMARY KEY IDENTITY(1, 1),
    nome VARCHAR(100),
    sobrenome VARCHAR(100),
    email VARCHAR(100),
    senha VARCHAR(100),
    data_cadastro DATETIME
)

CREATE TABLE placa (
    id_placa INT IDENTITY(1,1) PRIMARY KEY,
    placa_nome VARCHAR(255),
    id_status INT
)