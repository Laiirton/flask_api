from datetime import datetime, timedelta, UTC
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from typing import Callable, Dict, Any, Optional

def generate_token(user_data: Dict[str, Any], secret_key: str, expiry_hours: int = 1) -> str:
    """
    Gera um token JWT para o usuário
    """
    payload = {
        'exp': datetime.now(UTC) + timedelta(hours=expiry_hours),
        'iat': datetime.now(UTC),
        'sub': user_data['id'],
        'cpf': user_data['cpf'],
        'role': user_data['role']
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def decode_token(token: str, secret_key: str) -> Dict[str, Any]:
    """
    Decodifica um token JWT
    """
    try:
        return jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise Exception('Token expirado. Por favor, faça login novamente.')
    except jwt.InvalidTokenError:
        raise Exception('Token inválido. Por favor, faça login novamente.')

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
        
        if not token:
            return jsonify({'message': 'Token não fornecido!'}), 401
        
        try:
            # Decodifica o token
            secret_key = current_app.config['SECRET_KEY']
            payload = decode_token(token, secret_key)
            request.user_id = payload['sub']
            request.user_role = payload['role']
        except Exception as e:
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
        
        if not token:
            return jsonify({'message': 'Token não fornecido!'}), 401
        
        try:
            secret_key = current_app.config['SECRET_KEY']
            payload = decode_token(token, secret_key)
            if payload['role'] != 'admin':
                return jsonify({'message': 'Privilégios de administrador necessários!'}), 403
            
            request.user_id = payload['sub']
            request.user_role = payload['role']
        except Exception as e:
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