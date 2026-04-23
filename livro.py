from conexao import cursor, conexao

class Livro:

    @staticmethod
    def listar():
        cursor.execute("SELECT * FROM Livro")
        return cursor.fetchall()

    @staticmethod
    def atualizar_disponibilidade(id_livro, status):
        cursor.execute("UPDATE Livro SET disponivel = ? WHERE id = ?", (status, id_livro))
        conexao.commit()