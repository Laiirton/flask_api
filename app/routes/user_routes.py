from flask import Blueprint, request, jsonify, current_app
from app.services.user_service import UserService
from app.utils.auth import generate_token

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
    Login de usuário com username e data de nascimento
    """
    data = request.get_json()
    
    # Verifica campos obrigatórios
    if 'username' not in data or 'birth_date' not in data:
        return jsonify({'error': 'Username e data de nascimento são obrigatórios'}), 400
    
    # Autentica usuário
    user, error = UserService.authenticate_user(data['username'], data['birth_date'])
    
    if error:
        return jsonify({'error': error}), 401
    
    # Gera token
    secret_key = current_app.config['SECRET_KEY']
    user_dict = user.to_dict()
    token = generate_token(user_dict, secret_key)
    
    # Retorna token e dados do usuário
    return jsonify({
        'message': 'Login realizado com sucesso',
        'token': token,
        'user': user.to_response_dict()
    }), 200

@user_bp.route('/', methods=['GET'])
def get_all_users():
    """
    Obter todos os usuários
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
def get_user(user_id):
    """
    Obter um usuário pelo ID
    """
    user, error = UserService.get_user_by_id(user_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    # Retorna dados do usuário
    return jsonify({
        'message': 'Usuário recuperado com sucesso',
        'user': user.to_response_dict()
    }), 200

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Atualizar um usuário
    """
    data = request.get_json()
    user, error = UserService.update_user(user_id, data)
    
    if error:
        return jsonify({'error': error}), 400
    
    # Retorna dados atualizados do usuário
    return jsonify({
        'message': 'Usuário atualizado com sucesso',
        'user': user.to_response_dict()
    }), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Excluir um usuário
    """
    success, error = UserService.delete_user(user_id)
    
    if error:
        return jsonify({'error': error}), 400
    
    # Retorna mensagem de sucesso
    return jsonify({
        'message': 'Usuário excluído com sucesso'
    }), 200

@user_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Obter o usuário pelo ID fornecido
    """
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({'error': 'ID do usuário é obrigatório'}), 400
        
    user, error = UserService.get_user_by_id(user_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    # Retorna dados do usuário
    return jsonify({
        'message': 'Usuário recuperado com sucesso',
        'user': user.to_response_dict()
    }), 200