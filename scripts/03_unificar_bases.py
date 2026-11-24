import pandas as pd
from pathlib import Path

# 1. Localizar as pastas
pasta_projeto = Path(__file__).resolve().parent.parent
pasta_dados = pasta_projeto / "dados" / "processados"

# 2. Ler as bases já tratadas
cinema = pd.read_csv(
    pasta_dados / "base_cinema.csv",
    sep=";"
)

economia = pd.read_csv(
    pasta_dados / "base_crescimento_pib.csv"
)

# 3. Padronizar os nomes das colunas
cinema.columns = cinema.columns.str.strip()
economia.columns = economia.columns.str.strip()

# 4. Garantir que o ano seja numérico
cinema["ANO"] = pd.to_numeric(cinema["ANO"], errors="coerce")
economia["ANO"] = pd.to_numeric(economia["ANO"], errors="coerce")

# 5. Juntar as bases pelo ano
base_final = pd.merge(
    cinema,
    economia,
    on="ANO",
    how="inner"
)

# 6. Ordenar os dados cronologicamente
base_final = base_final.sort_values("ANO")

# 7. Calcular a participação do cinema nacional no público total
base_final["PUBLICO_TOTAL"] = (
    base_final["PUBLICO_BRASILEIRO"]
    + base_final["PUBLICO_ESTRANGEIRO"]
)

base_final["PARTICIPACAO_NACIONAL_PERCENTUAL"] = (
    base_final["PUBLICO_BRASILEIRO"]
    / base_final["PUBLICO_TOTAL"]
) * 100

# 8. Exibir a tabela
print("\nBASE FINAL DA PESQUISA")
print(base_final.to_string(index=False))

# 9. Salvar a base unificada
base_final.to_csv(
    pasta_dados / "base_final_pesquisa.csv",
    index=False
)

print("\nBase final criada com sucesso!")