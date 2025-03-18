from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from app.models.user_model import User
from app.utils.auth import validate_cpf, validate_birth_date
from config.config import Config

class UserService:
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> Tuple[User, Optional[str]]:
        """
        Cria um novo usuário no banco de dados
        Retorna o usuário criado ou uma mensagem de erro
        """
        # Valida campos obrigatórios
        required_fields = ['email', 'full_name', 'cpf', 'birth_date']
        for field in required_fields:
            if field not in user_data:
                return None, f"Campo obrigatório ausente: {field}"
        
        # Valida o formato do CPF
        if not validate_cpf(user_data['cpf']):
            return None, "Formato de CPF inválido"
        
        # Valida o formato da data de nascimento
        if not validate_birth_date(user_data['birth_date']):
            return None, "Formato de data de nascimento inválido. Use AAAA-MM-DD"
        
        # Adiciona valores padrão se não fornecidos
        user_data['status'] = user_data.get('status', 'active')
        user_data['role'] = user_data.get('role', 'user')
        
        # Cria objeto de usuário
        user = User.from_dict(user_data)
        
        try:
            # Conecta ao Supabase
            supabase = Config.get_supabase_client()
            
            # Insere usuário no banco de dados
            response = supabase.table('users').insert({
                'email': user.email,
                'full_name': user.full_name,
                'cpf': user.cpf,
                'birth_date': user.birth_date,
                'status': user.status,
                'role': user.role
            }).execute()
            
            # Verifica erros
            if 'error' in response:
                return None, response['error']['message']
            
            # Obtém o usuário criado
            created_user = User.from_dict(response.data[0])
            return created_user, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def authenticate_user(cpf: str, birth_date: str) -> Tuple[User, Optional[str]]:
        """
        Autentica um usuário com CPF e data de nascimento
        Retorna o usuário autenticado ou uma mensagem de erro
        """
        # Valida o formato do CPF
        if not validate_cpf(cpf):
            return None, "Formato de CPF inválido"
        
        # Valida o formato da data de nascimento
        if not validate_birth_date(birth_date):
            return None, "Formato de data de nascimento inválido. Use AAAA-MM-DD"
        
        try:
            # Conecta ao Supabase
            supabase = Config.get_supabase_client()
            
            # Consulta o banco de dados
            response = supabase.table('users').select('*').eq('cpf', cpf).eq('birth_date', birth_date).execute()
            
            # Verifica se o usuário existe
            if not response.data:
                return None, "Credenciais inválidas"
            
            user_data = response.data[0]
            
            # Atualiza hora do último login
            supabase.table('users').update({'last_login': datetime.now().isoformat()}).eq('id', user_data['id']).execute()
            
            # Retorna usuário
            return User.from_dict(user_data), None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Tuple[User, Optional[str]]:
        """
        Obtém um usuário pelo ID
        Retorna o usuário ou uma mensagem de erro
        """
        try:
            # Conecta ao Supabase
            supabase = Config.get_supabase_client()
            
            # Consulta o banco de dados
            response = supabase.table('users').select('*').eq('id', user_id).execute()
            
            # Verifica se o usuário existe
            if not response.data:
                return None, "Usuário não encontrado"
            
            # Retorna usuário
            return User.from_dict(response.data[0]), None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_all_users() -> Tuple[List[User], Optional[str]]:
        """
        Obtém todos os usuários
        Retorna uma lista de usuários ou uma mensagem de erro
        """
        try:
            # Conecta ao Supabase
            supabase = Config.get_supabase_client()
            
            # Consulta o banco de dados
            response = supabase.table('users').select('*').execute()
            
            # Converte para lista de objetos User
            users = [User.from_dict(user_data) for user_data in response.data]
            
            # Retorna usuários
            return users, None
            
        except Exception as e:
            return [], str(e)
    
    @staticmethod
    def update_user(user_id: int, user_data: Dict[str, Any]) -> Tuple[User, Optional[str]]:
        """
        Atualiza um usuário
        Retorna o usuário atualizado ou uma mensagem de erro
        """
        try:
            # Conecta ao Supabase
            supabase = Config.get_supabase_client()
            
            # Adiciona timestamp de atualização
            user_data['updated_at'] = datetime.now().isoformat()
            
            # Atualiza usuário no banco de dados
            response = supabase.table('users').update(user_data).eq('id', user_id).execute()
            
            # Verifica se o usuário existe
            if not response.data:
                return None, "Usuário não encontrado"
            
            # Retorna usuário atualizado
            return User.from_dict(response.data[0]), None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def delete_user(user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Exclui um usuário
        Retorna status de sucesso e mensagem de erro opcional
        """
        try:
            # Conecta ao Supabase
            supabase = Config.get_supabase_client()
            
            # Exclui usuário do banco de dados
            response = supabase.table('users').delete().eq('id', user_id).execute()
            
            # Verifica se o usuário foi excluído
            if not response.data:
                return False, "Usuário não encontrado"
            
            # Retorna sucesso
            return True, None
            
        except Exception as e:
            return False, str(e)