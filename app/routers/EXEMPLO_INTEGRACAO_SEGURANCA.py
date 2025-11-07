"""
Exemplo de Integração da Segurança com Router
==============================================

Este arquivo demonstra como integrar o serviço de criptografia, validadores
e schemas no router de cadastro, garantindo que dados sensíveis (CPF, Telefone, CNPJ)
sejam encriptados automaticamente.

IMPORTANTE:
- Este é um EXEMPLO de como usar os componentes de segurança
- Copie este padrão para seus routers de cadastro/pessoa
- Adapte para os models e endpoints específicos do seu módulo
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.schema_pessoa_fisica import (
    PessoaFisicaCreate,
    PessoaFisicaResponse,
)
from app.services.service_pessoa_fisica import get_pessoa_fisica_service
from app.database import get_db

# Criar router
router = APIRouter(prefix="/api/v1/cadastro", tags=["Cadastro"])


@router.post(
    "/pessoa-fisica",
    response_model=PessoaFisicaResponse,
    summary="Criar nova Pessoa Física",
    description="""
    Cria uma nova Pessoa Física com encriptação automática de dados sensíveis.
    
    **Dados Encriptados Automaticamente:**
    - CPF (com hash para buscas)
    - Telefone (com hash para buscas)
    
    **Validações Aplicadas:**
    - CPF válido (Módulo 11)
    - Telefone válido (10-11 dígitos)
    - Email válido (RFC 5322)
    
    **Resposta:**
    - CPF exibido mascarado (***.***.***-00)
    - Telefone mascarado
    - Nenhum dado encriptado exposto
    
    **LGPD Compliance:**
    - Todas as ações são auditadas
    - Dados sensíveis NUNCA aparecem em logs
    - Só hashes são registrados para rastreabilidade
    """,
)
async def criar_pessoa_fisica(
    dados: PessoaFisicaCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint para criar Pessoa Física com segurança LGPD
    
    Fluxo:
    1. Recebe dados via Pydantic schema (já validados)
    2. Obtém IP do cliente para auditoria
    3. Chama serviço de pessoa física
    4. Serviço encripta dados sensíveis
    5. Retorna schema seguro (mascarado)
    
    Args:
        dados: PessoaFisicaCreate (validado automaticamente pelo Pydantic)
        request: Requisição HTTP (para obter IP do cliente)
        db: Sessão do banco de dados
        
    Returns:
        PessoaFisicaResponse: Pessoa criada com dados mascarados
        
    Raises:
        HTTPException 400: Se dados inválidos (CPF duplicado, email duplicado, etc)
        HTTPException 500: Se erro interno durante encriptação
        
    Exemplo de Uso (cURL):
    ```bash
    curl -X POST "http://localhost:8010/api/v1/cadastro/pessoa-fisica" \\
      -H "Content-Type: application/json" \\
      -d '{
        "nome": "João Silva Santos",
        "cpf": "123.456.789-00",
        "telefone": "(11) 98765-4321",
        "email": "joao@example.com"
      }'
    ```
    
    Exemplo de Resposta:
    ```json
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nome": "João Silva Santos",
      "cpf_display": "***.***.***-00",
      "telefone_display": "(**) ****-4321",
      "email": "joao@example.com",
      "data_criacao": "2024-01-15T10:30:00",
      "ativo": true
    }
    ```
    """
    try:
        # Obter IP do cliente para auditoria LGPD
        usuario_ip = request.client.host if request.client else "0.0.0.0"

        # Obter serviço de pessoa física
        service = get_pessoa_fisica_service()

        # Criar pessoa com encriptação automática
        # O serviço cuida de:
        # - Validação (Pydantic já fez)
        # - Encriptação de CPF e Telefone
        # - Geração de hashes para buscas
        # - Auditoria LGPD
        # - Retorno de schema seguro
        pessoa = await service.criar_pessoa(
            sessao_db=db,
            dados=dados,
            usuario_id="sistema",  # TODO: Obter do token JWT
            usuario_ip=usuario_ip,
        )

        return pessoa

    except ValueError as e:
        # Erros de validação (CPF inválido, email duplicado, etc)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Erro interno
        raise HTTPException(status_code=500, detail=f"Erro ao criar pessoa: {str(e)}")


@router.get(
    "/pessoa-fisica/{pessoa_id}",
    response_model=PessoaFisicaResponse,
    summary="Obter Pessoa Física por ID",
    description="""
    Retorna dados de uma Pessoa Física.
    
    **Segurança:**
    - CPF sempre mascarado (***.***.***-00)
    - Telefone sempre mascarado
    - Dados descriptografados NUNCA são retornados
    - Acesso registrado em auditoria
    """,
)
async def obter_pessoa_fisica(
    pessoa_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint para obter Pessoa Física por ID

    Args:
        pessoa_id: UUID da pessoa
        request: Requisição HTTP (para auditoria)
        db: Sessão do banco de dados

    Returns:
        PessoaFisicaResponse com dados mascarados

    Raises:
        HTTPException 404: Se pessoa não encontrada
    """
    try:
        # TODO: Implementar busca no banco
        # service = get_pessoa_fisica_service()
        # pessoa = await service.buscar_por_id(db, pessoa_id)
        # if not pessoa:
        #     raise HTTPException(status_code=404, detail="Pessoa não encontrada")
        # return pessoa

        raise HTTPException(status_code=501, detail="Endpoint ainda não implementado")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/pessoa-fisica/buscar/cpf/{cpf}",
    response_model=PessoaFisicaResponse,
    summary="Buscar Pessoa Física por CPF",
    description="""
    Busca uma Pessoa Física usando CPF.
    
    **Segurança (Padrão Hash-based Search):**
    - CPF é hasheado antes da busca
    - NUNCA é descriptografado
    - Apenas comparação de hashes com banco
    - Reduz risco de vazamento em logs
    
    **Validação:**
    - CPF válido (Módulo 11)
    - Formatação automática (remove pontos, hífens)
    
    Exemplo: `/api/v1/cadastro/pessoa-fisica/buscar/cpf/12345678900`
    """,
)
async def buscar_pessoa_por_cpf(
    cpf: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Busca Pessoa Física por CPF (usa hash, seguro)

    Args:
        cpf: CPF (com ou sem formatação)
        request: Requisição HTTP
        db: Sessão do banco

    Returns:
        PessoaFisicaResponse com dados mascarados

    Raises:
        HTTPException 400: Se CPF inválido
        HTTPException 404: Se não encontrado
    """
    try:
        # TODO: Validar CPF
        # from app.security.validators import validar_cpf
        # if not validar_cpf(cpf):
        #     raise HTTPException(status_code=400, detail="CPF inválido")

        # TODO: Buscar usando serviço
        # service = get_pessoa_fisica_service()
        # usuario_ip = request.client.host if request.client else "0.0.0.0"
        # pessoa = await service.buscar_por_cpf(
        #     db,
        #     cpf,
        #     usuario_id="sistema",
        #     usuario_ip=usuario_ip
        # )
        # if not pessoa:
        #     raise HTTPException(status_code=404, detail="Pessoa não encontrada")
        # return pessoa

        raise HTTPException(status_code=501, detail="Endpoint ainda não implementado")

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# DOCUMENTAÇÃO DE INTEGRAÇÃO
# =====================================================

"""
COMO USAR ESTE EXEMPLO EM SEU CÓDIGO
=====================================

1. ADICIONAR O ROUTER NO app/routers/__init__.py:
   ```python
   from app.routers.M01_cadastro.router_cadastro_pessoa import router as cadastro_router
   
   def include_routers(app: FastAPI):
       # ... outros routers
       app.include_router(cadastro_router)
   ```

2. NO SEU ROUTER, IMPORTAR:
   ```python
   from app.models.schemas.schema_pessoa_fisica import PessoaFisicaCreate, PessoaFisicaResponse
   from app.services.service_pessoa_fisica import get_pessoa_fisica_service
   from app.security.validators import validar_cpf, validar_telefone
   ```

3. CRIAR ENDPOINT COM ENCRIPTAÇÃO:
   ```python
   @router.post("/pessoa-fisica", response_model=PessoaFisicaResponse)
   async def criar_pessoa(
       dados: PessoaFisicaCreate,  # Pydantic valida automaticamente
       request: Request,
       db: AsyncSession = Depends(get_db),
   ):
       # IP do cliente para auditoria
       usuario_ip = request.client.host if request.client else "0.0.0.0"
       
       # Serviço encripta e salva
       service = get_pessoa_fisica_service()
       pessoa = await service.criar_pessoa(
           db,
           dados,
           usuario_id="admin",
           usuario_ip=usuario_ip
       )
       
       # Retorna schema seguro (mascarado)
       return pessoa
   ```

FLUXO DE SEGURANÇA
==================

1. ENTRADA (POST /api/v1/cadastro/pessoa-fisica)
   └─ JSON: {"nome": "João", "cpf": "123.456.789-00", "telefone": "11987654321"}

2. VALIDAÇÃO PYDANTIC (automática)
   └─ Valida: CPF (Módulo 11), Telefone (10-11 dígitos), Email (RFC 5322)
   └─ Se inválido → HTTPException 422

3. SERVIÇO (get_pessoa_fisica_service().criar_pessoa)
   ├─ Encripta CPF com Fernet
   ├─ Gera hash SHA256 do CPF (para buscas)
   ├─ Encripta Telefone com Fernet
   ├─ Gera hash SHA256 do Telefone
   ├─ Salva no banco: {cpf_criptografado, cpf_hash, telefone_criptografado, telefone_hash}
   └─ Registra auditoria (LGPD): timestamp, usuário, IP, ação

4. RETORNO (PessoaFisicaResponse)
   ├─ id: UUID
   ├─ nome: "João"
   ├─ cpf_display: "***.***.***-00" (MASCARADO)
   ├─ telefone_display: "(**) ****-4321" (MASCARADO)
   ├─ email: "joao@example.com"
   └─ data_criacao: ISO 8601

5. LOG/AUDITORIA (LGPD-compliant)
   └─ {timestamp, acao: CRIACAO, usuario, ip, cpf_hash}
   └─ NUNCA: CPF original, Telefone original, dados descriptografados


PADRÕES DE SEGURANÇA APLICADOS
===============================

✅ ENCRIPTAÇÃO:
   - Fernet (AES-128 CBC) para dados sensíveis (CPF, Telefone, CNPJ)
   - PBKDF2 com SHA256 para derivação de chave
   - Chave mestra em variável de ambiente (MASTER_KEY)

✅ BUSCAS:
   - Hash-based search com SHA256
   - CPF/Telefone NUNCA são descriptografados para buscar
   - Reduz risco de vazamento em logs

✅ MASCARAMENTO:
   - CPF: ***.***.***-00 (últimos 2 dígitos)
   - Telefone: (**) ****-4321 (últimos 4 dígitos)
   - Sempre em response schemas

✅ AUDITORIA (LGPD):
   - Todas as ações registradas: CRIACAO, LEITURA, ATUALIZACAO, DELECAO
   - Dados sensíveis: timestamp, usuário, IP, ação, hash
   - NUNCA: valores originais ou descriptografados

✅ VALIDAÇÃO:
   - CPF: Módulo 11 (detecta valores inválidos)
   - Telefone: 10-11 dígitos (DDD 2 dígitos + 8-9 dígitos)
   - Email: RFC 5322 (Pydantic EmailStr)

✅ ISOLAMENTO:
   - Services: lógica de negócio + criptografia
   - Schemas: validação + mascaramento
   - Routers: apenas orquestração
   - Database: campos separados para encrypted + hash


COMPLIANCE REGULATÓRIO
=======================

✅ LGPD (Lei Geral de Proteção de Dados):
   - Dados pessoais encriptados (CPF, Telefone)
   - Direito ao acesso: dados mascarados
   - Direito ao esquecimento: deletar criptografados
   - Auditoria: log completo de acessos

✅ ISO 27001 (Segurança da Informação):
   - Encriptação de dados sensíveis em repouso
   - Controle de acesso (auditoria)
   - Hash para integridade

✅ PCI DSS (Pagamentos - se aplicável):
   - Dados de cartão encriptados (Fernet)
   - Nenhum armazenamento de CVC
   - Logs de acesso


EXEMPLO COMPLETO DE USO
========================

# 1. Criar Pessoa Física
curl -X POST "http://localhost:8010/api/v1/cadastro/pessoa-fisica" \\
  -H "Content-Type: application/json" \\
  -d '{
    "nome": "Maria Silva",
    "cpf": "98765432100",
    "telefone": "11987654321",
    "email": "maria@example.com"
  }'

# Resposta:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "Maria Silva",
  "cpf_display": "***.***.***-00",
  "telefone_display": "(**) ****-4321",
  "email": "maria@example.com",
  "data_criacao": "2024-01-15T10:30:00",
  "ativo": true
}

# 2. Buscar por CPF (usa hash internamente)
curl "http://localhost:8010/api/v1/cadastro/pessoa-fisica/buscar/cpf/98765432100"

# Resposta: mesma estrutura acima


PRÓXIMOS PASSOS
===============

1. Copiar este padrão para seus routers de cadastro
2. Implementar os TODO's (salvar no banco, buscar, etc)
3. Criar migration para adicionar campos criptografados ao banco
4. Escrever testes de encriptação/descriptografia
5. Testar compliance LGPD com ferramenta de auditoria
6. Documentar políticas de retenção de dados
"""
