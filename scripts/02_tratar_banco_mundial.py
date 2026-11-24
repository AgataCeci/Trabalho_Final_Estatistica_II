
import pandas as pd
from pathlib import Path

# 1. Localizar as pastas
pasta_projeto = Path(__file__).resolve().parent.parent
pasta_dados = pasta_projeto / "dados" / "originais"
pasta_saida = pasta_projeto / "dados" / "processados"

pasta_saida.mkdir(parents=True, exist_ok=True)

# 2. Ler os arquivos do Banco Mundial
arquivo_pib = pasta_dados / "crescimento_pib.csv"
arquivo_per_capita = pasta_dados / "crescimento_pib_per_capita.csv"

df_pib = pd.read_csv(arquivo_pib, skiprows=4)
df_per_capita = pd.read_csv(arquivo_per_capita, skiprows=4)

# 3. Definir os anos
anos = [str(ano) for ano in range(2010, 2026)]

# 4. Filtrar o Brasil
brasil_pib = df_pib[df_pib["Country Code"] == "BRA"]
brasil_per_capita = df_per_capita[
    df_per_capita["Country Code"] == "BRA"
]

if len(brasil_pib) != 1 or len(brasil_per_capita) != 1:
    raise ValueError("Não foi encontrada exatamente uma linha para o Brasil.")

# 5. Criar a tabela de crescimento do PIB
tabela_pib = brasil_pib[anos].T.reset_index()
tabela_pib.columns = ["ANO", "CRESCIMENTO_PIB_PERCENTUAL"]

# 6. Criar a tabela de crescimento do PIB per capita
tabela_per_capita = brasil_per_capita[anos].T.reset_index()
tabela_per_capita.columns = [
    "ANO",
    "CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL"
]

# 7. Converter os dados para números
for tabela in [tabela_pib, tabela_per_capita]:
    tabela["ANO"] = tabela["ANO"].astype(int)

tabela_pib["CRESCIMENTO_PIB_PERCENTUAL"] = pd.to_numeric(
    tabela_pib["CRESCIMENTO_PIB_PERCENTUAL"],
    errors="coerce"
)

tabela_per_capita["CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL"] = pd.to_numeric(
    tabela_per_capita["CRESCIMENTO_PIB_PER_CAPITA_PERCENTUAL"],
    errors="coerce"
)

# 8. Unir as duas tabelas
base_crescimento = pd.merge(
    tabela_pib,
    tabela_per_capita,
    on="ANO",
    how="inner"
)

base_crescimento = base_crescimento.sort_values("ANO")

# 9. Exibir o resultado
print("\nCRESCIMENTO REAL DO PIB E DO PIB PER CAPITA")
print(base_crescimento.to_string(index=False))

# 10. Salvar a tabela
base_crescimento.to_csv(
    pasta_saida / "base_crescimento_pib.csv",
    index=False
)

print("\nTabela salva com sucesso!")
