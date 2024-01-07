import streamlit as st
import io
import pandas as pd
import altair as alt

def faz_grafico(livros, usar_ano, ano):
    if usar_ano: livros=livros.query("ano==%s" % (ano))
    """#Variáveis"""

    base_width=80
    base_height=70
    big_width=7*base_width
    big_height=4*base_height
    font="roustel"
    font_graphs="caveat"
    font_nome="belovedays"
    font_size=42
    font_size_grphs=15
    font_size_grphs_title=30

    Q1=livros.velocidade.quantile(.25)
    Q3=livros.velocidade.quantile(.75)
    IQR=Q3-Q1
    lim_inf=Q1-1.5*IQR
    lim_sup=Q3+1.5*IQR

    """##Agregações"""
    cor_ranking=livros.query("ranking>0")[["livro", "autor", "nacionalidade", "ranking"]].sort_values("ranking").reset_index()
    cor_ranking["cor_ranking"]=cor_ranking.index%2

    livros_mes=livros.groupby(["ano", "mes"]).agg({"livro":"count"}).reset_index()
    livros_mes["num_livros"]="Número de Livros"

    tempo_media_movel=4
    livros_mes["soma"]=livros_mes.livro
    for tempo in range(1, tempo_media_movel):
      livros_mes["livro_delay"]=livros_mes.livro.shift(tempo)
      livros_mes.soma+=livros_mes.livro_delay

    livros_mes["media_movel"]=livros_mes.soma/tempo_media_movel
    livros_mes["media_movel_tit"]="Média móvel (%s meses)"%(tempo_media_movel)

    meses={
        1:"jan",
        2:"fev",
        3:"mar",
        4:"abr",
        5:"mai",
        6:"jun",
        7:"jul",
        8:"ago",
        9:"set",
        10:"out",
        11:"nov",
        12:"dez",
    }
    livros_mes["mes_nome"]=livros_mes.mes.map(meses)
    livros["mes_nome"]=livros.mes.map(meses)

    rank=livros.query("ranking>0").sort_values("ranking")[["ranking", "livro", "autor", "nacionalidade"]]
    rank["livro"]+="\n"

    kpis={"num_livros":[str(livros.livro.count())+" livros"],
          "num_paginas":[str(livros.paginas.sum())+" páginas"],
          "num_nacionalidade":[str(livros.nacionalidade.unique().shape[0])+" nacionalidades"],
          "paginas_por_dia":[str(round(livros.paginas.sum()/livros.tempo.sum()))+" páginas por dia"],
          "top_do_ano":["Top "+str(livros.ranking.max())+" livros do ano"],
          "titulo":["Relatório de leituras "+str(ano)],
          "autor":["Miguel Sarraf"],
          "autor_text":["Desenvolvido por "],
          "insta":["@sarraf_miguel"],
          "insta_url":["https://www.instagram.com/sarraf_miguel"]}
    kpis=pd.DataFrame(kpis)

    """#Visualização

    ## Interatividade
    """

    selector_livro = alt.selection_point(fields=["livro"], name="selector_livro")
    selector_estilo = alt.selection_point(fields=["estilo"], name="selector_estilo")
    selector_nacionalidade = alt.selection_point(fields=["nacionalidade"], name="selector_nacionalidade")

    """##Livros por mês"""

    livros_por_mes=alt.Chart(livros).mark_line(color="#4285f4").encode(
        x=alt.X(
            "mes:O",
            title="Mês",
            axis=alt.Axis(
                labelAngle=0,
                grid=True,
                titleFont=font_graphs,
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs_title
            )
        ),
        y=alt.Y(
            "count(livro):Q",
            title="",
            axis=alt.Axis(
                grid=False,
                titleFont=font_graphs,
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs_title
            ),
        ),
        tooltip=[
            alt.Tooltip("mes_nome",title="Mês"),
            alt.Tooltip("count(livro)",title="Número de livros")
        ],
        opacity=alt.Opacity(
            "num_livros",
            legend=alt.Legend(
                title="",
                orient="top-left",
                labelFontSize=font_size_grphs,
                symbolSize=100,
                symbolStrokeWidth=3
            )
        )
    ).properties(
        width=big_width,
        height=big_height,
        title="Livros por mês"
    ).transform_filter(selector_livro).transform_filter(selector_estilo).transform_filter(selector_nacionalidade)

    livros_movel_por_mes=alt.Chart(livros_mes).mark_line(color="blue").encode(
        x=alt.X(
            "mes:O",
            title="Mês",
            axis=alt.Axis(
                labelAngle=0,
                grid=True,
                titleFont=font_graphs,
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs_title
            )
        ),
        y=alt.Y(
            "media_movel:Q",
            title="",
            axis=alt.Axis(
                grid=False,
                titleFont=font_graphs,
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs_title
            ),
        ),
        tooltip=[
            alt.Tooltip("mes_nome",title="Mês"),
            alt.Tooltip("media_movel",title="Média móvel")
        ],
        opacity=alt.Opacity(
            "media_movel_tit",
            legend=alt.Legend(
                title="",
                orient="top-left",
                labelFontSize=font_size_grphs,
                symbolSize=100,
                symbolStrokeWidth=3
            )
        )
    ).properties(
        width=big_width,
        height=big_height,
    ).transform_filter(selector_livro).transform_filter(selector_estilo).transform_filter(selector_nacionalidade)

    """## KPIS"""

    titulo=alt.Chart(kpis).mark_text(size=50, font=font, lineBreak='\n').encode(
        text=alt.Text(
            "titulo:N"
        )
    ).properties(
        width=3.5*big_width,
        height=base_height
    )

    num_livros=alt.Chart(kpis).mark_text(baseline="middle", size=font_size, font=font_graphs).encode(
        text=alt.Text(
            "num_livros"
        )
    ).properties(
        width=base_width,
        height=base_height
    )

    num_paginas=alt.Chart(kpis).mark_text(baseline="middle", size=font_size, font=font_graphs).encode(
        text=alt.Text(
            "num_paginas"
        )
    ).properties(
        width=base_width,
        height=base_height
    )

    num_nacionalidade=alt.Chart(kpis).mark_text(baseline="middle", size=font_size, font=font_graphs).encode(
        text=alt.Text(
            "num_nacionalidade"
        )
    ).properties(
        width=base_width,
        height=base_height
    )

    paginas_por_dia=alt.Chart(kpis).mark_text(baseline="middle", size=font_size, font=font_graphs, lineBreak='\n').encode(
        text=alt.Text(
            "paginas_por_dia"
        )
    ).properties(
        width=base_width,
        height=base_height
    )

    """## Velocidade de leitura"""

    max_dias=livros.tempo.max()
    max_pags=livros.paginas.max()

    pontos_velocidade=alt.Chart(livros).mark_point(filled=True, size=70).encode(
        x=alt.X(
            "tempo:Q",
            title="Dias",
            scale=alt.Scale(
                domain=[0,max_dias]
            ),
            axis=alt.Axis(
                grid=False,
                titleFont=font_graphs,
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs_title,
            )
        ),
        y=alt.Y(
            "paginas:Q",
            title="Páginas",
            scale=alt.Scale(
                domain=[0,max_pags]
            ),
            axis=alt.Axis(
                grid=False,
                titleFont=font_graphs,
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs_title
            )
        ),
        shape=alt.Shape(
            "estilo:N",
            scale=alt.Scale(range=["square", "circle"]),
            legend=alt.Legend(
                title="Estilo",
                orient="top-left",
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs
            )
        ),
        tooltip=[
            alt.Tooltip("livro", title="Livro"),
            alt.Tooltip("velocidade", title="Páginas/dia"),
            alt.Tooltip("estilo", title="Estilo"),
            alt.Tooltip("outlier", title="Velocidade")
        ]
    ).properties(
        width=big_width,
        height=big_height,
        title="Velocidade de leitura"
    ).add_params(selector_livro).transform_filter(selector_estilo).transform_filter(selector_nacionalidade).transform_filter(selector_livro)

    reta_rapido=alt.Chart(pd.DataFrame({"x":[0, livros.tempo.max(), livros.paginas.max()/lim_sup],
                                        "y":[0, livros.tempo.max()*lim_sup, livros.paginas.max()],
                                        "c":["Divisor lidos rápido"]*3})).mark_line(color="gray", strokeDash=[15,15], clip=True).encode(
        x=alt.X("x",scale=alt.Scale(domain=[0,max_dias])),
        y=alt.Y("y",scale=alt.Scale(domain=[0,max_pags])),
        color=alt.Color(
            "c",
            scale=alt.Scale(range=["#4285f4", "blue"]),
            legend=alt.Legend(
                title="",
                orient="top-left",
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs
            )
        )
    )

    reta_lento=alt.Chart(pd.DataFrame({"x":[0, livros.tempo.max(), livros.paginas.max()/lim_inf],
                                       "y":[0, livros.tempo.max()*lim_inf, livros.paginas.max()],
                                        "c":["Divisor lidos devagar"]*3})).mark_line(color="gray", strokeDash=[15,15], clip=True).encode(
        x=alt.X("x",scale=alt.Scale(domain=[0,max_dias])),
        y=alt.Y("y",scale=alt.Scale(domain=[0,max_pags])),
        color=alt.Color(
            "c",
            scale=alt.Scale(range=["#4285f4", "blue"]),
            legend=alt.Legend(
                title="",
                orient="top-left",
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs
            )
        )
    )

    """## Livros por estilo"""

    limite_barras_estilo=(livros.groupby("estilo").agg({"livro":"count"}).livro.max()//5+1)*5

    livros_por_estilo=alt.Chart(livros).mark_bar(height=80, cornerRadiusTopRight=5, cornerRadiusBottomRight=5, color="#4285f4").encode(
        x=alt.X(
            "count(livro):Q",
            scale=alt.Scale(
                domain=[0,limite_barras_estilo]
            ),
            axis=alt.Axis(
                title="Número de livros",
                titleFont=font_graphs,
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs_title
            )
        ),
        y=alt.Y(
            "estilo:N",
            axis=alt.Axis(
                title="",
                titleFont=font_graphs,
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs_title
            )
        ),
        tooltip=[
            alt.Tooltip("count(livro)", title="Número de livros"),
        ]
    ).properties(
        width=big_width,
        height=big_height,
        title="Livros por estilo"
    ).add_params(selector_estilo).transform_filter(selector_estilo).transform_filter(selector_nacionalidade).transform_filter(selector_livro)

    """## Top livros"""

    top_do_ano=alt.Chart(kpis).mark_text(size=font_size, font=font, lineBreak='\n').encode(
        text=alt.Text(
            "top_do_ano"
        )
    ).properties(
        width=base_width,
        height=base_height
    )

    nomes_livros=alt.Chart(cor_ranking).mark_text(baseline="middle", size=font_size_grphs_title, font=font_graphs, lineBreak='\n').encode(
        y=alt.Y('ranking:O',axis=None),
        text="livro",
        color=alt.Color(
            "cor_ranking:N",
            scale=alt.Scale(range=["gray", "black"]),
            legend=None
        ),
        tooltip=[
            alt.Tooltip("autor", title="Autor"),
            alt.Tooltip("nacionalidade", title="Nacionalidade"),
        ]
    ).properties(
        width=base_width,
        height=3*base_height
    ).add_params(selector_livro).transform_filter(selector_estilo).transform_filter(selector_nacionalidade).transform_filter(selector_livro)

    """## Livros por nacionalidade"""

    limite_barras_nacionalidade=(livros.groupby("nacionalidade").agg({"livro":"count"}).livro.max()//5+1)*5

    livros_por_nacionalidade=alt.Chart(livros).mark_bar(width=30, cornerRadiusTopRight=5, cornerRadiusTopLeft=5, color="#4285f4", dx=-50).encode(
        x=alt.X(
            "nacionalidade:N",
            sort=alt.EncodingSortField(
                field="livro",
                op="count",
                order='descending'
            ),
            axis=alt.Axis(
                labelAngle=-30,
                title="Nacionalidade",
                titleFont=font_graphs,
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs_title,
            )
        ),
        y=alt.Y(
            "count(livro):Q",
            scale=alt.Scale(
                domain=[0,limite_barras_nacionalidade]
            ),
            axis=alt.Axis(
                title="",
                titleFont=font_graphs,
                labelFontSize=font_size_grphs,
                titleFontSize=font_size_grphs_title
            )
        ),
        tooltip=[
            alt.Tooltip("count(livro)", title="Número de livros")
        ]
    ).properties(
        width=big_width,
        height=big_height,
        title="Livros por nacionalidade"
    ).add_params(selector_nacionalidade).transform_filter(selector_estilo).transform_filter(selector_nacionalidade).transform_filter(selector_livro)

    """## Créditos"""

    autor_text=alt.Chart(kpis).mark_text(size=font_size_grphs_title, font=font_graphs, lineBreak='\n').encode(
        text=alt.Text(
            "autor_text"
        )
    ).properties(
        width=base_width,
        height=base_height/3
    )

    autor=alt.Chart(kpis).mark_text(size=font_size_grphs_title, font=font_nome, lineBreak='\n').encode(
        text=alt.Text(
            "autor"
        )
    ).properties(
        width=base_width,
        height=base_height/3
    )

    insta=alt.Chart(kpis).mark_text(size=font_size_grphs_title, font=font_graphs, lineBreak='\n').encode(
        text=alt.Text(
            "insta"
        ),
        href="insta_url:N"
    ).properties(
        width=3*base_width,
        height=base_height/3
    )

    """#Dash final"""

    creditos=((autor_text | autor) & insta)
    col1=((livros_por_mes+livros_movel_por_mes) & livros_por_estilo & creditos)
    col2=(num_livros & num_paginas & num_nacionalidade & paginas_por_dia & top_do_ano & nomes_livros)
    col3=((pontos_velocidade+reta_rapido+reta_lento) & livros_por_nacionalidade)

    data=((col1 | col2 | col3)).resolve_scale(
        color='independent',
        shape="independent",
        size="independent",
        opacity="independent",
        x="independent",
        y="independent"
    )

    return titulo, data.configure_title(
        font=font_graphs,
        fontSize=1.5*font_size_grphs_title
    ).configure_view(
        stroke=None
    )

def cria_tabs(livros, usar_ano,  ano):
    # -*- coding: utf-8 -*-
    """relatorio_livros.ipynb

    Automatically generated by Colaboratory.

    Original file is located at
        https://colab.research.google.com/drive/1kjqvCQtdYqioVua9DIb7QUTSSTSlAvGO
    """

    """#Enriquecimento

    ##Novas colunas
    """

    livros["velocidade"]=round(livros.paginas/livros.tempo)
    lim_letras=25
    Q1=livros.velocidade.quantile(.25)
    Q3=livros.velocidade.quantile(.75)
    IQR=Q3-Q1
    lim_inf=Q1-1.5*IQR
    lim_sup=Q3+1.5*IQR
    livros["outlier"]=livros.velocidade.apply(lambda vel: "Rápido" if vel>lim_sup else "Devagar" if vel<lim_inf else "Normal")
    livros["mes"]=livros.data.dt.month
    livros["num_livros"]="Número de Livros"
    livros["livro"]=livros.livro.apply(lambda nome: "\n".join([nome[i:i+lim_letras] for i  in range(0, len(nome), lim_letras)]))
    livros["livro"]=livros.livro.str.replace("\n\n", "\n")

    titulo, data=faz_grafico(livros, usar_ano, ano)
    st.altair_chart(titulo, use_container_width=True)
    st.altair_chart(data, use_container_width=True)
