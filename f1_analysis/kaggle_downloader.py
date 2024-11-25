import kagglehub
import os

def download_kaggle_data(dataset_name="rohanrao/formula-1-world-championship-1950-2020", local_path="./data"):
    """
    Baixa os dados mais recentes do Kaggle e salva na pasta especificada.
    """
    print("Baixando os dados mais recentes do Kaggle...")
    path = kagglehub.dataset_download(dataset_name)
    print(f"Dados baixados em: {path}")

    # Mover os dados para o diretório local (opcional, se necessário organizar)
    if local_path != path:
        os.makedirs(local_path, exist_ok=True)
        print(f"Certifique-se de carregar os arquivos do diretório: {path}")
    return path
