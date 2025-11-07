# 📧 Serviço de Email - SIGMA-PLI

## 📋 Visão Geral

O serviço de email foi implementado para notificar usuários sobre o status das solicitações de cadastro e mudanças de status nas contas. Este serviço é baseado na implementação do **PLI-CADASTRO** (`emailService.js` e `notificationService.js`) e adaptado para Python/FastAPI.

## 🏗️ Arquitetura

### Arquivos Criados:

1. **`app/services/M01_auth/service_email.py`**

   - Serviço principal de envio de emails
   - Baseado em `smtplib` (biblioteca nativa Python)
   - Funções: envio genérico, confirmação, aprovação, rejeição, notificação admins

2. **`app/services/M01_auth/service_notification.py`**
   - Serviço de notificações de mudança de status
   - Envia emails formatados para mudanças de status e ativação
   - Templates HTML profissionais

### Integração:

- **`app/services/M01_auth/service_auth.py`**: Integrado no fluxo de registro (`register_user()`)
- **`app/config.py`**: Configurações de SMTP adicionadas
- **`.env`**: Variáveis de ambiente para credenciais de email

## 🔧 Configuração

### 1. Configurar `.env`

Edite o arquivo `.env` com suas credenciais SMTP:

```properties
# Gmail (recomendado para desenvolvimento)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app-gmail
EMAIL_FROM=noreply@sigma-pli.gov.br
EMAIL_ADMIN=admin@sigma-pli.gov.br
FRONTEND_URL=http://127.0.0.1:8010
```

### 2. Obter Senha de App do Gmail

Para usar Gmail, você precisa criar uma **Senha de App**:

1. Acesse: https://myaccount.google.com/security
2. Ative a **Verificação em duas etapas**
3. Vá em **Senhas de app**
4. Selecione "Email" e "Outro dispositivo personalizado"
5. Copie a senha gerada (16 caracteres sem espaços)
6. Cole em `SMTP_PASSWORD` no `.env`

### 3. Testar Conexão

Execute este script para testar a conexão:

```python
from app.services.M01_auth.service_email import EmailService
import asyncio

asyncio.run(EmailService.testar_conexao())
```

## 📨 Fluxo de Emails

### 1. **Solicitação de Cadastro**

Quando um usuário se registra (`POST /api/v1/auth/register`):

#### Email para o Usuário:

- **Assunto**: "Solicitação de Acesso Recebida - SIGMA-PLI"
- **Conteúdo**:
  - Confirmação de recebimento
  - Protocolo da solicitação
  - Próximos passos
  - Anexo: Comprovante HTML

#### Email para Administradores:

- **Assunto**: "Nova Solicitação de Acesso - SIGMA-PLI"
- **Conteúdo**:
  - Dados do solicitante
  - Link para painel administrativo
  - Anexo: Comprovante HTML

### 2. **Aprovação de Cadastro**

```python
from app.services.M01_auth.service_email import EmailService

usuario = {
    "nome_completo": "João Silva",
    "email": "joao@example.com"
}

await EmailService.enviar_aprovacao(usuario)
```

- **Assunto**: "✅ Acesso Aprovado - SIGMA-PLI"
- **Conteúdo**: Confirmação de aprovação + link para login

### 3. **Rejeição de Cadastro**

```python
await EmailService.enviar_rejeicao(usuario, motivo="Documentação incompleta")
```

- **Assunto**: "❌ Solicitação de Acesso Não Aprovada - SIGMA-PLI"
- **Conteúdo**: Notificação + motivo (opcional)

### 4. **Mudança de Status**

```python
from app.services.M01_auth.service_notification import NotificationService

await NotificationService.notificar_mudanca_status(
    usuario=usuario,
    status_anterior="AGUARDANDO_APROVACAO",
    status_novo="APROVADO",
    responsavel="Admin SIGMA"
)
```

Status disponíveis:

- `AGUARDANDO_APROVACAO`
- `APROVADO`
- `REJEITADO`
- `SUSPENSO`
- `INATIVO`

### 5. **Ativação/Desativação de Conta**

```python
await NotificationService.notificar_mudanca_ativo(
    usuario=usuario,
    ativo_anterior=False,
    ativo_novo=True,
    responsavel="Admin SIGMA"
)
```

## 🎨 Templates de Email

Todos os emails usam templates HTML responsivos com:

- ✅ Design profissional
- ✅ Logo e identidade visual SIGMA-PLI
- ✅ Compatibilidade com clientes de email
- ✅ Informações de data/hora/responsável
- ✅ Links de ação (quando aplicável)

## 🔐 Segurança

### Boas Práticas Implementadas:

1. **Senhas Protegidas**: Uso de `SecretStr` do Pydantic
2. **TLS/SSL**: Conexão segura via `starttls()`
3. **Validação**: Verificação de destinatários antes de envio
4. **Logs**: Registro de erros sem expor credenciais
5. **Fallback**: Não bloqueia cadastro se email falhar

### Exemplo de Erro Tratado:

```python
try:
    await EmailService.enviar_confirmacao_solicitacao(usuario)
except Exception as email_error:
    print(f"[AuthService] Aviso: Erro ao enviar emails: {email_error}")
    # Cadastro continua mesmo se email falhar
```

## 📊 Uso no Código

### No Registro de Usuário:

```python
# app/services/M01_auth/service_auth.py

user_id = await UserService.create_user(...)

# Preparar dados para email
usuario_email = {
    "id": str(user_id),
    "nome_completo": "João Silva",
    "email": "joao@example.com",
    "email_institucional": "joao@prefeitura.gov.br",
    "instituicao": "Prefeitura Municipal",
    "tipo_usuario": "GESTOR",
    "username": "joao.silva_GESTOR"
}

# Enviar emails (não bloqueia se falhar)
await EmailService.enviar_confirmacao_solicitacao(usuario_email)
await EmailService.notificar_administradores(usuario_email)
```

### Em Endpoints Administrativos (futuro):

```python
@router.patch("/admin/usuarios/{user_id}/aprovar")
async def aprovar_usuario(user_id: str):
    # Atualizar status no banco
    await UserService.update_status(user_id, "APROVADO")

    # Buscar dados do usuário
    usuario = await UserService.get_user_by_id(user_id)

    # Enviar email de aprovação
    await EmailService.enviar_aprovacao(usuario)

    return {"success": True}
```

## 🚀 Melhorias Futuras

### 1. **Fila de Emails**

- Implementar Celery ou RQ para processamento em background
- Retry automático em caso de falha

### 2. **Templates Avançados**

- Usar Jinja2 para templates de email
- Suporte a diferentes idiomas

### 3. **Tracking**

- Registrar envios no banco de dados
- Rastreamento de abertura (via pixel tracker)

### 4. **Provedores Alternativos**

- SendGrid integration
- Amazon SES
- Microsoft Graph API (para Outlook/Office 365)

## 📝 Checklist de Implementação

- ✅ Serviço de email criado (`service_email.py`)
- ✅ Serviço de notificações criado (`service_notification.py`)
- ✅ Configurações adicionadas (`config.py`)
- ✅ Variáveis de ambiente configuradas (`.env`)
- ✅ Integrado no fluxo de registro (`service_auth.py`)
- ⏳ Testar envio de emails
- ⏳ Configurar credenciais reais
- ⏳ Implementar endpoints administrativos (aprovação/rejeição)

## 🐛 Troubleshooting

### Erro: "Authentication failed"

- **Solução**: Verifique se a senha de app está correta
- Use senha de app, não a senha normal do Gmail

### Erro: "Connection refused"

- **Solução**: Verifique firewall e porta (587 ou 465)
- Tente com `SMTP_PORT=465` e `secure=True`

### Emails não chegam

- **Solução**: Verifique spam/lixeira
- Confirme que `EMAIL_FROM` está configurado
- Use domínio confiável em produção

## 📞 Suporte

Para dúvidas sobre implementação:

1. Verificar logs: `print` statements mostram erros detalhados
2. Testar conexão: `EmailService.testar_conexao()`
3. Validar configurações: conferir `.env` e `config.py`

---

**Implementado em**: 03/11/2025  
**Baseado em**: PLI-CADASTRO `emailService.js` e `notificationService.js`  
**Tecnologia**: Python 3.11+, smtplib, FastAPI
