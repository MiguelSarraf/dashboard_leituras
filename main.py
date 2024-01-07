import streamlit as st
from relatorio_livros import cria_tabs
import pandas as pd

if "page" not in st.session_state:
	st.session_state.page="tabela"

# st.session_state.path="modelo.xlsx"

if st.session_state.page=="tabela":
	st.set_page_config(layout = "centered")
	st.title("Retrospectiva de leituras")
	st.write("Olá, seja bem-vind@.")
	st.write("Aqui você pode criar sua retrospectiva de leituras.")
	st.write("Baixe a planilha modelo ou suba sua planilha preenchida nos botões abaixo:")
	col1, col2=st.columns([1,1])
	botao1=col1.download_button("Clique aqui para baixar o modelo de tabela", data=open("./modelo.xlsx", "rb"), file_name="modelo.xlsx")
	botao2=col2.file_uploader("Suba aqui sua tabela para montar seu relatório", type=["xlsx"])
	if botao2:
		st.session_state.page="relatorio"
		st.session_state.path = pd.read_excel(botao2)
		st.experimental_rerun()

elif st.session_state.page=="relatorio":
	st.set_page_config(layout = "wide")
	# data=faz_grafico(st.session_state.path)

	# st.altair_chart(titulo, use_container_width=True)
	# st.altair_chart(data, use_container_width=True)

	livros=st.session_state.path
	livros["data"]=pd.to_datetime(livros.data, format="%d/%m/%y", )
	livros["ano"]=livros.data.dt.year

	anos=livros.ano.astype(int).unique()
	anos.sort()

	buttons_anos=[]
	for ano in anos:
		buttons_anos.append(st.sidebar.button(str(ano), key=ano))
	if "ano" not in st.session_state:st.session_state.ano=max(anos)

	cria_tabs(livros, st.session_state.ano)

	st.markdown("""
	<style>
	.big-font {
	    font-size:30px !important;
	}
	</style>
	""", unsafe_allow_html=True)
	st.markdown('<p class="big-font">Utilize a barra lateral para trocar o ano da visualização.</p>', unsafe_allow_html=True)

	_, col, _=st.columns([1,1,1])
	botao=col.button("Clique aqui para voltar à tela inicial", key="voltar")
	if botao:
		st.session_state.page="tabela"
		st.experimental_rerun()

	if any(buttons_anos):
		for ano, button in zip(anos, buttons_anos):
			if button:
				st.session_state.ano=ano
				st.experimental_rerun()
