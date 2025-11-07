"""
SIGMA-PLI - Modelos Pydantic
Esquema: dicionario - Perfis e extensões
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

# Modelo base com campos comuns
class BaseModelSIGMA(BaseModel):
    id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Perfil de arquivo
class PerfilBase(BaseModelSIGMA):
    nome: str
    descricao: Optional[str] = None
    icone: Optional[str] = None
    cor: Optional[str] = None
    ativo: bool = True
    ordem: Optional[int] = None

class PerfilCreate(PerfilBase):
    pass

class PerfilUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    icone: Optional[str] = None
    cor: Optional[str] = None
    ativo: Optional[bool] = None
    ordem: Optional[int] = None

class PerfilResponse(PerfilBase):
    pass

# Extensão de arquivo
class ExtensaoBase(BaseModelSIGMA):
    nome: str
    descricao: Optional[str] = None
    mime_type: Optional[str] = None
    categoria: str
    ativo: bool = True

class ExtensaoCreate(ExtensaoBase):
    pass

class ExtensaoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    mime_type: Optional[str] = None
    categoria: Optional[str] = None
    ativo: Optional[bool] = None

class ExtensaoResponse(ExtensaoBase):
    pass

# Listas para respostas
class PerfisList(BaseModel):
    perfis: List[PerfilResponse]
    total: int

class ExtensoesList(BaseModel):
    extensoes: List[ExtensaoResponse]
    total: int