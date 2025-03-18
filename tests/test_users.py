import json
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Adiciona o diretório pai ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config.config import config_by_name
from app.models.user_model import User

class TestUserAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_by_name['testing'])
        self.client = self.app.test_client()
        self.headers = {'Content-Type': 'application/json'}
    
    def test_health_check(self):
        """Testa rota de verificação de saúde da API"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
    
    @patch('config.config.Config.get_supabase_client')
    def test_register_user(self, mock_get_supabase):
        """Testa registro de usuário com dados válidos"""
        # Mock da resposta do Supabase
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        
        # Cria o mock completo para a cadeia de chamadas do Supabase
        mock_get_supabase.return_value = mock_supabase
        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = MagicMock(
            data=[{
                'id': 1, 
                'email': 'test@example.com', 
                'full_name': 'Usuário Teste',
                'cpf': '12345678909',
                'birth_date': '1990-01-01',
                'status': 'active',
                'role': 'user',
                'created_at': '2023-10-10T10:10:10Z',
                'updated_at': '2023-10-10T10:10:10Z'
            }]
        )
        
        # Dados para teste
        test_user = {
            'email': 'test@example.com',
            'full_name': 'Usuário Teste',
            'cpf': '12345678909',
            'birth_date': '1990-01-01'
        }
        
        # Realiza requisição de registro
        response = self.client.post(
            '/api/users/register',
            data=json.dumps(test_user),
            headers=self.headers
        )
        
        # Verifica resposta
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Usuário registrado com sucesso')
        self.assertEqual(data['user']['email'], test_user['email'])
        self.assertEqual(data['user']['full_name'], test_user['full_name'])
        self.assertEqual(data['user']['cpf'], test_user['cpf'])
        
        # Verifica chamadas ao mock
        mock_supabase.table.assert_called_once_with('users')
        mock_table.insert.assert_called_once()
    
    @patch('config.config.Config.get_supabase_client')
    def test_login_user(self, mock_get_supabase):
        """Testa login de usuário com credenciais válidas"""
        # Mock da resposta do Supabase
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_eq = MagicMock()
        mock_execute = MagicMock()
        mock_update = MagicMock()
        
        # Cria o mock completo para a cadeia de chamadas do Supabase
        mock_get_supabase.return_value = mock_supabase
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.eq.return_value = mock_execute
        mock_execute.execute.return_value = MagicMock(
            data=[{
                'id': 1, 
                'email': 'test@example.com', 
                'full_name': 'Usuário Teste',
                'cpf': '12345678909',
                'birth_date': '1990-01-01',
                'status': 'active',
                'role': 'user',
                'created_at': '2023-10-10T10:10:10Z',
                'updated_at': '2023-10-10T10:10:10Z'
            }]
        )
        
        # Mock da atualização do último login
        mock_table.update.return_value = MagicMock()
        mock_table.update.return_value.eq.return_value = MagicMock()
        mock_table.update.return_value.eq.return_value.execute.return_value = None
        
        # Dados para teste
        login_data = {
            'cpf': '12345678909',
            'birth_date': '1990-01-01'
        }
        
        # Realiza requisição de login
        response = self.client.post(
            '/api/users/login',
            data=json.dumps(login_data),
            headers=self.headers
        )
        
        # Verifica resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Login realizado com sucesso')
        self.assertIn('token', data)
        self.assertIn('user', data)

    @patch('config.config.Config.get_supabase_client')
    def test_register_invalid_cpf(self, mock_get_supabase):
        """Testa registro com CPF inválido"""
        # Dados para teste com CPF inválido
        test_user = {
            'email': 'test@example.com',
            'full_name': 'Usuário Teste',
            'cpf': '11111111111',  # CPF inválido (todos os números iguais)
            'birth_date': '1990-01-01'
        }
        
        # Realiza requisição de registro
        response = self.client.post(
            '/api/users/register',
            data=json.dumps(test_user),
            headers=self.headers
        )
        
        # Verifica resposta
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('CPF', data['error'])

if __name__ == '__main__':
    unittest.main()