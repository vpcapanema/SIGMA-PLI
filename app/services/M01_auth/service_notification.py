"""
Serviço de Notificações - SIGMA-PLI
Responsável por enviar notificações de mudanças de status e ativação
"""

from datetime import datetime
from typing import Optional

from app.services.M01_auth.service_email import EmailService


class NotificationService:
    """Serviço para envio de notificações por email"""

    STATUS_MAP = {
        "AGUARDANDO_APROVACAO": "Aguardando Aprovação",
        "APROVADO": "Aprovado",
        "REJEITADO": "Rejeitado",
        "SUSPENSO": "Suspenso",
        "INATIVO": "Inativo",
    }

    @staticmethod
    def _criar_template_email(
        nome_usuario: str, titulo: str, conteudo: str, responsavel: Optional[str] = None
    ) -> str:
        """
        Cria template HTML para emails

        Args:
            nome_usuario: Nome do usuário
            titulo: Título da notificação
            conteudo: Conteúdo principal da mensagem
            responsavel: Nome do responsável pela mudança

        Returns:
            str: HTML do email
        """
        data_formatada = datetime.now().strftime("%d/%m/%Y %H:%M")
        responsavel_html = (
            f'<p style="margin: 5px 0 0 0;"><strong>👤 Responsável:</strong> {responsavel}</p>'
            if responsavel
            else ""
        )

        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{titulo}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}  # noqa: E501
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}  # noqa: E501
                .header {{ background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 30px; text-align: center; }}  # noqa: E501
                .header h1 {{ margin: 0; font-size: 24px; font-weight: 300; }}
                .content {{ padding: 30px; line-height: 1.6; color: #333; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #6c757d; border-top: 1px solid #dee2e6; }}  # noqa: E501
                .info-box {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #2196f3; }}  # noqa: E501
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏛️ SIGMA-PLI</h1>
                    <p>Sistema de Gerenciamento de Cadastros</p>
                </div>
                
                <div class="content">
                    <h2>Olá, {nome_usuario}!</h2>
                    
                    {conteudo}
                    
                    <div class="info-box">
                        <p style="margin: 0;"><strong>📧 Sistema:</strong> SIGMA-PLI - Sistema de Gerenciamento de Cadastros</p>
                        <p style="margin: 5px 0 0 0;"><strong>🕒 Data:</strong> {data_formatada}</p>
                        {responsavel_html}
                    </div>
                    
                    <p>Se você tiver dúvidas ou precisar de suporte, entre em contato com nossa equipe.</p>
                    
                    <p style="margin-top: 30px;">
                        Atenciosamente,<br>
                        <strong>Equipe SIGMA-PLI</strong>
                    </p>
                </div>
                
                <div class="footer">
                    <p>Esta é uma mensagem automática do sistema SIGMA-PLI.</p>
                    <p>Por favor, não responda este email. Para suporte, utilize os canais oficiais.</p>
                    <p>© 2025 SIGMA-PLI - Sistema de Gerenciamento de Cadastros</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    async def notificar_mudanca_status(
        usuario: dict,
        status_anterior: str,
        status_novo: str,
        responsavel: Optional[str] = None,
    ) -> bool:
        """
        Notifica mudança de status do usuário

        Args:
            usuario: Dados do usuário (email_institucional, nome_completo, username)
            status_anterior: Status anterior
            status_novo: Status novo
            responsavel: Nome do responsável pela mudança

        Returns:
            bool: True se enviado com sucesso
        """
        try:
            status_anterior_formatado = NotificationService.STATUS_MAP.get(
                status_anterior, status_anterior
            )
            status_novo_formatado = NotificationService.STATUS_MAP.get(
                status_novo, status_novo
            )

            # Definir mensagem e cor baseadas no status
            if status_novo == "APROVADO":
                cor_status = "#28a745"
                assunto = "✅ Conta Aprovada - SIGMA-PLI"
                mensagem = f"""
                <p>Parabéns! Sua conta no sistema SIGMA-PLI foi <strong style="color: {cor_status};">aprovada</strong>.</p>
                <p>Agora você pode acessar o sistema com suas credenciais.</p>
                <p>Para ativar completamente sua conta, verifique seu email institucional se ainda não o fez.</p>
                """

            elif status_novo == "REJEITADO":
                cor_status = "#dc3545"
                assunto = "❌ Solicitação de Conta Rejeitada - SIGMA-PLI"
                mensagem = f"""
                <p>Informamos que sua solicitação de conta no sistema SIGMA-PLI foi <strong style="color: {cor_status};">rejeitada</strong>.</p>  # noqa: E501
                <p>Para mais informações sobre os motivos da rejeição, entre em contato com o administrador do sistema.</p>
                <p>Você pode enviar uma nova solicitação após resolver as pendências.</p>
                """

            elif status_novo == "SUSPENSO":
                cor_status = "#ffc107"
                assunto = "⚠️ Conta Suspensa - SIGMA-PLI"
                mensagem = f"""
                <p>Sua conta no sistema SIGMA-PLI foi <strong style="color: {cor_status};">suspensa</strong> temporariamente.</p>
                <p>Durante este período, você não poderá acessar o sistema.</p>
                <p>Entre em contato com o administrador para mais informações.</p>
                """

            elif status_novo == "AGUARDANDO_APROVACAO":
                cor_status = "#17a2b8"
                assunto = "🔄 Status Alterado para Aguardando Aprovação - SIGMA-PLI"
                mensagem = f"""
                <p>O status da sua conta foi alterado para <strong style="color: {cor_status};">Aguardando Aprovação</strong>.</p>
                <p>Sua solicitação está sendo analisada por nossa equipe.</p>
                <p>Você receberá uma notificação assim que houver uma decisão.</p>
                """

            else:
                cor_status = "#6c757d"
                assunto = "📋 Status da Conta Alterado - SIGMA-PLI"
                mensagem = f"""
                <p>O status da sua conta no sistema SIGMA-PLI foi alterado.</p>
                <p><strong>Status anterior:</strong> {status_anterior_formatado}</p>
                <p><strong>Status atual:</strong> <span style="color: {cor_status};">{status_novo_formatado}</span></p>
                """

            html_completo = NotificationService._criar_template_email(
                usuario.get("nome_completo", usuario.get("username", "Usuário")),
                assunto.replace("✅ ", "")
                .replace("❌ ", "")
                .replace("⚠️ ", "")
                .replace("🔄 ", "")
                .replace("📋 ", ""),
                mensagem,
                responsavel,
            )

            email = usuario.get("email_institucional") or usuario.get("email")
            if not email:
                raise ValueError("Usuário não possui email válido para notificação")
            
            return await EmailService.enviar_email(
                destinatarios=[email],
                assunto=assunto,
                html=html_completo,
            )

        except Exception as e:
            print(
                f"[NotificationService] Erro ao enviar notificação de mudança de status: {e}"
            )
            return False

    @staticmethod
    async def notificar_mudanca_ativo(
        usuario: dict,
        ativo_anterior: bool,
        ativo_novo: bool,
        responsavel: Optional[str] = None,
    ) -> bool:
        """
        Notifica mudança de status ativo

        Args:
            usuario: Dados do usuário
            ativo_anterior: Status ativo anterior
            ativo_novo: Status ativo novo
            responsavel: Nome do responsável pela mudança

        Returns:
            bool: True se enviado com sucesso
        """
        try:
            if ativo_novo:
                # Conta ativada
                cor_status = "#28a745"
                assunto = "🟢 Conta Ativada - SIGMA-PLI"
                mensagem = f"""
                <p>Excelente! Sua conta no sistema SIGMA-PLI foi <strong style="color: {cor_status};">ativada</strong> com sucesso.</p>  # noqa: E501
                <p>Agora você tem acesso completo às funcionalidades do sistema conforme seu perfil de usuário.</p>
                <p>Faça login no sistema para começar a utilizar os recursos disponíveis.</p>
                <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #28a745;">  # noqa: E501
                    <p style="margin: 0;"><strong>💡 Dica:</strong> Certifique-se de que seu email institucional está verificado para ter acesso total ao sistema.</p>  # noqa: E501
                </div>
                """
            else:
                # Conta desativada
                cor_status = "#dc3545"
                assunto = "🔴 Conta Desativada - SIGMA-PLI"
                mensagem = f"""
                <p>Informamos que sua conta no sistema SIGMA-PLI foi <strong style="color: {cor_status};">desativada</strong>.</p>
                <p>Você não poderá acessar o sistema até que sua conta seja reativada.</p>
                <p>Se você acredita que isso é um erro ou precisa de esclarecimentos, entre em contato com o administrador do sistema.</p>
                <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #dc3545;">  # noqa: E501
                    <p style="margin: 0;"><strong>📞 Suporte:</strong> Para reativação da conta, entre em contato com o departamento responsável.</p>  # noqa: E501
                </div>
                """

            html_completo = NotificationService._criar_template_email(
                usuario.get("nome_completo", usuario.get("username", "Usuário")),
                assunto.replace("🟢 ", "").replace("🔴 ", ""),
                mensagem,
                responsavel,
            )
            
            email = usuario.get("email_institucional") or usuario.get("email")
            if not email:
                raise ValueError("Usuário não possui email válido para notificação")
            
            return await EmailService.enviar_email(
                destinatarios=[email],
                assunto=assunto,
                html=html_completo,
            )

        except Exception as e:
            print(
                f"[NotificationService] Erro ao enviar notificação de mudança de ativo: {e}"
            )
            return False
