
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import pearsonr, spearmanr, linregress

# 1. Localizar as pastas
pasta_projeto = Path(__file__).resolve().parent.parent
pasta_dados = pasta_projeto / "dados" / "processados"
pasta_graficos = pasta_projeto / "resultados" / "graficos"

pasta_graficos.mkdir(parents=True, exist_ok=True)

# 2. Ler a base final
df = pd.read_csv(pasta_dados / "base_final_pesquisa.csv")

df = df.sort_values("ANO").reset_index(drop=True)

# 3. Calcular a variação anual do público
df["VARIACAO_PUBLICO_BRASILEIRO_PERCENTUAL"] = (
    df["PUBLICO_BRASILEIRO"].pct_change(fill_method=None) * 100
)

df["VARIACAO_PUBLICO_ESTRANGEIRO_PERCENTUAL"] = (
    df["PUBLICO_ESTRANGEIRO"].pct_change(fill_method=None) * 100
)

# 4. Calcular a mudança na participação nacional
df["VARIACAO_PARTICIPACAO_NACIONAL_PONTOS"] = (
    df["PARTICIPACAO_NACIONAL_PERCENTUAL"].diff()
)

# 5. Exibir as novas variáveis
print("\nVARIAÇÕES ANUAIS DO PÚBLICO")
print(
    df[[
        "ANO",
        "CRESCIMENTO_PIB_PERCENTUAL",
        "CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL",
        "VARIACAO_PUBLICO_BRASILEIRO_PERCENTUAL",
        "VARIACAO_PUBLICO_ESTRANGEIRO_PERCENTUAL",
        "VARIACAO_PARTICIPACAO_NACIONAL_PONTOS"
    ]].to_string(index=False)
)

# 6. Estatísticas descritivas
print("\nESTATÍSTICAS DESCRITIVAS")
print(df.describe().round(2).to_string())

# 7. Definir as variáveis para as correlações
variaveis_economicas = [
    "CRESCIMENTO_PIB_PERCENTUAL",
    "CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL"
]

variaveis_cinema = [
    "VARIACAO_PUBLICO_BRASILEIRO_PERCENTUAL",
    "VARIACAO_PUBLICO_ESTRANGEIRO_PERCENTUAL",
    "VARIACAO_PARTICIPACAO_NACIONAL_PONTOS"
]

# 8. Calcular Pearson e Spearman

# 8. Calcular Pearson e Spearman, incluindo valores-p
resultados = []

for economia in variaveis_economicas:
    for cinema in variaveis_cinema:

        dados = df[[economia, cinema]].dropna()

        pearson, p_pearson = pearsonr(
            dados[economia],
            dados[cinema]
        )

        spearman, p_spearman = spearmanr(
            dados[economia],
            dados[cinema]
        )

        resultados.append({
            "INDICADOR_ECONOMICO": economia,
            "INDICADOR_CINEMA": cinema,
            "OBSERVACOES": len(dados),
            "PEARSON": pearson,
            "P_VALOR_PEARSON": p_pearson,
            "SPEARMAN": spearman,
            "P_VALOR_SPEARMAN": p_spearman
        })

tabela_correlacoes = pd.DataFrame(resultados)

print("\nRESULTADOS DAS CORRELAÇÕES")
print(tabela_correlacoes.round(4).to_string(index=False))


# ==========================================
# 8.1 GERAR IMAGENS PNG DAS TABELAS
# ==========================================

# Criar pasta para armazenar as tabelas
pasta_tabelas = pasta_graficos / "tabelas"
pasta_tabelas.mkdir(parents=True, exist_ok=True)


# Função para transformar uma tabela em imagem PNG
def salvar_tabela_png(tabela, caminho, titulo, tamanho_fonte=8):

    # Criar uma cópia para não alterar os dados originais
    tabela_visual = tabela.copy()

    # Formatar os valores numéricos
    for coluna in tabela_visual.columns:

        if pd.api.types.is_float_dtype(tabela_visual[coluna]):
            tabela_visual[coluna] = tabela_visual[coluna].map(
                lambda valor: f"{valor:.2f}" if pd.notna(valor) else ""
            )

        elif pd.api.types.is_integer_dtype(tabela_visual[coluna]):
            tabela_visual[coluna] = tabela_visual[coluna].astype(str)

    # Definir tamanho da imagem conforme a tabela
    largura = max(12, len(tabela_visual.columns) * 2.2)
    altura = max(3, len(tabela_visual) * 0.45 + 2)

    fig, ax = plt.subplots(figsize=(largura, altura))

    # Retirar os eixos
    ax.axis("off")

    # Título da tabela
    ax.set_title(
        titulo,
        fontsize=13,
        fontweight="bold",
        pad=20
    )

    # Criar tabela
    tabela_imagem = ax.table(
        cellText=tabela_visual.values,
        colLabels=tabela_visual.columns,
        cellLoc="center",
        loc="center"
    )

    # Ajustar aparência
    tabela_imagem.auto_set_font_size(False)
    tabela_imagem.set_fontsize(tamanho_fonte)
    tabela_imagem.scale(1, 1.6)

    # Destacar os cabeçalhos
    for (linha, coluna), celula in tabela_imagem.get_celld().items():

        if linha == 0:
            celula.set_text_props(weight="bold")

    plt.tight_layout()

    # Salvar imagem
    plt.savefig(
        caminho,
        dpi=300,
        bbox_inches="tight",
        facecolor="white"
    )

    plt.close()


# ------------------------------------------
# TABELA 1: VARIACOES ANUAIS
# ------------------------------------------

tabela_variacoes = df[[
    "ANO",
    "CRESCIMENTO_PIB_PERCENTUAL",
    "CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL",
    "VARIACAO_PUBLICO_BRASILEIRO_PERCENTUAL",
    "VARIACAO_PUBLICO_ESTRANGEIRO_PERCENTUAL",
    "VARIACAO_PARTICIPACAO_NACIONAL_PONTOS"
]].copy()

tabela_variacoes = tabela_variacoes.rename(columns={
    "ANO": "Ano",
    "CRESCIMENTO_PIB_PERCENTUAL": "Crescimento PIB (%)",
    "CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL": "Crescimento PIB per capita (%)",
    "VARIACAO_PUBLICO_BRASILEIRO_PERCENTUAL": "Variacao publico brasileiro (%)",
    "VARIACAO_PUBLICO_ESTRANGEIRO_PERCENTUAL": "Variacao publico estrangeiro (%)",
    "VARIACAO_PARTICIPACAO_NACIONAL_PONTOS": "Variacao participacao nacional (p.p.)"
})

salvar_tabela_png(
    tabela_variacoes,
    pasta_tabelas / "tabela_variacoes_anuais.png",
    "Variacoes anuais das variaveis (2010-2025)",
    tamanho_fonte=7
)


# ------------------------------------------
# TABELA 2: ESTATISTICAS DESCRITIVAS
# ------------------------------------------

variaveis_descritivas = [
    "CRESCIMENTO_PIB_PERCENTUAL",
    "CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL",
    "VARIACAO_PUBLICO_BRASILEIRO_PERCENTUAL",
    "VARIACAO_PUBLICO_ESTRANGEIRO_PERCENTUAL",
    "PARTICIPACAO_NACIONAL_PERCENTUAL",
    "VARIACAO_PARTICIPACAO_NACIONAL_PONTOS"
]

tabela_descritiva = df[variaveis_descritivas].describe().T.reset_index()

tabela_descritiva = tabela_descritiva.rename(columns={
    "index": "Variavel",
    "CRESCIMENTO_PIB_PERCENTUAL": "Crescimento PIB",
    "CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL": "Crescimento PIB per capita",
    "VARIACAO_PUBLICO_BRASILEIRO_PERCENTUAL": "Variacao publico brasileiro",
    "VARIACAO_PUBLICO_ESTRANGEIRO_PERCENTUAL": "Variacao publico estrangeiro",
    "PARTICIPACAO_NACIONAL_PERCENTUAL": "Participacao nacional",
    "VARIACAO_PARTICIPACAO_NACIONAL_PONTOS": "Variacao participacao nacional"
})

salvar_tabela_png(
    tabela_descritiva,
    pasta_tabelas / "tabela_estatisticas_descritivas.png",
    "Estatisticas descritivas das variaveis",
    tamanho_fonte=8
)


# ------------------------------------------
# TABELA 3: RESULTADOS DAS CORRELACOES
# ------------------------------------------

tabela_correlacoes_png = tabela_correlacoes.copy()

tabela_correlacoes_png = tabela_correlacoes_png.rename(columns={
    "INDICADOR_ECONOMICO": "Indicador economico",
    "INDICADOR_CINEMA": "Indicador cinematografico",
    "OBSERVACOES": "N",
    "PEARSON": "Pearson (r)",
    "P_VALOR_PEARSON": "Valor-p Pearson",
    "SPEARMAN": "Spearman",
    "P_VALOR_SPEARMAN": "Valor-p Spearman"
})

# Simplificar os nomes para melhorar a leitura
tabela_correlacoes_png["Indicador economico"] = (
    tabela_correlacoes_png["Indicador economico"].replace({
        "CRESCIMENTO_PIB_PERCENTUAL": "Crescimento do PIB",
        "CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL": "Crescimento do PIB per capita"
    })
)

tabela_correlacoes_png["Indicador cinematografico"] = (
    tabela_correlacoes_png["Indicador cinematografico"].replace({
        "VARIACAO_PUBLICO_BRASILEIRO_PERCENTUAL": "Variacao publico brasileiro",
        "VARIACAO_PUBLICO_ESTRANGEIRO_PERCENTUAL": "Variacao publico estrangeiro",
        "VARIACAO_PARTICIPACAO_NACIONAL_PONTOS": "Variacao participacao nacional"
    })
)

salvar_tabela_png(
    tabela_correlacoes_png,
    pasta_tabelas / "tabela_correlacoes.png",
    "Correlacoes entre economia e mercado cinematografico",
    tamanho_fonte=8
)


print("\nIMAGENS DAS TABELAS GERADAS COM SUCESSO!")
print(f"Tabelas salvas em: {pasta_tabelas}")


# 9. Salvar as tabelas
df.to_csv(
    pasta_dados / "base_com_variacoes.csv",
    index=False
)

tabela_correlacoes.to_csv(
    pasta_dados / "resultados_correlacoes.csv",
    index=False
)

# 10. Gráfico: evolução do público
plt.figure(figsize=(10, 6))

plt.plot(
    df["ANO"],
    df["PUBLICO_BRASILEIRO"] / 1_000_000,
    marker="o",
    label="Filmes brasileiros"
)

plt.plot(
    df["ANO"],
    df["PUBLICO_ESTRANGEIRO"] / 1_000_000,
    marker="o",
    label="Filmes estrangeiros"
)

plt.title("Evolução do público de cinema no Brasil")
plt.xlabel("Ano")
plt.ylabel("Público (milhões de espectadores)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    pasta_graficos / "evolucao_publico.png",
    dpi=300
)

plt.close()

# 11. Gráfico: crescimento econômico
plt.figure(figsize=(10, 6))

plt.plot(
    df["ANO"],
    df["CRESCIMENTO_PIB_PERCENTUAL"],
    marker="o",
    label="Crescimento real do PIB"
)

plt.plot(
    df["ANO"],
    df["CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL"],
    marker="o",
    label="Crescimento real do PIB per capita"
)

plt.axhline(0, linestyle="--")
plt.title("Crescimento econômico do Brasil")
plt.xlabel("Ano")
plt.ylabel("Variação anual (%)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    pasta_graficos / "crescimento_economico.png",
    dpi=300
)

plt.close()

# 12. Gráfico: participação nacional
plt.figure(figsize=(10, 6))

plt.plot(
    df["ANO"],
    df["PARTICIPACAO_NACIONAL_PERCENTUAL"],
    marker="o"
)

plt.title("Participação dos filmes brasileiros no público total")
plt.xlabel("Ano")
plt.ylabel("Participação nacional (%)")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    pasta_graficos / "participacao_nacional.png",
    dpi=300
)

plt.close()

print("\nAnálise inicial concluída!")
print("Tabelas e gráficos salvos nas pastas do projeto.")


# ==========================================
# 6. GRAFICOS DE DISPERSAO
# ==========================================

# Criar pasta para armazenar os seis graficos
pasta_dispersao = pasta_graficos / "dispersao"
pasta_dispersao.mkdir(parents=True, exist_ok=True)

# Nomes mais claros para aparecer nos graficos
nomes_economicos = {
    "CRESCIMENTO_PIB_PERCENTUAL": "Crescimento anual do PIB (%)",
    "CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL": "Crescimento anual do PIB per capita (%)"
}

nomes_cinema = {
    "VARIACAO_PUBLICO_BRASILEIRO_PERCENTUAL":
        "Variação do público de filmes brasileiros (%)",

    "VARIACAO_PUBLICO_ESTRANGEIRO_PERCENTUAL":
        "Variação do público de filmes estrangeiros (%)",

    "VARIACAO_PARTICIPACAO_NACIONAL_PONTOS":
        "Variação da participação do cinema nacional (pontos percentuais)"
}

# Combinar os dois indicadores economicos com os tres indicadores de cinema
for economia in variaveis_economicas:

    for cinema in variaveis_cinema:

        # Selecionar somente as colunas necessárias e retirar valores ausentes
        dados = df[[economia, cinema]].dropna()

        # Separar os eixos X e Y
        x = dados[economia]
        y = dados[cinema]

        # Calcular a linha de tendencia linear
        resultado = linregress(x, y)

        # Criar o grafico
        plt.figure(figsize=(9, 6))

        # Pontos do grafico
        plt.scatter(x, y, alpha=0.8, s=60)

        # Linha de tendencia
        x_linha = [x.min(), x.max()]
        y_linha = [
            resultado.intercept + resultado.slope * valor
            for valor in x_linha
        ]

        plt.plot(
            x_linha,
            y_linha,
            linestyle="--",
            linewidth=2,
            label="Linha de tendência"
        )

        # Titulo e nomes dos eixos
        plt.title(
            f"{nomes_economicos[economia]}\n"
            f"e {nomes_cinema[cinema]}",
            fontsize=12
        )

        plt.xlabel(nomes_economicos[economia])
        plt.ylabel(nomes_cinema[cinema])

        # Mostrar o coeficiente de Pearson
        r, p = pearsonr(x, y)

        plt.text(
            0.05,
            0.95,
            f"Correlação de Pearson (r) = {r:.3f}\n"
            f"Valor-p = {p:.3f}",
            transform=plt.gca().transAxes,
            verticalalignment="top",
            bbox=dict(facecolor="white", alpha=0.8)
        )

        plt.axhline(0, linewidth=0.7, alpha=0.5)
        plt.axvline(0, linewidth=0.7, alpha=0.5)

        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Nome do arquivo
        nome_arquivo = f"dispersao_{economia}_{cinema}.png"

        # Salvar imagem
        plt.savefig(
            pasta_dispersao / nome_arquivo,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

print("\nSEIS GRAFICOS DE DISPERSAO GERADOS COM SUCESSO!")
print(f"Arquivos salvos em: {pasta_dispersao}")
