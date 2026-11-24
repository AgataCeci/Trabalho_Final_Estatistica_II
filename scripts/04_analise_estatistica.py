
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
