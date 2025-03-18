import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configuração base"""
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-secret-key')
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    @staticmethod
    def get_supabase_client() -> Client:
        """Retorna uma instância do cliente Supabase"""
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("URL e chave do Supabase devem ser definidos nas variáveis de ambiente")
        
        return create_client(supabase_url, supabase_key)

class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    ENV = 'production'

class TestingConfig(Config):
    """Configuração de testes"""
    TESTING = True
    DEBUG = True

# Dicionário de configuração
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# Padrão para configuração de desenvolvimento
app_config = config_by_name.get(os.environ.get('FLASK_ENV', 'development'))