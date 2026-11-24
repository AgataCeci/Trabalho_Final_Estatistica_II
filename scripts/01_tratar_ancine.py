
import pandas as pd
from pathlib import Path

# =========================================
# 1. DEFINIR OS CAMINHOS
# =========================================

PROJETO = Path(__file__).resolve().parent.parent

arquivo = (
    PROJETO
    / "dados"
    / "originais"
    / "publico-renda-e-numero-de-lancamentos-por-tipo-de-distribuidora-2009-a-2025.csv"
)

pasta_saida = PROJETO / "dados" / "processados"

pasta_saida.mkdir(parents=True, exist_ok=True)

# =========================================
# 2. IMPORTAR A BASE ORIGINAL
# =========================================

dados = pd.read_csv(
    arquivo,
    sep=";",
    header=None,
    encoding="utf-8-sig",
    dtype=str
)

print("Arquivo da ANCINE importado!")

# =========================================
# 3. IDENTIFICAR OS ANOS
# =========================================

linha_anos = dados.iloc[1]

colunas_anos = {}

for coluna in range(1, dados.shape[1]):

    valor = linha_anos.iloc[coluna]

    if pd.notna(valor) and valor.strip().isdigit():

        ano = int(valor.strip())

        if 2010 <= ano <= 2025:
            colunas_anos[ano] = coluna

# =========================================
# 4. LOCALIZAR AS LINHAS DE PÚBLICO
# =========================================

rotulos = dados.iloc[:, 0].str.strip()

linha_br = dados[
    rotulos == "Público - Filmes Brasileiros"
]

linha_estrangeiros = dados[
    rotulos == "Público - Filmes Estrangeiros"
]

if len(linha_br) != 1 or len(linha_estrangeiros) != 1:
    raise ValueError("Não foi possível localizar as linhas de público.")

linha_br = linha_br.iloc[0]
linha_estrangeiros = linha_estrangeiros.iloc[0]

# =========================================
# 5. CONVERTER OS VALORES
# =========================================

def converter_publico(valor):

    if pd.isna(valor) or valor.strip() in ["", "-"]:
        return pd.NA

    return int(valor.replace(".", "").strip())

# =========================================
# 6. CRIAR A NOVA TABELA
# =========================================

resultado = []

for ano in sorted(colunas_anos):

    coluna = colunas_anos[ano]

    publico_br = converter_publico(
        linha_br.iloc[coluna]
    )

    publico_estrangeiro = converter_publico(
        linha_estrangeiros.iloc[coluna]
    )

    resultado.append({
        "ANO": ano,
        "PUBLICO_BRASILEIRO": publico_br,
        "PUBLICO_ESTRANGEIRO": publico_estrangeiro
    })

base_cinema = pd.DataFrame(resultado)

# =========================================
# 7. EXPORTAR OS RESULTADOS
# =========================================

base_cinema.to_csv(
    pasta_saida / "base_cinema.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print("\nBASE DA ANCINE CRIADA COM SUCESSO!")
print(base_cinema.to_string(index=False))
