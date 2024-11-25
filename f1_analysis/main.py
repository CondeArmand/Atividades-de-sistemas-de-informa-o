import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
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

def best_drivers_analysis():
    """
    Determina os melhores pilotos entre 2022 e 2024 com base em métricas de desempenho.
    """
    print("\nAnálise dos Melhores Pilotos (2022-2024)")

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
    results_with_year = results.merge(races[['raceId', 'year']], on='raceId')

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

        # Melhor posição alcançada
        best_position = np.min(driver_positions)

        # Índice de desempenho ponderado
        performance_score = (
            (total_points * 0.5) +  # Peso maior para pontos totais
            (total_wins * 30) +    # Vitórias impactam significativamente
            (avg_points_per_race * 10) +  # Consistência é valorizada
            ((1 / best_position) * 100)  # Melhores posições têm peso menor
        )

        metrics[driver] = {
            'Pontos Totais': total_points,
            'Vitórias Totais': total_wins,
            'Corridas Disputadas': total_races,
            'Taxa de Vitórias (%)': win_rate,
            'Média de Pontos por Corrida': avg_points_per_race,
            'Melhor Posição': best_position,
            'Índice de Desempenho': performance_score
        }

    # Ordenar os pilotos por índice de desempenho
    metrics_sorted = sorted(metrics.items(), key=lambda x: x[1]['Índice de Desempenho'], reverse=True)

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
    print("\nMelhores Pilotos (2022-2024):")
    print(metrics_df)

    # Gráfico: Índice de Desempenho
    plt.figure(figsize=(12, 6))
    plt.bar(metrics_df["Piloto"], metrics_df["Índice de Desempenho"], color="purple", alpha=0.7)
    plt.title("Melhores Pilotos por Índice de Desempenho (2022-2024)")
    plt.xlabel("Pilotos")
    plt.ylabel("Índice de Desempenho")
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


def main_menu():
    """
    Menu principal para selecionar as análises.
    """
    print("\nF1 Analysis Menu")
    print("1. Análise de Pilotos")
    print("2. Análise de Melhores Pilotos")
    print("3. Análise de Equipes")
    print("4. Análise Avançada de Melhores Pilotos")
    print("0. Sair")

    while True:
        choice = input("\nEscolha uma opção: ")
        if choice == "1":
            analyze_drivers()
        elif choice == "2":
            best_drivers_analysis()
        elif choice == "3":
            analyze_teams()
        elif choice == "4":
            enhanced_best_drivers_analysis()
        elif choice == "0":
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    print("Iniciando o carregamento dos dados...")
    DataLoader.load_data()  # Carregar os dados
    print("Dados carregados com sucesso.")
    main_menu()