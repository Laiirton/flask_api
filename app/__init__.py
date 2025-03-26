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
    
    # Configura CORS especificamente para rotas /api
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": app.config['CORS_METHODS'],
            "allow_headers": app.config['CORS_HEADERS']
        }
    })
    
    # Registra blueprints (sem prefixo adicional, pois já está definido no blueprint)
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    
    # Rota de verificação de saúde também com prefixo /api
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok'}, 200
    
    return app