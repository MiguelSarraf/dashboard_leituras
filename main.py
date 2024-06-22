import streamlit as st
from relatorio_livros import cria_tabs
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

__version__="1.3"
__data__="jun/24"

if "page" not in st.session_state:
	st.session_state.page="tabela"

# st.session_state.path="modelo.xlsx"

if st.session_state.page=="tabela":
	st.set_page_config(layout = "centered")
	st.session_state.window_width=streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
	st.title("Retrospectiva de leituras")
	st.write("Olá, seja bem-vind@.")
	st.write("Aqui você pode criar sua retrospectiva de leituras.")
	st.write("Baixe a planilha modelo ou suba sua planilha preenchida nos botões abaixo:")
	col1, col2=st.columns([1,1])
	baixa_modelo=col1.download_button("Clique aqui para baixar o modelo de tabela", data=open("./modelo.xlsx", "rb"), file_name="modelo.xlsx")
	gera_modelo=col1.button("Clique aqui para gerar relatório com a tabela de exemplo")
	carrega=col2.file_uploader("Suba aqui sua tabela para montar seu relatório", type=["xlsx"])
	st.write("Versão %s de %s" % (__version__, __data__))
	if carrega:
		st.session_state.page="relatorio"
		st.session_state.path = pd.read_excel(carrega)
		if "ano" in st.session_state:del st.session_state.ano
		st.rerun()
	if gera_modelo:
		st.session_state.page="relatorio"
		st.session_state.path = pd.read_excel("modelo.xlsx")
		if "ano" in st.session_state:del st.session_state.ano
		st.rerun()

elif st.session_state.page=="relatorio":
	st.set_page_config(layout = "wide")

	livros=st.session_state.path
	livros["data"]=pd.to_datetime(livros.data, format="%d/%m/%y", )
	livros["ano"]=livros.data.dt.year

	anos=livros.ano.astype(int).unique()
	anos.sort()

	if len(anos)>1:
		buttons_anos=[]
		for ano in anos:
			buttons_anos.append(st.sidebar.button(str(ano), key=ano))
		usar_anos=True
	else:
		usar_anos=False
	if "ano" not in st.session_state:st.session_state.ano=max(anos)

	cria_tabs(livros, usar_anos, st.session_state.ano)

	st.markdown("""
	<style>
	.big-font {
	    font-size:30px !important;
	}
	</style>
	""", unsafe_allow_html=True)
	if usar_anos: st.markdown('<p class="big-font">Utilize a barra lateral para trocar o ano da visualização.</p>', unsafe_allow_html=True)

	_, col, _=st.columns([1,1,1])
	botao=col.button("Clique aqui para voltar à tela inicial", key="voltar")
	if botao:
		st.session_state.page="tabela"
		st.rerun()

	if usar_anos and any(buttons_anos):
		for ano, button in zip(anos, buttons_anos):
			if button:
				st.session_state.ano=ano
				st.rerun()
