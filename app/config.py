"""SIGMA-PLI - Configurações do Sistema"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Aplicação
    app_name: str = "SIGMA-PLI"
    app_version: str = "1.0.0"
    debug: bool = True

    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000

    # PostgreSQL
    database_url: str = Field(default="")  # Connection string completa (prioritária)
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_database: str = Field(default="sigma_pli")
    postgres_user: str = Field(default="sigma_admin")
    postgres_password: SecretStr = Field(default=SecretStr(""))
    postgres_sslmode: str = Field(default="prefer")

    # Neo4j
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: SecretStr = Field(default=SecretStr(""))
    neo4j_database: str = Field(default="neo4j")

    # Neo4j Aura (fallback) - campos adicionais
    neo4j_aura_uri: str = Field(default="")
    neo4j_aura_user: str = Field(default="neo4j")
    neo4j_aura_password: SecretStr = Field(default=SecretStr(""))
    neo4j_username: str = Field(default="neo4j")
    aura_instanceid: str = Field(default="")
    aura_instancename: str = Field(default="")

    # JWT
    jwt_secret_key: str = "sigma-pli-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Upload
    upload_max_size: int = 100 * 1024 * 1024  # 100MB
    upload_allowed_extensions: list = [
        # Documentos texto
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        # Mídia
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".mp4",
        ".mp3",
        # Tabular
        ".csv",
        ".xls",
        ".xlsx",
        ".ods",
        # Geoespacial
        ".shp",
        ".kml",
        ".kmz",
        ".geojson",
        ".gpx",
        ".tif",
        ".tiff",
        ".img",
        ".las",
        ".laz",
        ".ply",
        ".dwg",
        ".dxf",
        ".skp",
        # Outros
        ".sql",
        ".db",
        ".mdb",
        ".gdb",
        ".sde",
        ".zip",
        ".rar",
        ".7z",
    ]

    # GeoServer (futuro)
    geoserver_url: str = "http://localhost:8080/geoserver"
    geoserver_user: str = "admin"
    geoserver_password: str = "geoserver"

    # Feature flags de bancos (permitem subir a API sem bancos)
    enable_postgres: bool = True
    enable_neo4j: bool = False

    # Configurações de Email (SMTP)
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: SecretStr = Field(default=SecretStr(""))
    email_from: str = Field(default="noreply@sigma-pli.gov.br")
    email_admin: str = Field(default="admin@sigma-pli.gov.br")
    frontend_url: str = Field(default="http://127.0.0.1:8010")

    # Keep-Alive (Render)
    enable_keepalive: bool = Field(default=False)  # Ativar em produção
    keepalive_url: str = Field(
        default=""
    )  # URL do próprio servidor (ex: https://sigma-pli.onrender.com)
    keepalive_interval_minutes: int = Field(default=10)  # Intervalo entre pings

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global das configurações
settings = Settings()
