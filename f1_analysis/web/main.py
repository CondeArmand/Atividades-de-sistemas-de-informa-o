import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import numpy as np
import pandas as pd
from f1_analysis.main import DataLoader
from dash import dash_table
import dash_bootstrap_components as dbc

# Carregar dados primeiro
print("Carregando dados...")
DataLoader.load_data()

# Inicializar o aplicativo Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "F1 Analysis Dashboard"

# Layout com Bootstrap
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("F1 Analysis Dashboard", className="text-center"), width=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dbc.Button("Análise de Pilotos", id="btn-drivers", color="primary", className="me-2"), width="auto"),
        dbc.Col(dbc.Button("Análise de Equipes", id="btn-teams", color="secondary", className="me-2"), width="auto"),
        dbc.Col(dbc.Button("Análise Avançada", id="btn-advanced", color="success"), width="auto")
    ], className="mb-4 justify-content-center"),

    dbc.Row([
        dbc.Col(html.Div(id="output-area"), width=12)
    ])
], fluid=True)

# Callback para atualizar o conteúdo com base no botão clicado
@app.callback(
    Output("output-area", "children"),
    [Input("btn-drivers", "n_clicks"),
     Input("btn-teams", "n_clicks"),
     Input("btn-advanced", "n_clicks")]
)
def update_output(btn_drivers, btn_teams, btn_advanced):
    ctx = dash.callback_context

    # Se nenhum botão foi clicado, mostrar mensagem inicial
    if not ctx.triggered:
        return html.Div("Selecione uma análise acima.", style={"textAlign": "center"})

    # Identificar qual botão foi clicado
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "btn-drivers":
        return analyze_drivers_dash()

    if button_id == "btn-teams":
        return analyze_teams_dash()

    if button_id == "btn-advanced":
        return enhanced_analysis_dash()


def analyze_drivers_dash():
    """
    Análise de pilotos com métricas adicionais para exibição no Dash.
    """
    try:
        dataframes = DataLoader.get_dataframes()
        drivers = dataframes.get("drivers")
        races = dataframes.get("races")
        results = dataframes.get("results")

        # Relacionar os resultados com as corridas para obter o ano
        results_with_year = results.merge(races[['raceId', 'year']], on='raceId')
        recent_years = results_with_year.query("2022 <= year <= 2024")

        # Dados
        driver_ids = recent_years['driverId'].values
        points = recent_years['points'].values
        positions = recent_years['positionOrder'].values

        unique_drivers = np.unique(driver_ids)
        metrics = {}
        for driver in unique_drivers:
            driver_points = points[driver_ids == driver]
            driver_positions = positions[driver_ids == driver]

            total_points = np.sum(driver_points)
            total_wins = np.sum(driver_positions == 1)
            total_races = len(driver_positions)
            avg_position = np.mean(driver_positions)
            win_rate = (total_wins / total_races) * 100 if total_races > 0 else 0
            top_5_rate = (np.sum(driver_positions <= 5) / total_races) * 100 if total_races > 0 else 0

            metrics[driver] = {
                'Pontos Totais': total_points,
                'Vitórias Totais': total_wins,
                'Corridas Disputadas': total_races,
                'Média de Posição Final': round(avg_position, 2),
                'Vitórias (%)': round(win_rate, 2),
                'Top 5 (%)': round(top_5_rate, 2)
            }

        # Ordenar por pontos totais
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

        # Gráfico interativo
        fig = px.bar(
            metrics_df,
            x="Piloto",
            y="Pontos Totais",
            title="Total de Pontos por Piloto (2022-2024)",
            labels={"Pontos Totais": "Pontos", "Piloto": "Pilotos"}
        )

        # Retornar gráfico e tabela
        from dash import dash_table
        return html.Div([
            dcc.Graph(figure=fig),
            dash_table.DataTable(
                data=metrics_df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in metrics_df.columns],
                style_table={'overflowX': 'auto', 'marginTop': '20px'}
            )
        ])

    except Exception as e:
        return html.Div(f"Erro: {e}", style={"color": "red"})



def analyze_teams_dash():
    """
    Análise de equipes com métricas adicionais para exibição no Dash.
    """
    try:
        dataframes = DataLoader.get_dataframes()
        constructors = dataframes.get("constructors")
        races = dataframes.get("races")
        results = dataframes.get("results")

        # Relacionar os resultados com as corridas e as equipes
        results_with_year = results.merge(races[['raceId', 'year']], on='raceId')
        recent_years = results_with_year.query("2022 <= year <= 2024")

        # Dados
        constructor_ids = recent_years['constructorId'].values
        points = recent_years['points'].values
        positions = recent_years['positionOrder'].values

        unique_constructors = np.unique(constructor_ids)
        metrics = {}
        for constructor in unique_constructors:
            constructor_points = points[constructor_ids == constructor]
            constructor_positions = positions[constructor_ids == constructor]

            total_points = np.sum(constructor_points)
            total_wins = np.sum(constructor_positions == 1)
            total_races = len(np.unique(recent_years[constructor_ids == constructor]['raceId']))
            avg_points_per_race = total_points / total_races if total_races > 0 else 0
            win_rate = (total_wins / total_races) * 100 if total_races > 0 else 0

            metrics[constructor] = {
                'Pontos Totais': total_points,
                'Vitórias Totais': total_wins,
                'Corridas Disputadas': total_races,
                'Média de Pontos por Corrida': round(avg_points_per_race, 2),
                'Vitórias (%)': round(win_rate, 2)
            }

        # Ordenar por pontos totais
        metrics_sorted = sorted(metrics.items(), key=lambda x: x[1]['Pontos Totais'], reverse=True)

        # Criar DataFrame para exibição
        rows = []
        for constructor, data in metrics_sorted:
            constructor_name = constructors.set_index('constructorId').loc[constructor, 'name']
            rows.append({
                'Equipe': constructor_name,
                **data
            })
        metrics_df = pd.DataFrame(rows)

        # Gráfico interativo
        fig = px.bar(
            metrics_df,
            x="Equipe",
            y="Pontos Totais",
            title="Total de Pontos por Equipe (2022-2024)",
            labels={"Pontos Totais": "Pontos", "Equipe": "Equipes"}
        )

        # Retornar gráfico e tabela
        return html.Div([
            dcc.Graph(figure=fig),
            dash_table.DataTable(
                data=metrics_df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in metrics_df.columns],
                style_table={'overflowX': 'auto', 'marginTop': '20px'}
            )
        ])

    except Exception as e:
        return html.Div(f"Erro: {e}", style={"color": "red"})



def enhanced_analysis_dash():
    """
    Análise avançada de pilotos com métricas adicionais para exibição no Dash.
    """
    try:
        dataframes = DataLoader.get_dataframes()
        drivers = dataframes.get("drivers")
        races = dataframes.get("races")
        results = dataframes.get("results")
        constructors = dataframes.get("constructors")

        # Relacionar os resultados com as corridas e as equipes
        results_with_year = results.merge(races[['raceId', 'year']], on='raceId')
        results_with_year = results_with_year.merge(constructors[['constructorId', 'name']], on='constructorId')
        recent_years = results_with_year.query("2022 <= year <= 2024")

        # Dados
        driver_ids = recent_years['driverId'].values
        constructor_ids = recent_years['constructorId'].values
        points = recent_years['points'].values
        positions = recent_years['positionOrder'].values
        grid_positions = recent_years['grid'].values  # Classificação na largada

        unique_drivers = np.unique(driver_ids)
        metrics = {}
        team_metrics = {}

        # Cálculo de competitividade da equipe
        unique_constructors = np.unique(constructor_ids)
        for constructor in unique_constructors:
            team_points = np.sum(points[constructor_ids == constructor])
            team_wins = np.sum(positions[(constructor_ids == constructor)] == 1)
            team_metrics[constructor] = {
                'Total de Pontos': team_points,
                'Total de Vitórias': team_wins
            }

        # Cálculo das métricas para cada piloto
        for driver in unique_drivers:
            driver_points = points[driver_ids == driver]
            driver_positions = positions[driver_ids == driver]
            driver_grid_positions = grid_positions[driver_ids == driver]
            driver_constructor = constructor_ids[driver_ids == driver][0]

            total_points = np.sum(driver_points)
            total_wins = np.sum(driver_positions == 1)
            total_podiums = np.sum(driver_positions <= 3)
            total_races = len(driver_positions)
            avg_grid_position = np.mean(driver_grid_positions)
            avg_finish_position = np.mean(driver_positions)
            positions_gained = avg_grid_position - avg_finish_position

            # Representatividade na equipe
            team_total_points = team_metrics[driver_constructor]['Total de Pontos']
            team_total_wins = team_metrics[driver_constructor]['Total de Vitórias']
            points_contribution = (total_points / team_total_points) * 100 if team_total_points > 0 else 0
            wins_contribution = (total_wins / team_total_wins) * 100 if team_total_wins > 0 else 0

            # Pontuação ajustada pela competitividade da equipe
            performance_score = (
                total_points * 0.6 +
                total_wins * 30 +
                total_podiums * 10 +
                positions_gained * 5 +
                points_contribution * 0.2
            )

            metrics[driver] = {
                'Piloto': drivers.set_index('driverId').loc[driver, 'surname'],
                'Pontos Totais': total_points,
                'Vitórias Totais': total_wins,
                'Pódios Totais': total_podiums,
                'Corridas Disputadas': total_races,
                'Classificação Média (Grid)': round(avg_grid_position, 2),
                'Posições Ganhas em Média': round(positions_gained, 2),
                '% de Pontos pela Equipe': round(points_contribution, 2),
                '% de Vitórias pela Equipe': round(wins_contribution, 2),
                'Pontuação Ajustada': round(performance_score, 2)
            }

        # Ordenar por pontuação ajustada
        metrics_sorted = sorted(metrics.values(), key=lambda x: x['Pontuação Ajustada'], reverse=True)

        # Criar DataFrame para exibição
        metrics_df = pd.DataFrame(metrics_sorted)

        # Gráfico interativo
        fig = px.bar(
            metrics_df,
            x="Piloto",
            y="Pontuação Ajustada",
            title="Pontuação Ajustada dos Pilotos (2022-2024)",
            labels={"Pontuação Ajustada": "Pontuação", "Piloto": "Pilotos"}
        )

        # Retornar gráfico e tabela
        from dash import dash_table
        return html.Div([
            dcc.Graph(figure=fig),
            dash_table.DataTable(
                data=metrics_df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in metrics_df.columns],
                style_table={'overflowX': 'auto', 'marginTop': '20px'}
            )
        ])

    except Exception as e:
        return html.Div(f"Erro: {e}", style={"color": "red"})




# Executar o servidor
if __name__ == "__main__":
    app.run_server(debug=True)
