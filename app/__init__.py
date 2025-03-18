from flask import Flask
from flask_cors import CORS
from config.config import Config

def create_app(config_class=Config):
    """
    Função fábrica da aplicação
    """
    # Cria a aplicação Flask
    app = Flask(__name__)
    
    # Configura a aplicação
    app.config.from_object(config_class)
    
    # Habilita CORS
    CORS(app)
    
    # Registra blueprints
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    
    # Adiciona uma rota simples de verificação de saúde
    @app.route('/health')
    def health_check():
        return {'status': 'ok'}, 200
    
    return app