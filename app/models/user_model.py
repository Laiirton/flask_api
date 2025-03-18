from datetime import datetime
from typing import Dict, Optional, Any

class User:
    def __init__(
        self,
        id: Optional[int] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        cpf: Optional[str] = None,
        birth_date: Optional[str] = None,
        status: str = "active",
        role: str = "user",
        last_login: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.cpf = cpf
        self.birth_date = birth_date
        self.status = status
        self.role = role
        self.last_login = last_login
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Cria uma instância de User a partir de um dicionário
        """
        return cls(
            id=data.get('id'),
            email=data.get('email'),
            full_name=data.get('full_name'),
            cpf=data.get('cpf'),
            birth_date=data.get('birth_date'),
            status=data.get('status', 'active'),
            role=data.get('role', 'user'),
            last_login=data.get('last_login'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a instância de User para dicionário
        """
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'cpf': self.cpf,
            'birth_date': self.birth_date,
            'status': self.status,
            'role': self.role,
            'last_login': self.last_login,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def to_response_dict(self) -> Dict[str, Any]:
        """
        Converte a instância de User para dicionário para resposta da API
        (exclui informações sensíveis)
        """
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'cpf': self.cpf,
            'birth_date': self.birth_date,
            'status': self.status,
            'role': self.role,
            'last_login': self.last_login,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }