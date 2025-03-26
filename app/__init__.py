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
    
    # Configura CORS para toda a aplicação
    CORS(app, 
         resources={r"/api/*": {"origins": ["http://localhost:3000"]}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Registra blueprints (sem prefixo adicional, pois já está definido no blueprint)
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    
    # Rota de verificação de saúde também com prefixo /api
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok'}, 200
    
    return app