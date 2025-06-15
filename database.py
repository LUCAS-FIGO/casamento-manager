import os
import pyodbc
import streamlit as st
import logging
from dotenv import load_dotenv
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

class Database:  # Nome da classe deve ser Database, não DatabaseManager
    def __init__(self):
        self.server = st.secrets["connections"]["sql"]["DB_SERVER"]
        self.database = st.secrets["connections"]["sql"]["DB_NAME"]
        self.username = st.secrets["connections"]["sql"]["DB_USER"]
        self.password = st.secrets["connections"]["sql"]["DB_PASSWORD"]
        
        self.connection_string = (
            "Driver={SQL Server};"
            f"Server={self.server};"
            f"Database={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
        )
        
        # Configurar logging
        logging.basicConfig(
            filename='database.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def get_connection(self):
        try:
            conn = pyodbc.connect(self.connection_string, timeout=30)
            logging.info("Conexão com banco de dados estabelecida com sucesso")
            return conn
        except pyodbc.Error as e:
            logging.error(f"Erro ao conectar ao banco de dados: {str(e)}")
            raise Exception("Erro de conexão com o banco de dados. Verifique as configurações.")

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
            logging.error(f"Erro ao inserir demanda: {e}")
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
            logging.error(f"Erro ao obter demandas: {e}")
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
            logging.error(f"Erro ao inserir orçamento: {e}")
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
            logging.error(f"Erro ao inserir gasto: {e}")
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
            logging.error(f"Erro ao obter gastos: {e}")
            return []

    def atualizar_demanda(self, id: int, nome: str, descricao: str, 
                         prioridade: int, status: str) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Demandas 
                    SET nome=?, descricao=?, prioridade=?, status=?
                    WHERE id=?
                """, (nome, descricao, prioridade, status, id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Erro ao atualizar demanda: {e}")
            return False

    def deletar_demanda(self, id: int) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Primeiro deleta os orçamentos relacionados
                cursor.execute("DELETE FROM Orcamentos WHERE demanda_id=?", (id,))
                # Depois deleta a demanda
                cursor.execute("DELETE FROM Demandas WHERE id=?", (id,))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Erro ao deletar demanda: {e}")
            return False

    def obter_orcamentos_por_demanda(self, demanda_id: int) -> List[Orcamento]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM Orcamentos 
                    WHERE demanda_id=? 
                    ORDER BY valor ASC
                """, (demanda_id,))
                rows = cursor.fetchall()
                return [Orcamento(
                    id=row[0],
                    demanda_id=row[1],
                    fornecedor=row[2],
                    valor=Decimal(str(row[3])),
                    descricao=row[4],
                    status=row[5]
                ) for row in rows]
        except Exception as e:
            logging.error(f"Erro ao obter orçamentos: {e}")
            return []

    def obter_total_gastos(self) -> Decimal:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(valor) FROM Gastos")
                result = cursor.fetchone()[0]
                return Decimal(str(result)) if result else Decimal('0')
        except Exception as e:
            logging.error(f"Erro ao calcular total de gastos: {e}")
            return Decimal('0')