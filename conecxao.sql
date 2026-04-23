CREATE DATABASE Biblioteca_Renovada;
GO

USE Biblioteca_Renovada;
GO


CREATE TABLE Livro (
    id INT PRIMARY KEY IDENTITY,
    titulo VARCHAR(100) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    ano INT,
    genero VARCHAR(50),
    editora VARCHAR(100),
    disponivel BIT DEFAULT 1
);


CREATE TABLE Usuario (
    id INT PRIMARY KEY IDENTITY,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE,
    email VARCHAR(100),
    telefone VARCHAR(20)
);


CREATE TABLE Funcionario (
    id INT PRIMARY KEY IDENTITY,
    nome VARCHAR(100) NOT NULL,
    salario DECIMAL(10,2) NOT NULL,
    tipo VARCHAR(50) CHECK (tipo IN ('Bibliotecario', 'Gerente'))
);


CREATE TABLE Emprestimo (
    id INT PRIMARY KEY IDENTITY,
    id_usuario INT NOT NULL,
    id_livro INT NOT NULL,

    data_emprestimo DATE DEFAULT GETDATE(),
    data_prevista DATE,       -- prazo (7 dias)
    data_devolvida DATE,      -- quando devolveu de verdade

    devolvido BIT DEFAULT 0,

    FOREIGN KEY (id_usuario) REFERENCES Usuario(id),
    FOREIGN KEY (id_livro) REFERENCES Livro(id)
);



CREATE TRIGGER trg_calcular_bonus
ON Funcionario
AFTER INSERT, UPDATE
AS
BEGIN
    UPDATE f
    SET 
        bonus = 
            CASE 
                WHEN f.tipo = 'Gerente' THEN f.salario * 0.2
                WHEN f.tipo = 'Bibliotecario' THEN f.salario * 0.1
                ELSE 0
            END,
        total = f.salario + 
            CASE 
                WHEN f.tipo = 'Gerente' THEN f.salario * 0.2
                WHEN f.tipo = 'Bibliotecario' THEN f.salario * 0.1
                ELSE 0
            END
    FROM Funcionario f
    INNER JOIN inserted i ON f.id = i.id;
END;


ALTER TABLE Funcionario
ADD bonus DECIMAL(10,2),
    total DECIMAL(10,2);
select * from usuario 
select * from Livro
select * from Funcionario
select * from Emprestimo


CREATE VIEW vw_meus_emprestimos AS
SELECT
    Emprestimo.id_usuario,
    Livro.titulo,
    Emprestimo.data_prevista,
    Emprestimo.data_devolvida,

    CASE
        WHEN Emprestimo.devolvido = 1 THEN 'Devolvido'
        WHEN Emprestimo.data_prevista < CAST(GETDATE() AS DATE) THEN 'Atrasado'
        ELSE 'Em aberto'
    END AS status

FROM Emprestimo
INNER JOIN Livro
    ON Livro.id = Emprestimo.id_livro;
GO


SELECT 
    Usuario.nome,
    Livro.titulo,
    Emprestimo.data_emprestimo,
    Emprestimo.devolvido
FROM Emprestimo
INNER JOIN Usuario ON Usuario.id = Emprestimo.id_usuario
INNER JOIN Livro ON Livro.id = Emprestimo.id_livro;


SELECT nome, salario, bonus, total FROM Funcionario
WHERE nome = 'Teste Ana';