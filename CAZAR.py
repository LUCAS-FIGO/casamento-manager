import streamlit as st
from decimal import Decimal
import logging
import pyodbc
from database import Database
from datetime import datetime

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Configuração da página
st.set_page_config(page_title="Gestor de Casamento", page_icon="💒")
st.title("Sistema de Gestão de Casamento 💒")

def check_odbc_drivers():
    try:
        drivers = pyodbc.drivers()
        st.write("### Drivers ODBC Disponíveis:")
        for driver in drivers:
            st.write(f"- {driver}")
        return True
    except Exception as e:
        st.error(f"Erro ao verificar drivers ODBC: {str(e)}")
        logging.error(f"Erro ODBC: {str(e)}")
        return False

def main():
    st.title("Sistema de Gerenciamento de Casamento 💒")
    try:
        # Verifica drivers antes de iniciar a aplicação
        if not check_odbc_drivers():
            st.error("Drivers ODBC não encontrados!")
            return

        # Inicialização do banco de dados
        if 'db' not in st.session_state:
            st.session_state.db = Database()
            st.session_state.db.criar_tabelas()
        
        db = st.session_state.db

        # Sidebar para navegação
        menu = st.sidebar.selectbox(
            "Selecione uma opção",
            ["Demandas", "Orçamentos", "Relatório Financeiro"]
        )

        if menu == "Demandas":
            st.header("Cadastro de Demandas")
            
            with st.form("nova_demanda"):
                nome = st.text_input("Nome da Demanda")
                descricao = st.text_area("Descrição")
                prioridade = st.slider("Prioridade", 1, 5, 3)
                status = "Pendente"
                
                if st.form_submit_button("Adicionar Demanda"):
                    if db.inserir_demanda(nome, descricao, prioridade, status):
                        st.success(f"Demanda '{nome}' criada com sucesso!")

            # Exibir demandas cadastradas
            st.subheader("Demandas Cadastradas")
            demandas = db.obter_demandas()
            for d in demandas:
                st.write(f"**{d.nome}** (Prioridade: {d.prioridade})")
                st.write(d.descricao)
                st.write("---")

        elif menu == "Orçamentos":
            st.header("Gestão de Orçamentos")
            
            demandas = db.obter_demandas()
            if demandas:
                demanda_selecionada = st.selectbox(
                    "Selecione a demanda",
                    demandas,
                    format_func=lambda x: x.nome
                )
                
                with st.form("novo_orcamento"):
                    fornecedor = st.text_input("Fornecedor")
                    valor = st.number_input("Valor", min_value=0.0, step=100.0)
                    descricao = st.text_area("Descrição do Orçamento")
                    status = "Em análise"
                    
                    if st.form_submit_button("Adicionar Orçamento"):
                        if db.inserir_orcamento(demanda_selecionada.id, fornecedor, valor, descricao, status):
                            st.success("Orçamento adicionado com sucesso!")
            else:
                st.warning("Cadastre algumas demandas primeiro!")

        else:  # Relatório Financeiro
            st.header("Relatório Financeiro")
            
            with st.form("novo_gasto"):
                descricao_gasto = st.text_input("Descrição do Gasto")
                valor_gasto = st.number_input("Valor", min_value=0.0, step=100.0)
                
                if st.form_submit_button("Registrar Gasto"):
                    if db.inserir_gasto(descricao_gasto, valor_gasto):
                        st.success("Gasto registrado com sucesso!")
        
            # Exibir gastos
            st.subheader("Gastos Registrados")
            gastos = db.obter_gastos()
            total = sum(g.valor for g in gastos)
            st.metric("Total de Gastos", f"R$ {total:,.2f}")
            
            for g in gastos:
                st.write(f"**{g.descricao}**: R$ {g.valor:,.2f}")
                st.write(f"Data: {g.data.strftime('%d/%m/%Y %H:%M')}")
                st.write("---")

        st.sidebar.markdown("---")
        st.sidebar.markdown("### Desenvolvido com ❤️")
    
    except Exception as e:
        st.error("Erro na aplicação. Verifique os logs para mais detalhes.")
        logging.error(f"Erro: {str(e)}")

if __name__ == "__main__":
    main()