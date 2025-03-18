from datetime import datetime, timedelta, UTC
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from typing import Callable, Dict, Any, Optional
import logging

# Configuração de logging para depuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_token(user_data: Dict[str, Any], secret_key: str, expiry_hours: int = 1) -> str:
    """
    Gera um token JWT para o usuário
    """
    payload = {
        'exp': datetime.now(UTC) + timedelta(hours=expiry_hours),
        'iat': datetime.now(UTC),
        'sub': str(user_data['id']),  # Convertendo ID para string para evitar erros de validação
        'cpf': user_data['cpf'],
        'role': user_data['role']
    }
    logger.info(f"Gerando token com payload: {payload}")
    return jwt.encode(payload, secret_key, algorithm='HS256')

def decode_token(token: str, secret_key: str) -> Dict[str, Any]:
    """
    Decodifica um token JWT
    """
    try:
        # Adicionar log para depuração
        logger.info(f"Decodificando token: {token[:10]}...")
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        logger.info(f"Token decodificado com sucesso: {decoded}")
        return decoded
    except jwt.ExpiredSignatureError:
        logger.error("Token expirado")
        raise Exception('Token expirado. Por favor, faça login novamente.')
    except jwt.InvalidTokenError as e:
        logger.error(f"Token inválido: {str(e)}")
        raise Exception('Token inválido. Por favor, faça login novamente.')
    except Exception as e:
        logger.error(f"Erro ao decodificar token: {str(e)}")
        raise Exception(f'Erro ao processar token: {str(e)}')

def token_required(f: Callable) -> Callable:
    """
    Decorador para exigir autenticação de token
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verifica se o token está no cabeçalho
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            if (auth_header.startswith('Bearer ')):
                token = auth_header.split(' ')[1]
                logger.info(f"Token extraído do cabeçalho: {token[:10]}...")
        
        if not token:
            logger.warning("Token não fornecido no cabeçalho")
            return jsonify({'message': 'Token não fornecido!'}), 401
        
        try:
            # Decodifica o token
            secret_key = current_app.config['SECRET_KEY']
            logger.info(f"Usando SECRET_KEY: {secret_key[:5]}...")
            payload = decode_token(token, secret_key)
            request.user_id = payload['sub']
            request.user_role = payload['role']
            logger.info(f"Token validado para usuário ID: {request.user_id}, função: {request.user_role}")
        except Exception as e:
            logger.error(f"Erro na validação do token: {str(e)}")
            return jsonify({'message': str(e)}), 401
            
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f: Callable) -> Callable:
    """
    Decorador para exigir função de administrador
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            logger.info(f"Token extraído do cabeçalho: {token[:10]}...")
        
        if not token:
            logger.warning("Token não fornecido no cabeçalho para acesso administrativo")
            return jsonify({'message': 'Token não fornecido!'}), 401
        
        try:
            secret_key = current_app.config['SECRET_KEY']
            logger.info(f"Usando SECRET_KEY para admin: {secret_key[:5]}...")
            payload = decode_token(token, secret_key)
            if payload['role'] != 'admin':
                logger.warning(f"Tentativa de acesso admin por usuário não-admin: {payload['sub']}")
                return jsonify({'message': 'Privilégios de administrador necessários!'}), 403
            
            request.user_id = payload['sub']
            request.user_role = payload['role']
            logger.info(f"Token admin validado para usuário ID: {request.user_id}")
        except Exception as e:
            logger.error(f"Erro na validação do token admin: {str(e)}")
            return jsonify({'message': str(e)}), 401
            
        return f(*args, **kwargs)
    
    return decorated

def validate_cpf(cpf: str) -> bool:
    """
    Valida o formato do CPF
    """
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se o CPF tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Valida o CPF usando o algoritmo de verificação
    for i in range(9, 11):
        value = sum((int(cpf[j]) * ((i + 1) - j) for j in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if int(cpf[i]) != digit:
            return False
    
    return True

def validate_birth_date(birth_date: str) -> bool:
    """
    Valida o formato da data de nascimento (AAAA-MM-DD)
    """
    try:
        datetime.strptime(birth_date, '%Y-%m-%d')
        return True
    except ValueError:
        return False