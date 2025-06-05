import pyodbc
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class Demanda:
    id: int
    nome: str
    descricao: str
    prioridade: int
    status: str
    data_criacao: datetime

@dataclass
class Orcamento:
    id: int
    demanda_id: int
    fornecedor: str
    valor: Decimal
    descricao: str
    status: str

@dataclass
class Gasto:
    id: int
    descricao: str
    valor: Decimal
    data: datetime

class DatabaseManager:
    def __init__(self):
        # Altere estas configurações conforme seu ambiente
        self.connection_string = (
            "DRIVER={SQL Server};"
            "SERVER=DESKTOP-G6K4M8T\SQL2019;"  # Altere para seu servidor
            "DATABASE=CasamentoDB;"  # Altere para seu banco
            "Trusted_Connection=yes;"  # Windows Authentication
        )

    def get_connection(self):
        return pyodbc.connect(self.connection_string)

    def criar_tabelas(self):
        queries = [
            """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Demandas]') AND type in (N'U'))
            BEGIN
                CREATE TABLE Demandas (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nome NVARCHAR(100) NOT NULL,
                    descricao NVARCHAR(MAX),
                    prioridade INT,
                    status NVARCHAR(50),
                    data_criacao DATETIME DEFAULT GETDATE()
                )
            END
            """,
            """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Orcamentos]') AND type in (N'U'))
            BEGIN
                CREATE TABLE Orcamentos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    demanda_id INT,
                    fornecedor NVARCHAR(100),
                    valor DECIMAL(10,2),
                    descricao NVARCHAR(MAX),
                    status NVARCHAR(50),
                    FOREIGN KEY (demanda_id) REFERENCES Demandas(id)
                )
            END
            """,
            """
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Gastos]') AND type in (N'U'))
            BEGIN
                CREATE TABLE Gastos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    descricao NVARCHAR(MAX),
                    valor DECIMAL(10,2),
                    data DATETIME DEFAULT GETDATE()
                )
            END
            """
        ]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            for query in queries:
                cursor.execute(query)
            conn.commit()

    def inserir_demanda(self, nome: str, descricao: str, prioridade: int, status: str) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Demandas (nome, descricao, prioridade, status)
                    VALUES (?, ?, ?, ?)
                """, (nome, descricao, prioridade, status))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao inserir demanda: {e}")
            return False

    def obter_demandas(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Demandas ORDER BY prioridade DESC")
                rows = cursor.fetchall()
                return [Demanda(
                    id=row[0],
                    nome=row[1],
                    descricao=row[2],
                    prioridade=row[3],
                    status=row[4],
                    data_criacao=row[5]
                ) for row in rows]
        except Exception as e:
            print(f"Erro ao obter demandas: {e}")
            return []

    def inserir_orcamento(self, demanda_id: int, fornecedor: str, 
                         valor: float, descricao: str, status: str) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Orcamentos (demanda_id, fornecedor, valor, descricao, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (demanda_id, fornecedor, valor, descricao, status))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao inserir orçamento: {e}")
            return False

    def inserir_gasto(self, descricao: str, valor: float) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Gastos (descricao, valor)
                    VALUES (?, ?)
                """, (descricao, valor))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao inserir gasto: {e}")
            return False

    def obter_gastos(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Gastos ORDER BY data DESC")
                rows = cursor.fetchall()
                return [Gasto(
                    id=row[0],
                    descricao=row[1],
                    valor=row[2],
                    data=row[3]
                ) for row in rows]
        except Exception as e:
            print(f"Erro ao obter gastos: {e}")
            return []