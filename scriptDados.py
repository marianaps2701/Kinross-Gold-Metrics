import yfinance as yf
import pandas as pd
from functools import reduce

ticker = yf.Ticker("KGC")

info = ticker.info
free_float = info.get("floatShares")
shares_outstanding = info.get("sharesOutstanding")
market_cap_atual = info.get("marketCap")
div_yield = info.get("dividendYield")

#income
income = ticker.financials

#balanço
balanco = ticker.balance_sheet

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

#divida bruta
divida_bruta = balanco.loc["Total Debt"]
divida_bruta = divida_bruta.reset_index()
divida_bruta.columns = ["Date", "Divida_Bruta"]

divida_bruta["Year"] = pd.to_datetime(divida_bruta["Date"]).dt.year
divida_bruta = divida_bruta[["Year", "Divida_Bruta"]]

#liquidez corrente
ativo_circulante = balanco.loc["Current Assets"]
passivo_circulante = balanco.loc['Current Liabilities']

liq_corrente = ativo_circulante / passivo_circulante
liq_corrente = liq_corrente.reset_index()
liq_corrente.columns = ["Date", "Liquidez_Corrente"]

liq_corrente["Year"] = pd.to_datetime(liq_corrente["Date"]).dt.year
liq_corrente = liq_corrente[["Year", "Liquidez_Corrente"]]

#patrimonio liquido
balanco_tri = ticker.quarterly_balance_sheet

#trimestral
patrimonio_liq_tri = balanco_tri.loc["Total Equity Gross Minority Interest"]
patrimonio_liq_tri = patrimonio_liq_tri.reset_index()
patrimonio_liq_tri.columns = ["Data", "Patrimonio_Liquido"]
patrimonio_liq_tri["Quarter"] = pd.to_datetime(patrimonio_liq_tri["Data"]).dt.to_period("Q")
patrimonio_liq_tri["Quarter"] = patrimonio_liq_tri["Quarter"].astype(str)

#anual
patrimonio_liq = balanco.loc["Total Equity Gross Minority Interest"]
patrimonio_liq = patrimonio_liq.reset_index()
patrimonio_liq.columns = ["Data", "Patrimonio_Liquido"]
patrimonio_liq["Year"] = pd.to_datetime(patrimonio_liq["Data"]).dt.year
patrimonio_liq = patrimonio_liq[["Year", "Patrimonio_Liquido"]]

#shares
eps = income.loc["Basic EPS"]
lucro = income.loc["Net Income"]
shares = lucro/eps

shares = shares.reset_index()
shares.columns = ["Date", "Shares"]
shares["Year"] = pd.to_datetime(shares["Date"]).dt.year
shares = shares[["Year", "Shares"]]

#ativos totais
ativos = balanco.loc["Total Assets"]
ativos = ativos.reset_index()
ativos.columns = ["Date", "Total_Assets"]

ativos["Year"] = pd.to_datetime(ativos["Date"]).dt.year
ativos = ativos[["Year", "Total_Assets"]]

#caixa
caixa = balanco.loc["Cash And Cash Equivalents"]
caixa = caixa.reset_index()
caixa.columns = ["Date", "Cash"]

caixa["Year"] = pd.to_datetime(caixa["Date"]).dt.year
caixa = caixa[["Year", "Cash"]]

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
        "Valor de mercado atual",
        "Dividend Yield (12M)"
    ],
    "Valor": [
        "Kinross Gold", "KGC",
        free_float, f"{percentual_free_float:.2f}%" if percentual_free_float else None,
        shares_outstanding,
        market_cap_atual,
        div_yield
    ]
})

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
    patrimonio_liq_tri[["Quarter", "Patrimonio_Liquido"]],
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
    operacional,
    divida_bruta,
    liq_corrente,
    patrimonio_liq,
    shares,
    ativos,
    caixa
]

anual = reduce(lambda left, right: pd.merge(left, right, on="Year", how="left"), dfs)

anual["margem_bruta(%)"] = (anual["Lucro Bruto"]/anual["Receita"]) * 100

anual["margem_ebtida(%)"] = anual["EBITDA"] / anual["Receita"] * 100

anual["margem_operacional(%)"] = anual["Operating_Income"] / anual["Receita"] * 100

anual['margem_liquida(%)'] = anual["Lucro Líquido"] / anual["Receita"] * 100

anual["LPA"] = anual["Lucro Líquido"] / anual["Shares"]

anual["VPA"] = anual["Patrimonio_Liquido"] / anual["Shares"]

anual["PL"] = anual["preco_medio_fechamento"] / anual["LPA"]

anual["P_VPA"] = anual["preco_medio_fechamento"] / anual["VPA"]

anual["ROE"] = anual["Lucro Líquido"] / anual["Patrimonio_Liquido"]

# ROA
anual["ROA"] = anual["Lucro Líquido"] / anual["Total_Assets"]

# ROIC (aproximação)
anual["NOPAT"] = anual["Operating_Income"] * 0.7  # assumindo 30% imposto
anual["Capital_Investido"] = anual["Total_Assets"] - anual["Cash"]

anual["ROIC"] = anual["NOPAT"] / anual["Capital_Investido"]

anual["ROE"] = anual["ROE"] * 100
anual["ROA"] = anual["ROA"] * 100
anual["ROIC"] = anual["ROIC"] * 100

anual["valor_mercado"] = anual["preco_medio_fechamento"] * anual["Shares"]

anual["PSR"] = anual["valor_mercado"] / anual["Receita"]

# SALVAR NO EXCEL
with pd.ExcelWriter("kinross_gold_2020_2025.xlsx", engine="openpyxl") as writer:
    resumo.to_excel(writer, sheet_name="Resumo", index=False)
    anual.to_excel(writer, sheet_name="Anual", index=False)
    trimestral.to_excel(writer, sheet_name = "Trimestral", index=False)
    mensal.to_excel(writer, sheet_name="Mensal", index=False)
    diario.to_excel(writer, sheet_name="Diario", index=False)