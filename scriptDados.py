import yfinance as yf
import pandas as pd
from functools import reduce

ticker = yf.Ticker("KGC")

info = ticker.info
free_float = info.get("floatShares")
shares_outstanding = info.get("sharesOutstanding")
market_cap_atual = info.get("marketCap")

#income
income = ticker.financials

#receita
receita = income.loc["Total Revenue"]
receita = receita.reset_index()
receita.columns = ["Date", "Receita"]

receita["Year"] = pd.to_datetime(receita["Date"]).dt.year
receita = receita[["Year", "Receita"]]

#lucro_bruto bruto
lucro_bruto = income.loc["Gross Profit"]
lucro_bruto = lucro_bruto.reset_index()
lucro_bruto.columns = ["Date", "Lucro Bruto"]

lucro_bruto["Year"] = pd.to_datetime(lucro_bruto["Date"]).dt.year
lucro_bruto = lucro_bruto[["Year", "Lucro Bruto"]]

#lucro liquido
lucro_liquido = income.loc["Net Income"]
lucro_liquido = lucro_liquido.reset_index()
lucro_liquido.columns = ["Date", "Lucro Líquido"]

lucro_liquido["Year"] = pd.to_datetime(lucro_liquido["Date"]).dt.year
lucro_liquido = lucro_liquido[["Year", "Lucro Líquido"]]

#despesas gerais
despesas = income.loc["Selling General And Administration"]
despesas = despesas.reset_index()
despesas.columns = ["Date", "SGA"]

despesas["Year"] = pd.to_datetime(despesas["Date"]).dt.year
despesas = despesas[["Year", "SGA"]]

#ebitda
ebitda = income.loc["EBITDA"]
ebitda = ebitda.reset_index()
ebitda.columns = ["Date", "EBITDA"]

ebitda["Year"] = pd.to_datetime(ebitda["Date"]).dt.year
ebitda = ebitda[["Year", "EBITDA"]]

#operating income
operacional = income.loc["Operating Income"]
operacional = operacional.reset_index()
operacional.columns = ["Date", "Operating_Income"]

operacional["Year"] = pd.to_datetime(operacional["Date"]).dt.year
operacional = operacional[["Year", "Operating_Income"]]


#percentual de free float
if free_float and shares_outstanding:
    percentual_free_float = free_float / shares_outstanding * 100
else:
    percentual_free_float = None


#resumo
resumo = pd.DataFrame({
    "Indicador": [
        "Empresa", "Ticker",
        "Free float (ações)", "Free float (%)",
        "Ações em circulação",
        "Valor de mercado atual"
    ],
    "Valor": [
        "Kinross Gold", "KGC",
        free_float, f"{percentual_free_float:.2f}%" if percentual_free_float else None,
        shares_outstanding,
        market_cap_atual
    ]
})

#patrimonio liquido
balanco_tri = ticker.quarterly_balance_sheet
patrimonio_tri = balanco_tri.loc["Total Equity Gross Minority Interest"]
patrimonio_tri = patrimonio_tri.reset_index()
patrimonio_tri.columns = ["Data", "Patrimonio_Liquido"]
patrimonio_tri["Quarter"] = pd.to_datetime(patrimonio_tri["Data"]).dt.to_period("Q")
patrimonio_tri["Quarter"] = patrimonio_tri["Quarter"].astype(str)

# BASE DIÁRIA
diario = ticker.history(start="2020-01-01", end="2025-12-31", interval="1d")
diario = diario[["Close", "Volume"]]
diario.reset_index(inplace=True)
diario["Date"] = diario["Date"].dt.tz_localize(None)

# BASE TRIMESTRAL

trimestral = diario.copy()
trimestral["Quarter"] = trimestral["Date"].dt.to_period("Q").astype(str)

trimestral = trimestral.groupby("Quarter").agg(
    volume_medio_trimestral=("Volume", "mean")
).reset_index()

trimestral = pd.merge(
    trimestral,
    patrimonio_tri[["Quarter", "Patrimonio_Liquido"]],
    on="Quarter",
    how="left"
)

# BASE MENSAL
mensal = diario.copy()
mensal["YearMonth"] = mensal["Date"].dt.to_period("M").astype(str)

mensal = mensal.groupby("YearMonth").agg(
    preco_medio_fechamento=("Close", "mean"),
    volume_medio=("Volume", "mean")
).reset_index()

#retorno mensal
retorno_mensal = diario.groupby(diario["Date"].dt.to_period("M")).agg(
    preco_fechamento_ultimo=("Close", "last"),
    preco_fechamento_primeiro=("Close", "first")
).reset_index()

retorno_mensal["retorno_mensal"] = (
    retorno_mensal["preco_fechamento_ultimo"] / retorno_mensal["preco_fechamento_primeiro"] - 1
)

retorno_mensal["Date"] = retorno_mensal["Date"].astype(str)

mensal = pd.merge(
    mensal,
    retorno_mensal[["Date", "retorno_mensal"]],
    left_on="YearMonth",
    right_on="Date",
    how="left"
)

mensal.drop(columns="Date", inplace=True)

# BASE ANUAL
anual = diario.copy()
anual["Year"] = anual["Date"].dt.year

anual = anual.groupby("Year").agg(
    preco_medio_fechamento=("Close", "mean"),
    volume_medio=("Volume", "mean")
).reset_index()

retorno_anual = diario.groupby(diario["Date"].dt.year).agg(
    preco_fechamento_ultimo=("Close", "last"),
    preco_fechamento_primeiro=("Close", "first")
).reset_index()

retorno_anual["retorno_anual"] = (
    retorno_anual["preco_fechamento_ultimo"] / retorno_anual["preco_fechamento_primeiro"] - 1
)

retorno_anual.rename(columns={"Date": "Year"}, inplace=True)


dfs = [
    anual,
    receita,
    lucro_bruto,
    lucro_liquido,
    despesas,
    ebitda,
    operacional
]

anual = reduce(lambda left, right: pd.merge(left, right, on="Year", how="left"), dfs)

anual["margem_bruta(%)"] = (anual["Lucro Bruto"]/anual["Receita"]) * 100

anual["margem_ebtida(%)"] = anual["EBITDA"] / anual["Receita"] * 100

anual["margem_operacional(%)"] = anual["Operating_Income"] / anual["Receita"] * 100

anual['margem_liquida(%)'] = anual["Lucro Líquido"] / anual["Receita"] * 100


# valor de mercado anual (estimado)
if shares_outstanding:
    anual["valor_mercado_estimado"] = anual["preco_medio_fechamento"] * shares_outstanding
else:
    anual["valor_mercado_estimado"] = None

# SALVAR NO EXCEL
with pd.ExcelWriter("kinross_gold_2020_2025.xlsx", engine="openpyxl") as writer:
    resumo.to_excel(writer, sheet_name="Resumo", index=False)
    anual.to_excel(writer, sheet_name="Anual", index=False)
    trimestral.to_excel(writer, sheet_name = "Trimestral", index=False)
    mensal.to_excel(writer, sheet_name="Mensal", index=False)
    diario.to_excel(writer, sheet_name="Diario", index=False)