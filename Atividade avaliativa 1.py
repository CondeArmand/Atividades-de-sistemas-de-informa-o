import numpy as np

matriz_A = np.random.choice([True, False], size=(3, 3))
matriz_B = np.random.choice([True, False], size=(3, 3))

# Operações lógicas
and_result = np.logical_and(matriz_A, matriz_B)
or_result = np.logical_or(matriz_A, matriz_B)
not_result_a = np.logical_not(matriz_A)
not_result_b = np.logical_not(matriz_B)

# Resultados
results = {
    "Matriz A": matriz_A,
    "Matriz B": matriz_B,
    "AND Result": and_result,
    "OR Result": or_result,
    "NOT A Result": not_result_a,
    "NOT B Result": not_result_b
}

# Formatando a exibição dos resultados
for key, value in results.items():
    print(f"{key}:\n{value}\n{'-' * 30}")


