from conexao import cursor

class Usuario:

    @staticmethod
    def listar():
        cursor.execute("SELECT * FROM Usuario")
        return cursor.fetchall()

    @staticmethod
    def contar_livros(id_usuario):
        cursor.execute(
            "SELECT COUNT(*) FROM Emprestimo WHERE id_usuario = ? AND data_devolucao IS NULL",
            (id_usuario,)
        )
        return cursor.fetchone()[0]