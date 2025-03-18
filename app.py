from app import create_app
from config.config import app_config

# Cria a aplicação Flask
app = create_app(app_config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)