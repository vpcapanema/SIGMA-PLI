"""
Serviço de Email - SIGMA-PLI
Responsável pelo envio de emails de notificação do sistema
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from datetime import datetime
import uuid

from app.config import settings


class EmailService:
    """Serviço para envio de emails"""

    @staticmethod
    def _criar_conexao_smtp():
        """Cria conexão SMTP baseada nas configurações"""
        try:
            # Verificar se é Gmail
            if "gmail" in settings.smtp_host.lower():
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(
                    settings.smtp_user, settings.smtp_password.get_secret_value()
                )
                return server

            # Configuração genérica SMTP
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password.get_secret_value())
            return server

        except Exception as e:
            print(f"[EmailService] Erro ao criar conexão SMTP: {e}")
            raise

    @staticmethod
    async def enviar_email(
        destinatarios: List[str],
        assunto: str,
        html: str,
        anexos: Optional[List[dict]] = None,
    ) -> bool:
        """
        Envia email genérico

        Args:
            destinatarios: Lista de emails destinatários
            assunto: Assunto do email
            html: Conteúdo HTML do email
            anexos: Lista de anexos [{filename: str, content: str, content_type: str}]

        Returns:
            bool: True se enviado com sucesso
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = settings.email_from
            msg["To"] = ", ".join(destinatarios)
            msg["Subject"] = assunto

            # Adicionar corpo HTML
            msg.attach(MIMEText(html, "html", "utf-8"))

            # Adicionar anexos se houver
            if anexos:
                for anexo in anexos:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(anexo["content"].encode("utf-8"))
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="{anexo["filename"]}"',
                    )
                    msg.attach(part)

            # Enviar email
            server = EmailService._criar_conexao_smtp()
            server.send_message(msg)
            server.quit()

            print(
                f"[EmailService] Email enviado com sucesso para: {', '.join(destinatarios)}"
            )
            return True

        except Exception as e:
            print(f"[EmailService] Erro ao enviar email: {e}")
            return False

    @staticmethod
    def _gerar_comprovante_html(usuario: dict) -> str:
        """Gera HTML do comprovante de solicitação"""
        protocolo = usuario.get("id", f"PLI-{uuid.uuid4().hex[:8].upper()}")
        data_formatada = datetime.now().strftime("%d/%m/%Y %H:%M")

        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Comprovante de Solicitação de Cadastro - SIGMA-PLI</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h1 {{ color: #007bff; }}
                .section {{ margin-bottom: 25px; border: 1px solid #ddd;
                    border-radius: 5px; padding: 15px; }}
                .section-title {{ background-color: #007bff; color: white;
                    padding: 10px; margin: -15px -15px 15px -15px;
                    border-radius: 5px 5px 0 0; }}
                .field {{ margin-bottom: 10px; }}
                .field-label {{ font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 30px;
                    font-size: 0.9em; color: #666; }}
                .protocol {{ background-color: #f8f9fa; padding: 10px;
                    border-radius: 5px; text-align: center;
                    font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Comprovante de Solicitação de Cadastro</h1>
                    <p>Sistema SIGMA-PLI</p>
                </div>
                
                <div class="protocol">
                    Protocolo: {protocolo}<br>
                    Data/Hora: {data_formatada}
                </div>
                
                <div class="section">
                    <h3 class="section-title">Dados Pessoais</h3>
                    <div class="field">
                        <span class="field-label">Nome Completo:</span> {usuario.get('nome_completo', '')}
                    </div>
                    <div class="field">
                        <span class="field-label">Email:</span> {usuario.get('email', '')}
                    </div>
                    <div class="field">
                        <span class="field-label">Telefone:</span> {usuario.get('telefone', '')}
                    </div>
                    <div class="field">
                        <span class="field-label">CPF:</span> {usuario.get('cpf', '')}
                    </div>
                </div>
                
                <div class="section">
                    <h3 class="section-title">Dados Profissionais</h3>
                    <div class="field">
                        <span class="field-label">Instituição:</span> {usuario.get('instituicao', '')}
                    </div>
                    <div class="field">
                        <span class="field-label">Email Institucional:</span> {usuario.get('email_institucional', '')}
                    </div>
                    <div class="field">
                        <span class="field-label">Telefone Institucional:</span> {usuario.get('telefone_institucional', '')}
                    </div>
                </div>
                
                <div class="section">
                    <h3 class="section-title">Dados de Acesso</h3>
                    <div class="field">
                        <span class="field-label">Tipo de Usuário:</span> {usuario.get('tipo_usuario', '')}
                    </div>
                    <div class="field">
                        <span class="field-label">Nome de Usuário:</span> {usuario.get('username', '')}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Este documento é um comprovante de solicitação de cadastro no SIGMA-PLI.</p>
                    <p>A solicitação está sujeita à aprovação pelos administradores do sistema.</p>
                    <p>&copy; {datetime.now().year} Sistema SIGMA-PLI</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    async def enviar_confirmacao_solicitacao(usuario: dict) -> bool:
        """
        Envia email de confirmação de solicitação de cadastro para o usuário

        Args:
            usuario: Dados do usuário (nome_completo, email, email_institucional, etc)

        Returns:
            bool: True se enviado com sucesso
        """
        try:
            protocolo = usuario.get("id", f"PLI-{uuid.uuid4().hex[:8].upper()}")
            comprovante_html = EmailService._gerar_comprovante_html(usuario)

            # Lista de destinatários
            destinatarios = []
            if usuario.get("email"):
                destinatarios.append(usuario["email"])
            if usuario.get("email_institucional") and usuario[
                "email_institucional"
            ] != usuario.get("email"):
                destinatarios.append(usuario["email_institucional"])

            if not destinatarios:
                print("[EmailService] Nenhum destinatário encontrado")
                return False

            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px;  # noqa: E501
                margin: 0 auto; padding: 20px; border: 1px solid #ddd;
                border-radius: 5px;">
                <h2 style="color: #007bff;">
                    Solicitação de Acesso Recebida
                </h2>
                <p>Olá <strong>{usuario.get('nome_completo', 'Usuário')
                    }</strong>,</p>  # noqa: E501
                <p>Sua solicitação de acesso ao <strong>SIGMA-PLI</strong>
                    foi recebida com sucesso.</p>
                <p><strong>Protocolo:</strong> {protocolo}</p>  # noqa: E501

                <h3>Próximos Passos:</h3>
                <ol>
                    <li><strong>Etapa Atual:</strong> Solicitação recebida
                        e aguardando análise.</li>
                    <li><strong>Próxima Etapa:</strong> Análise pelos administradores ou gestores do sistema.</li>
                    <li><strong>Etapa Final:</strong> Aprovação ou rejeição da solicitação.</li>
                </ol>
                
                <p>Você receberá um email quando sua solicitação for analisada.</p>
                <p>Em anexo, você encontrará o comprovante da sua solicitação de cadastro.</p>
                
                <p>Atenciosamente,<br>Equipe SIGMA-PLI</p>
            </div>
            """

            anexos = [
                {
                    "filename": f"Comprovante_Solicitacao_{usuario.get('nome_completo', 'Usuario').replace(' ', '_')}.html",
                    "content": comprovante_html,
                    "content_type": "text/html",
                }
            ]

            return await EmailService.enviar_email(
                destinatarios=destinatarios,
                assunto="Solicitação de Acesso Recebida - SIGMA-PLI",
                html=html,
                anexos=anexos,
            )

        except Exception as e:
            print(f"[EmailService] Erro ao enviar confirmação de solicitação: {e}")
            return False

    @staticmethod
    async def notificar_administradores(usuario: dict) -> bool:
        """
        Notifica administradores sobre nova solicitação de acesso

        Args:
            usuario: Dados do usuário

        Returns:
            bool: True se enviado com sucesso
        """
        try:
            comprovante_html = EmailService._gerar_comprovante_html(usuario)

            # Emails de administradores (configurável via settings)
            emails_admins = (
                [settings.email_admin] if hasattr(settings, "email_admin") else []
            )

            if not emails_admins:
                print("[EmailService] Nenhum email de administrador configurado")
                return False

            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">  # noqa: E501
                <h2 style="color: #007bff;">Nova Solicitação de Acesso</h2>
                <p>Uma nova solicitação de acesso foi recebida:</p>
                <ul>
                    <li><strong>Nome:</strong> {usuario.get('nome_completo', '')}</li>
                    <li><strong>Email:</strong> {usuario.get('email', '')}</li>
                    <li><strong>Email Institucional:</strong> {usuario.get('email_institucional', 'Não informado')}</li>
                    <li><strong>Instituição:</strong> {usuario.get('instituicao', '')}</li>
                    <li><strong>Tipo de Usuário:</strong> {usuario.get('tipo_usuario', '')}</li>
                    <li><strong>Nome de Usuário:</strong> {usuario.get('username', '')}</li>
                </ul>
                
                <p style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                    <strong>Ação Necessária:</strong> Acesse o painel administrativo para aprovar ou rejeitar esta solicitação.
                </p>
                
                <p>
                    <a href="{settings.frontend_url}/admin/usuarios"   # noqa: E501
                       style="background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; display: inline-block;">  # noqa: E501
                        Acessar Painel de Usuários
                    </a>
                </p>
                
                <p>Atenciosamente,<br>Sistema SIGMA-PLI</p>
            </div>
            """

            anexos = [
                {
                    "filename": f"Comprovante_Solicitacao_{usuario.get('nome_completo', 'Usuario').replace(' ', '_')}.html",
                    "content": comprovante_html,
                    "content_type": "text/html",
                }
            ]

            return await EmailService.enviar_email(
                destinatarios=emails_admins,
                assunto="Nova Solicitação de Acesso - SIGMA-PLI",
                html=html,
                anexos=anexos,
            )

        except Exception as e:
            print(f"[EmailService] Erro ao notificar administradores: {e}")
            return False

    @staticmethod
    async def enviar_aprovacao(usuario: dict) -> bool:
        """
        Envia email de aprovação para o usuário

        Args:
            usuario: Dados do usuário

        Returns:
            bool: True se enviado com sucesso
        """
        try:
            # Obter email válido
            email = usuario.get("email") or usuario.get("email_institucional")
            if not email:
                print("[EmailService] Nenhum email encontrado para enviar aprovação")
                return False

            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">  # noqa: E501
                <h2 style="color: #28a745;">✅ Acesso Aprovado!</h2>
                <p>Olá <strong>{usuario.get('nome_completo', 'Usuário')}</strong>,</p>  # noqa: E501
                <p>Sua solicitação de acesso ao <strong>SIGMA-PLI</strong> foi <strong style="color: #28a745;">APROVADA</strong>.</p>  # noqa: E501
                <p>Você já pode acessar o sistema utilizando seu nome de usuário e senha cadastrados.</p>
                <p>
                    <a href="{settings.frontend_url}/auth/login"   # noqa: E501
                       style="background-color: #28a745; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">  # noqa: E501
                        Acessar o Sistema
                    </a>
                </p>
                <p>Atenciosamente,<br>Equipe SIGMA-PLI</p>
            </div>
            """

            return await EmailService.enviar_email(
                destinatarios=[email],
                assunto="✅ Acesso Aprovado - SIGMA-PLI",
                html=html,
            )

        except Exception as e:
            print(f"[EmailService] Erro ao enviar aprovação: {e}")
            return False

    @staticmethod
    async def enviar_rejeicao(usuario: dict, motivo: Optional[str] = None) -> bool:
        """
        Envia email de rejeição para o usuário

        Args:
            usuario: Dados do usuário
            motivo: Motivo da rejeição

        Returns:
            bool: True se enviado com sucesso
        """
        try:
            # Obter email válido
            email = usuario.get("email") or usuario.get("email_institucional")
            if not email:
                print("[EmailService] Nenhum email encontrado para enviar rejeição")
                return False

            motivo_html = f"<p><strong>Motivo:</strong> {motivo}</p>" if motivo else ""

            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">  # noqa: E501
                <h2 style="color: #dc3545;">❌ Solicitação de Acesso Não Aprovada</h2>
                <p>Olá <strong>{usuario.get('nome_completo', 'Usuário')}</strong>,</p>  # noqa: E501
                <p>Sua solicitação de acesso ao <strong>SIGMA-PLI</strong> não foi aprovada neste momento.</p>  # noqa: E501
                {motivo_html}
                <p>Se você acredita que isso é um erro ou precisa de mais informações, entre em contato conosco respondendo a este email.</p>
                <p>Atenciosamente,<br>Equipe SIGMA-PLI</p>
            </div>
            """

            return await EmailService.enviar_email(
                destinatarios=[email],
                assunto="❌ Solicitação de Acesso Não Aprovada - SIGMA-PLI",
                html=html,
            )

        except Exception as e:
            print(f"[EmailService] Erro ao enviar rejeição: {e}")
            return False

    @staticmethod
    async def testar_conexao() -> bool:
        """
        Testa a conexão com o servidor de email

        Returns:
            bool: True se conexão bem-sucedida
        """
        try:
            server = EmailService._criar_conexao_smtp()
            server.quit()
            print(
                "[EmailService] Conexão com servidor de email estabelecida com sucesso"
            )
            return True
        except Exception as e:
            print(f"[EmailService] Erro ao conectar com servidor de email: {e}")
            return False
