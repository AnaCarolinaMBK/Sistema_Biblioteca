from conexao import cursor, conexao


class Emprestimo:

    @staticmethod
    def emprestar(id_usuario, id_livro):
        cursor.execute("EXEC sp_emprestar_livro ?, ?", (id_usuario, id_livro))
        conexao.commit()

    @staticmethod
    def devolver(id_usuario, id_livro):
        cursor.execute("EXEC sp_devolver_livro ?, ?", (id_usuario, id_livro))
        conexao.commit()