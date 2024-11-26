import os

import numpy as np
import pandas as pd
from kagglehub import dataset_download


class DataLoader:
    _dataframes = None

    @staticmethod
    def load_data():
        """
        Carrega os dados do Kaggle e popula o singleton de DataFrames.
        """
        if DataLoader._dataframes is None:
            DataLoader._dataframes = {}
            print("Baixando os dados mais recentes do Kaggle...")
            base_path = dataset_download("rohanrao/formula-1-world-championship-1950-2020")
            print(f"Dados baixados no caminho: {base_path}")

            # Carregar os arquivos CSV
            DataLoader._dataframes["drivers"] = pd.read_csv(os.path.join(base_path, "drivers.csv"))
            DataLoader._dataframes["races"] = pd.read_csv(os.path.join(base_path, "races.csv"))
            DataLoader._dataframes["driver_standings"] = pd.read_csv(os.path.join(base_path, "driver_standings.csv"))
            DataLoader._dataframes["constructors"] = pd.read_csv(os.path.join(base_path, "constructors.csv"))
            DataLoader._dataframes["constructor_standings"] = pd.read_csv(os.path.join(base_path, "constructor_standings.csv"))
            DataLoader._dataframes["results"] = pd.read_csv(os.path.join(base_path, "results.csv"))
            print("Dados carregados com sucesso:", list(DataLoader._dataframes.keys()))

    @staticmethod
    def get_dataframes():
        """
        Retorna os DataFrames carregados.
        """
        if DataLoader._dataframes is None:
            raise ValueError("Os dados não foram carregados. Execute 'load_data()' primeiro.")
        return DataLoader._dataframes


def analyze_drivers():
    """
    Realiza uma análise detalhada dos pilotos com várias métricas.
    """
    print("\nAnálise de Pilotos")

    try:
        dataframes = DataLoader.get_dataframes()
        print("DataFrames disponíveis:", list(dataframes.keys()))  # Debug
    except ValueError as e:
        print(e)
        return

    drivers = dataframes.get("drivers")
    races = dataframes.get("races")
    results = dataframes.get("results")

    if drivers is None or results is None or races is None:
        print("Erro: Faltando um ou mais arquivos necessários para a análise.")
        return

    # Relacionar 'results' com 'races' para obter o ano
    results_with_year = results.merge(races[['raceId', 'year', 'name']], on='raceId')

    # Filtrar para os anos recentes (2022-2024)
    recent_years = results_with_year.query("2022 <= year <= 2024")

    # Converter os dados para NumPy arrays
    driver_ids = recent_years['driverId'].values
    race_ids = recent_years['raceId'].values
    points = recent_years['points'].values
    positions = recent_years['positionOrder'].values

    # Usar NumPy para métricas básicas
    unique_drivers = np.unique(driver_ids)

    metrics = {}
    for driver in unique_drivers:
        driver_points = points[driver_ids == driver]
        driver_positions = positions[driver_ids == driver]
        driver_race_ids = race_ids[driver_ids == driver]

        # Total de pontos
        total_points = np.sum(driver_points)

        # Número de vitórias
        total_wins = np.sum(driver_positions == 1)

        # Número de corridas disputadas
        total_races = len(driver_points)

        # Taxa de vitórias
        win_rate = (total_wins / total_races) * 100 if total_races > 0 else 0

        # Média de pontos por corrida
        avg_points_per_race = total_points / total_races if total_races > 0 else 0

        # Melhores posições
        best_positions = np.min(driver_positions)

        # Detalhamento de vitórias
        win_race_names = recent_years[(recent_years['driverId'] == driver) & (recent_years['positionOrder'] == 1)]['name'].tolist()

        metrics[driver] = {
            'Pontos Totais': total_points,
            'Vitórias Totais': total_wins,
            'Corridas Disputadas': total_races,
            'Taxa de Vitórias (%)': win_rate,
            'Média de Pontos por Corrida': avg_points_per_race,
            'Melhor Posição': best_positions,
            'Corridas Vencidas': win_race_names
        }

    # Ordenar os pilotos por pontos totais
    metrics_sorted = sorted(metrics.items(), key=lambda x: x[1]['Pontos Totais'], reverse=True)

    # Criar DataFrame para exibição
    rows = []
    for driver, data in metrics_sorted:
        driver_name = drivers.set_index('driverId').loc[driver, 'surname']
        rows.append({
            'Piloto': driver_name,
            **data
        })
    metrics_df = pd.DataFrame(rows)

    # Exibir DataFrame
    print("\nResumo Estatístico dos Pilotos (2022-2024):")
    print(metrics_df)

    # Gráfico: Total de Pontos por Piloto
    plt.figure(figsize=(12, 6))
    plt.bar(metrics_df["Piloto"], metrics_df["Pontos Totais"], color="blue", alpha=0.7)
    plt.title("Total de Pontos por Piloto (2022-2024)")
    plt.xlabel("Pilotos")
    plt.ylabel("Pontos")
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.show()

    # Gráfico: Taxa de Vitórias por Piloto
    plt.figure(figsize=(12, 6))
    plt.bar(metrics_df["Piloto"], metrics_df["Taxa de Vitórias (%)"], color="green", alpha=0.7)
    plt.title("Taxa de Vitórias por Piloto (2022-2024)")
    plt.xlabel("Pilotos")
    plt.ylabel("Taxa de Vitórias (%)")
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.show()

    # Gráfico: Média de Pontos por Corrida
    plt.figure(figsize=(12, 6))
    plt.bar(metrics_df["Piloto"], metrics_df["Média de Pontos por Corrida"], color="orange", alpha=0.7)
    plt.title("Média de Pontos por Corrida (2022-2024)")
    plt.xlabel("Pilotos")
    plt.ylabel("Média de Pontos")
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.show()

def analyze_teams():
    """
    Realiza análise de desempenho por equipe (2022-2024).
    """
    print("\nAnálise de Desempenho das Equipes (2022-2024)")

    try:
        dataframes = DataLoader.get_dataframes()
        print("DataFrames disponíveis:", list(dataframes.keys()))  # Debug
    except ValueError as e:
        print(e)
        return

    drivers = dataframes.get("drivers")
    races = dataframes.get("races")
    results = dataframes.get("results")
    constructors = dataframes.get("constructors")

    if drivers is None or results is None or races is None or constructors is None:
        print("Erro: Faltando um ou mais arquivos necessários para a análise.")
        return

    # Relacionar 'results' com 'races' e 'constructors' para obter o ano
    results_with_year = results.merge(races[['raceId', 'year']], on='raceId')
    results_with_year = results_with_year.merge(constructors[['constructorId', 'name']], on='constructorId')

    # Filtrar para os anos recentes (2022-2024)
    recent_years = results_with_year.query("2022 <= year <= 2024")

    # Converter os dados para NumPy arrays
    constructor_ids = recent_years['constructorId'].values
    points = recent_years['points'].values
    positions = recent_years['positionOrder'].values
    race_ids = recent_years['raceId'].values
    constructor_names = recent_years['name'].values

    # Usar NumPy para métricas básicas
    unique_constructors = np.unique(constructor_ids)

    team_metrics = {}
    for constructor in unique_constructors:
        team_points = points[constructor_ids == constructor]
        team_positions = positions[constructor_ids == constructor]
        team_race_ids = race_ids[constructor_ids == constructor]

        # Total de pontos
        total_points = np.sum(team_points)

        # Número de vitórias
        total_wins = np.sum(team_positions == 1)

        # Número de pódios
        total_podiums = np.sum((team_positions >= 1) & (team_positions <= 3))

        # Número de corridas disputadas
        total_races = len(np.unique(team_race_ids))

        # Média de pontos por corrida
        avg_points_per_race = total_points / total_races if total_races > 0 else 0

        # Melhor resultado
        best_result = np.min(team_positions)

        team_metrics[constructor] = {
            'Equipe': constructor_names[constructor_ids == constructor][0],
            'Pontos Totais': total_points,
            'Vitórias Totais': total_wins,
            'Pódios Totais': total_podiums,
            'Corridas Disputadas': total_races,
            'Média de Pontos por Corrida': avg_points_per_race,
            'Melhor Resultado': best_result
        }

    # Ordenar as equipes por pontos totais
    team_metrics_sorted = sorted(team_metrics.items(), key=lambda x: x[1]['Pontos Totais'], reverse=True)

    # Criar DataFrame para exibição
    rows = [data for _, data in team_metrics_sorted]
    team_metrics_df = pd.DataFrame(rows)

    # Exibir DataFrame
    print("\nResumo Estatístico das Equipes (2022-2024):")
    print(team_metrics_df)

    # Gráfico: Total de Pontos por Equipe
    plt.figure(figsize=(12, 6))
    plt.bar(team_metrics_df["Equipe"], team_metrics_df["Pontos Totais"], color="blue", alpha=0.7)
    plt.title("Total de Pontos por Equipe (2022-2024)")
    plt.xlabel("Equipes")
    plt.ylabel("Pontos")
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.show()

    # Gráfico: Total de Vitórias por Equipe
    plt.figure(figsize=(12, 6))
    plt.bar(team_metrics_df["Equipe"], team_metrics_df["Vitórias Totais"], color="green", alpha=0.7)
    plt.title("Total de Vitórias por Equipe (2022-2024)")
    plt.xlabel("Equipes")
    plt.ylabel("Vitórias")
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.show()

    # Gráfico: Média de Pontos por Corrida
    plt.figure(figsize=(12, 6))
    plt.bar(team_metrics_df["Equipe"], team_metrics_df["Média de Pontos por Corrida"], color="orange", alpha=0.7)
    plt.title("Média de Pontos por Corrida por Equipe (2022-2024)")
    plt.xlabel("Equipes")
    plt.ylabel("Média de Pontos")
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.show()

def enhanced_best_drivers_analysis():
        """
        Determina os melhores pilotos considerando o desempenho da equipe e dados de classificação.
        """
        print("\nAnálise Avançada dos Melhores Pilotos (2022-2024)")

        try:
            dataframes = DataLoader.get_dataframes()
            print("DataFrames disponíveis:", list(dataframes.keys()))  # Debug
        except ValueError as e:
            print(e)
            return

        drivers = dataframes.get("drivers")
        races = dataframes.get("races")
        results = dataframes.get("results")
        constructors = dataframes.get("constructors")

        if drivers is None or results is None or races is None or constructors is None:
            print("Erro: Faltando um ou mais arquivos necessários para a análise.")
            return

        # Relacionar 'results' com 'races' e 'constructors' para obter o ano
        results_with_year = results.merge(races[['raceId', 'year']], on='raceId')
        results_with_year = results_with_year.merge(constructors[['constructorId', 'name']], on='constructorId')

        # Filtrar para os anos recentes (2022-2024)
        recent_years = results_with_year.query("2022 <= year <= 2024")

        # Converter os dados para NumPy arrays
        driver_ids = recent_years['driverId'].values
        constructor_ids = recent_years['constructorId'].values
        points = recent_years['points'].values
        positions = recent_years['positionOrder'].values
        grid_positions = recent_years['grid'].values  # Dados de classificação

        # Métricas de Equipe
        unique_constructors = np.unique(constructor_ids)
        team_metrics = {}
        for constructor in unique_constructors:
            team_points = points[constructor_ids == constructor]
            team_positions = positions[constructor_ids == constructor]

            total_points = np.sum(team_points)
            total_wins = np.sum(team_positions == 1)
            total_races = len(np.unique(recent_years[constructor_ids == constructor]['raceId'].values))
            avg_points_per_race = total_points / total_races if total_races > 0 else 0

            team_metrics[constructor] = {
                'Competitividade': (total_points * 0.5 + total_wins * 30 + avg_points_per_race * 10)
            }

        # Métricas de Pilotos
        unique_drivers = np.unique(driver_ids)
        metrics = {}
        for driver in unique_drivers:
            driver_points = points[driver_ids == driver]
            driver_positions = positions[driver_ids == driver]
            driver_grid_positions = grid_positions[driver_ids == driver]
            driver_constructor = recent_years[recent_years['driverId'] == driver]['constructorId'].iloc[0]

            total_points = np.sum(driver_points)
            total_wins = np.sum(driver_positions == 1)
            total_races = len(driver_points)
            avg_points_per_race = total_points / total_races if total_races > 0 else 0
            win_rate = (total_wins / total_races) * 100 if total_races > 0 else 0
            avg_grid_position = np.mean(driver_grid_positions)
            avg_finish_position = np.mean(driver_positions)
            positions_gained = avg_grid_position - avg_finish_position

            # Ajuste pelo desempenho da equipe
            team_competitiveness = team_metrics[driver_constructor]['Competitividade']
            performance_score = (
                    (total_points * 0.5) +
                    (total_wins * 30) +
                    (avg_points_per_race * 10) +
                    (positions_gained * 5) +
                    (team_competitiveness * 0.2)
            )

            metrics[driver] = {
                'Pontos Totais': total_points,
                'Vitórias Totais': total_wins,
                'Corridas Disputadas': total_races,
                'Taxa de Vitórias (%)': win_rate,
                'Média de Pontos por Corrida': avg_points_per_race,
                'Posições Ganhas em Média': positions_gained,
                'Índice de Desempenho Ajustado': performance_score
            }

        # Ordenar os pilotos por índice de desempenho ajustado
        metrics_sorted = sorted(metrics.items(), key=lambda x: x[1]['Índice de Desempenho Ajustado'], reverse=True)

        # Criar DataFrame para exibição
        rows = []
        for driver, data in metrics_sorted:
            driver_name = drivers.set_index('driverId').loc[driver, 'surname']
            rows.append({
                'Piloto': driver_name,
                **data
            })
        metrics_df = pd.DataFrame(rows)

        # Exibir DataFrame
        print("\nMelhores Pilotos Ajustados (2022-2024):")
        print(metrics_df)

        # Gráfico: Índice de Desempenho Ajustado
        plt.figure(figsize=(12, 6))
        plt.bar(metrics_df["Piloto"], metrics_df["Índice de Desempenho Ajustado"], color="purple", alpha=0.7)
        plt.title("Melhores Pilotos Ajustados por Índice de Desempenho (2022-2024)")
        plt.xlabel("Pilotos")
        plt.ylabel("Índice de Desempenho Ajustado")
        plt.xticks(rotation=45)
        plt.grid(axis='y')
        plt.show()

import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt


class F1AnalysisApp:
    def __init__(self, root):
        """
        Inicializa a interface gráfica principal.
        """
        self.root = root
        self.root.title("F1 Analysis Dashboard")
        self.root.geometry("400x300")

        # Título da aplicação
        title = tk.Label(root, text="F1 Analysis Dashboard", font=("Arial", 16))
        title.pack(pady=20)

        # Botões para análises
        btn_drivers = tk.Button(root, text="Análise de Pilotos", command=self.analyze_drivers)
        btn_drivers.pack(pady=5)

        btn_teams = tk.Button(root, text="Análise de Equipes", command=self.analyze_teams)
        btn_teams.pack(pady=5)

        btn_advanced = tk.Button(root, text="Análise Avançada de Pilotos", command=self.enhanced_analysis)
        btn_advanced.pack(pady=5)

        btn_exit = tk.Button(root, text="Sair", command=self.root.quit)
        btn_exit.pack(pady=20)

    def analyze_drivers(self):
        """
        Chama a análise de pilotos e exibe os resultados.
        """
        try:
            analyze_drivers()  # Função já definida no código original
            messagebox.showinfo("Sucesso", "Análise de Pilotos concluída!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar a análise de pilotos:\n{e}")

    def analyze_teams(self):
        """
        Chama a análise de equipes e exibe os resultados.
        """
        try:
            analyze_teams()  # Função já definida no código original
            messagebox.showinfo("Sucesso", "Análise de Equipes concluída!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar a análise de equipes:\n{e}")

    def enhanced_analysis(self):
        """
        Chama a análise avançada de pilotos e exibe os resultados.
        """
        try:
            enhanced_best_drivers_analysis()  # Função já definida no código original
            messagebox.showinfo("Sucesso", "Análise Avançada concluída!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar a análise avançada:\n{e}")


if __name__ == "__main__":
    # Carregar os dados primeiro
    print("Carregando dados...")
    DataLoader.load_data()

    # Inicializar a aplicação Tkinter
    root = tk.Tk()
    app = F1AnalysisApp(root)
    root.mainloop()
