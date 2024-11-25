import kagglehub
import matplotlib.pyplot as plt
import pandas as pd

# Baixar a última versão do dataset
path = kagglehub.dataset_download("rohanrao/formula-1-world-championship-1950-2020")

# Carregar os dados das tabelas desejadas usando o path
driver_standings = pd.read_csv(f"{path}/driver_standings.csv")
constructor_standings = pd.read_csv(f"{path}/constructor_standings.csv")
races = pd.read_csv(f"{path}/races.csv")
lap_times = pd.read_csv(f"{path}/lap_times.csv")
pit_stops = pd.read_csv(f"{path}/pit_stops.csv")
seasons = pd.read_csv(f"{path}/seasons.csv")

# 1. Analisar o desempenho dos pilotos ao longo dos anos
piloto_por_ano = driver_standings.groupby(['driverId', 'year'])['points'].sum().unstack()
piloto_por_ano = piloto_por_ano.fillna(0)

# 2. Determinar o piloto com maior número de vitórias em uma temporada
vitorias_por_piloto = driver_standings[driver_standings['wins'] > 0].groupby(['driverId', 'year'])['wins'].sum()
piloto_com_mais_vitorias = vitorias_por_piloto.groupby('year').idxmax()

# 3. Verificar a média de pontos dos pilotos por temporada
media_pontos_por_temporada = driver_standings.groupby(['year'])['points'].mean()

# Gráfico de desempenho dos pilotos ao longo dos anos
plt.figure(figsize=(10, 6))
for piloto in piloto_por_ano.index[:5]:
    plt.plot(piloto_por_ano.columns, piloto_por_ano.loc[piloto], label=f"Piloto {piloto}")
plt.xlabel("Ano")
plt.ylabel("Pontos")
plt.title("Desempenho dos Pilotos ao Longo dos Anos")
plt.legend(title="Pilotos")
plt.show()

# Gráfico de média de pontos dos pilotos por temporada
plt.figure(figsize=(10, 6))
plt.plot(media_pontos_por_temporada.index, media_pontos_por_temporada.values, marker='o', color='b')
plt.xlabel("Ano")
plt.ylabel("Média de Pontos")
plt.title("Média de Pontos dos Pilotos por Temporada")
plt.grid()
plt.show()
