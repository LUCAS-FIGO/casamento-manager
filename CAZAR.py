import streamlit as st
from database import Database

# Configuração da página
st.set_page_config(
    page_title="Gestor de Casamento",
    page_icon="💒",
    layout="wide"
)

def cadastrar_demanda():
    st.subheader("Cadastro de Demandas")
    
    # Campos do formulário usando form
    with st.form("form_demanda", clear_on_submit=True):
        nome = st.text_input("Nome da Demanda")
        descricao = st.text_area("Descrição")
        prioridade = st.slider("Prioridade", 1, 5, 3)
        valor = st.text_input("Valor (R$)", "0,00")
        
        # Botão de submit do form
        submitted = st.form_submit_button("Adicionar Demanda")
        
        if submitted:
            try:
                # Validação dos campos
                if not nome or not descricao:
                    st.error("❌ Nome e Descrição são obrigatórios!")
                    return
                
                # Tratamento do valor
                valor_limpo = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
                if not valor_limpo:
                    valor_limpo = "0"
                    
                try:
                    valor_float = float(valor_limpo)
                except ValueError:
                    st.error("❌ Formato de valor inválido!")
                    st.info("💡 Use apenas números, exemplo: 1500,00")
                    return
                
                # Inserção no banco
                if st.session_state.db.inserir_demanda(
                    nome=nome,
                    descricao=descricao,
                    prioridade=str(prioridade),
                    valor=valor_float
                ):
                    st.success("✅ Demanda cadastrada com sucesso!")
                    # Força atualização da lista de demandas
                    st.session_state.update_demandas = True
                    
            except Exception as e:
                st.error("❌ Erro ao cadastrar demanda")
                st.error(f"Detalhes: {str(e)}")

def main():
    # Inicialização do estado da sessão
    if 'update_demandas' not in st.session_state:
        st.session_state.update_demandas = False
        
    st.title("Sistema de Gestão de Casamento 💒")
    
    try:
        # Inicializa conexão com banco de dados
        if 'db' not in st.session_state:
            st.session_state.db = Database()

        db = st.session_state.db

        # Menu lateral
        st.sidebar.title("Menu")
        opcao = st.sidebar.selectbox(
            "Selecione uma opção",
            ["Demandas", "Orçamentos", "Relatório Financeiro"]
        )

        if opcao == "Demandas":
            cadastrar_demanda()

            # Lista de demandas (atualiza quando necessário)
            if st.session_state.update_demandas:
                listar_demandas()
                st.session_state.update_demandas = False

        elif opcao == "Orçamentos":
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
        st.error("❌ Erro na aplicação")
        st.error(f"Detalhes: {str(e)}")

if __name__ == "__main__":
    main()