from abc import ABC, abstractmethod
from conexao import cursor

class Funcionario(ABC):
    def __init__(self, nome, salario):
        self.nome = nome
        self.salario = salario

    def mostrarDados(self):
        print(f"Nome: {self.nome} | Salário: {self.salario}")

    @abstractmethod
    def calcularBonus(self):
        pass


class Pagamento(ABC):
    @abstractmethod

    def processarPagamento(self, valor):
        pass


class Bibliotecario(Funcionario, Pagamento):

    def calcularBonus(self):
        return self.salario * 0.1

    def processarPagamento(self, valor):
        print(f"Pagamento de R${valor} para Bibliotecário {self.nome}")


class Gerente(Funcionario, Pagamento):

    def calcularBonus(self):
        return self.salario * 0.2

    def processarPagamento(self, valor):
        print(f"Pagamento de R${valor} para Gerente {self.nome}")



def buscar_funcionario(id_funcionario):
    cursor.execute(
        "SELECT nome, salario, tipo FROM Funcionario WHERE id = ?",
        (id_funcionario,)
    )

    dados = cursor.fetchone()

    if not dados:
        print("Funcionário não encontrado!")
        return None

    nome, salario, tipo = dados

    salario = float(salario)

    if tipo.lower() == "bibliotecario":
        return Bibliotecario(nome, salario)
    elif tipo.lower() == "gerente":
        return Gerente(nome, salario)
    else:
        print("Tipo de funcionário desconhecido!")
        return None

def calcular_pagamento_total(funcionario):
    return funcionario.salario + funcionario.calcularBonus()