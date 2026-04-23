USE Biblioteca_Renovada;
GO

CREATE PROCEDURE sp_emprestar_livro
    @id_usuario INT,
    @id_livro INT
AS
BEGIN
    DECLARE @qtd INT
    DECLARE @disponivel BIT

    -- Limite de livros
    SELECT @qtd = COUNT(*)
    FROM Emprestimo
    WHERE id_usuario = @id_usuario AND devolvido = 0

    IF @qtd >= 3
    BEGIN
        RAISERROR('Limite de 3 livros atingido', 16, 1)
        RETURN
    END

    -- Verifica disponibilidade
    SELECT @disponivel = disponivel FROM Livro WHERE id = @id_livro

    IF @disponivel = 0
    BEGIN
        RAISERROR('Livro indisponível', 16, 1)
        RETURN
    END

    -- Inserir empréstimo
    INSERT INTO Emprestimo (id_usuario, id_livro, data_prevista, devolvido)
    VALUES (@id_usuario, @id_livro, DATEADD(DAY, 7, GETDATE()), 0)

    -- Atualizar livro
    UPDATE Livro SET disponivel = 0 WHERE id = @id_livro
END



CREATE PROCEDURE sp_devolver_livro
    @id_usuario INT,
    @id_livro INT
AS
BEGIN
    UPDATE Emprestimo
    SET devolvido = 1
    WHERE id_usuario = @id_usuario
    AND id_livro = @id_livro
    AND devolvido = 0

    UPDATE Livro
    SET disponivel = 1
    WHERE id = @id_livro
END