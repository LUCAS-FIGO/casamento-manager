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

class Database:
    def __init__(self):
        try:
            # String de conexão com driver 17
            self.connection_string = (
                "Driver={ODBC Driver 17 for SQL Server};"
                "Server=tcp:cazar-server.database.windows.net,1433;"
                "Database=CasamentoDB;"
                "Uid=lufigotdb;"
                "Pwd=Senha@007;"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
                "Connection Timeout=30;"
            )
            
            # Debug: Lista drivers disponíveis
            drivers = pyodbc.drivers()
            st.write("Drivers ODBC disponíveis:")
            st.write(drivers)
            
            # Testa conexão
            with self.get_connection() as conn:
                st.success("✅ Conexão estabelecida!")
                
            # Após conexão bem sucedida, criar tabelas
            self.criar_tabelas()
                
        except Exception as e:
            st.error("❌ Erro na conexão")
            st.error(f"Detalhes: {str(e)}")
            raise e
            
    def get_connection(self):
        try:
            return pyodbc.connect(self.connection_string)
        except pyodbc.Error as e:
            st.error(f"Erro de conexão: {str(e)}")
            raise e

    def criar_tabelas(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Recria tabela Demandas com todas as colunas necessárias
                cursor.execute("""
                IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Orcamentos]') AND type in (N'U'))
                    DROP TABLE Orcamentos;
                    
                IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Demandas]') AND type in (N'U'))
                    DROP TABLE Demandas;

                CREATE TABLE Demandas (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nome NVARCHAR(100) NOT NULL,
                    descricao NVARCHAR(200) NOT NULL,
                    prioridade NVARCHAR(20),
                    status NVARCHAR(50),
                    data_criacao DATETIME DEFAULT GETDATE(),
                    valor DECIMAL(10,2)
                );

                CREATE TABLE Orcamentos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    demanda_id INT,
                    fornecedor NVARCHAR(100),
                    valor DECIMAL(10,2),
                    data_criacao DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (demanda_id) REFERENCES Demandas(id)
                );
                """)
                
                conn.commit()
                st.success("✅ Tabelas recriadas com sucesso!")
                
        except Exception as e:
            st.error("❌ Erro ao criar tabelas")
            st.error(f"Detalhes: {str(e)}")
            raise e

    def inserir_demanda(self, nome, descricao, prioridade, valor=None):
        try:
            # Trata o valor antes da inserção
            if valor is None or valor == '':
                valor_decimal = 0.0
            else:
                try:
                    # Remove R$ e outros caracteres especiais
                    valor_limpo = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
                    valor_decimal = float(valor_limpo)
                except ValueError:
                    st.error("❌ Erro: Formato de valor inválido")
                    st.info("💡 Use apenas números, exemplo: 1500,00")
                    return False

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Demandas 
                    (nome, descricao, prioridade, status, valor)
                    VALUES (?, ?, ?, 'Pendente', ?)
                """, (nome, descricao, prioridade, valor_decimal))
                conn.commit()
                st.success("✅ Demanda inserida com sucesso!")
                return True

        except Exception as e:
            st.error("❌ Erro ao inserir demanda")
            st.error(f"Detalhes: {str(e)}")
            return False

    def obter_demandas(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, nome, descricao, prioridade, status, data_criacao, valor
                    FROM Demandas
                    ORDER BY data_criacao DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao obter demandas: {str(e)}")
            raise e

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