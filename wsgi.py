import sys
import os

# Adiciona o caminho do projeto ao path do Python
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from app import create_app
from config.config import app_config

# Cria a aplicação Flask
application = create_app(app_config)

# Para debug - adicione logs aqui se precisar

if __name__ == '__main__':
    application.run()