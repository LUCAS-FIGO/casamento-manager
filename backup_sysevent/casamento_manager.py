from datetime import datetime
from typing import List, Dict
from decimal import Decimal

class Demanda:
    def __init__(self, nome: str, descricao: str, prioridade: int, status: str):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.prioridade = prioridade  # 1 a 5
        self.status = status  # Pendente, Em Andamento, Concluído
        self.data_criacao = datetime.now()
        self.orcamentos: List[Orcamento] = []

class Orcamento:
    def __init__(self, fornecedor: str, valor: Decimal, descricao: str):
        self.fornecedor = fornecedor
        self.valor = valor
        self.descricao = descricao
        self.data_cotacao = datetime.now()
        self.status = "Em análise"  # Em análise, Aprovado, Rejeitado

class ControleFinanceiro:
    def __init__(self, orcamento_total: Decimal):
        self.orcamento_total = orcamento_total
        self.gastos: List[Dict] = []
        self.saldo = orcamento_total

    def registrar_gasto(self, descricao: str, valor: Decimal):
        self.gastos.append({
            "descricao": descricao,
            "valor": valor,
            "data": datetime.now()
        })
        self.saldo -= valor

class GestorCasamento:
    def __init__(self):
        self.demandas: List[Demanda] = []
        self.controle_financeiro = None

    def criar_demanda(self, nome: str, descricao: str, prioridade: int) -> Demanda:
        demanda = Demanda(nome, descricao, prioridade, "Pendente")
        self.demandas.append(demanda)
        return demanda

    def adicionar_orcamento(self, demanda: Demanda, fornecedor: str, 
                          valor: Decimal, descricao: str) -> Orcamento:
        orcamento = Orcamento(fornecedor, valor, descricao)
        demanda.orcamentos.append(orcamento)
        return orcamento

    def definir_orcamento_total(self, valor: Decimal):
        self.controle_financeiro = ControleFinanceiro(valor)

    def listar_demandas_por_status(self, status: str) -> List[Demanda]:
        return [d for d in self.demandas if d.status == status]

    def gerar_relatorio_financeiro(self) -> str:
        if not self.controle_financeiro:
            return "Orçamento total não definido"
        
        relatorio = f"""
        Relatório Financeiro
        -------------------
        Orçamento Total: R$ {self.controle_financeiro.orcamento_total}
        Gastos Totais: R$ {sum(g['valor'] for g in self.controle_financeiro.gastos)}
        Saldo: R$ {self.controle_financeiro.saldo}
        
        Detalhamento de Gastos:
        """
        
        for gasto in self.controle_financeiro.gastos:
            relatorio += f"\n{gasto['data'].strftime('%d/%m/%Y')} - {gasto['descricao']}: R$ {gasto['valor']}"
        
        return relatorio