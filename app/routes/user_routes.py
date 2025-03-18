from flask import Blueprint, request, jsonify, current_app
from app.services.user_service import UserService
from app.utils.auth import generate_token, token_required, admin_required
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# Cria blueprint
user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/register', methods=['POST'])
def register():
    """
    Registra um novo usuário
    """
    data = request.get_json()
    
    # Cria usuário
    user, error = UserService.create_user(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    # Retorna dados do usuário
    return jsonify({
        'message': 'Usuário registrado com sucesso',
        'user': user.to_response_dict()
    }), 201

@user_bp.route('/login', methods=['POST'])
def login():
    """
    Login de usuário com CPF e data de nascimento
    """
    data = request.get_json()
    
    # Verifica campos obrigatórios
    if 'cpf' not in data or 'birth_date' not in data:
        return jsonify({'error': 'CPF e data de nascimento são obrigatórios'}), 400
    
    # Autentica usuário
    user, error = UserService.authenticate_user(data['cpf'], data['birth_date'])
    
    if error:
        return jsonify({'error': error}), 401
    
    # Gera token
    secret_key = current_app.config['SECRET_KEY']
    logger.info(f"Gerando token com chave: {secret_key[:5]}...")
    
    user_dict = user.to_dict()
    logger.info(f"Dados do usuário para token: ID={user_dict['id']}, Role={user_dict['role']}")
    
    token = generate_token(user_dict, secret_key)
    logger.info(f"Token gerado: {token[:15]}...")
    
    # Retorna token e dados do usuário
    return jsonify({
        'message': 'Login realizado com sucesso',
        'token': token,
        'user': user.to_response_dict()
    }), 200

@user_bp.route('/', methods=['GET'])
@admin_required
def get_all_users():
    """
    Obter todos os usuários (apenas administrador)
    """
    users, error = UserService.get_all_users()
    
    if error:
        return jsonify({'error': error}), 500
    
    # Retorna dados dos usuários
    return jsonify({
        'message': 'Usuários recuperados com sucesso',
        'users': [user.to_response_dict() for user in users]
    }), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """
    Obter um usuário pelo ID
    """
    # Verifica se o usuário tem permissão para acessar este recurso
    if request.user_role != 'admin' and request.user_id != user_id:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    user, error = UserService.get_user_by_id(user_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    # Retorna dados do usuário
    return jsonify({
        'message': 'Usuário recuperado com sucesso',
        'user': user.to_response_dict()
    }), 200

@user_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """
    Atualizar um usuário
    """
    # Verifica se o usuário tem permissão para acessar este recurso
    if request.user_role != 'admin' and request.user_id != user_id:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    data = request.get_json()
    
    # Impede escalação de função por não-administradores
    if 'role' in data and request.user_role != 'admin':
        del data['role']
    
    user, error = UserService.update_user(user_id, data)
    
    if error:
        return jsonify({'error': error}), 400
    
    # Retorna dados atualizados do usuário
    return jsonify({
        'message': 'Usuário atualizado com sucesso',
        'user': user.to_response_dict()
    }), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Excluir um usuário (apenas administrador)
    """
    success, error = UserService.delete_user(user_id)
    
    if error:
        return jsonify({'error': error}), 400
    
    # Retorna mensagem de sucesso
    return jsonify({
        'message': 'Usuário excluído com sucesso'
    }), 200

@user_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Obter o usuário atualmente logado
    """
    logger.info(f"Acessando rota /me com user_id={request.user_id}")
    
    user, error = UserService.get_user_by_id(request.user_id)
    
    if error:
        logger.error(f"Erro ao buscar usuário: {error}")
        return jsonify({'error': error}), 404
    
    logger.info(f"Usuário encontrado: {user.id}")
    
    # Retorna dados do usuário
    return jsonify({
        'message': 'Usuário recuperado com sucesso',
        'user': user.to_response_dict()
    }), 200