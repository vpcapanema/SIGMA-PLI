# Configurações do Banco de Dados PostgreSQL
DB_CONFIG = {
    "host": "sigma-pli-postgresql-db.cwlmgwc4igdh.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "database": "sigma_pli",
    "user": "sigma_admin",
    "password": "Malditas131533*",
    "sslmode": "require"
}

# String de conexão para SQLAlchemy
DATABASE_URL = "postgresql://sigma_admin:Malditas131533*@sigma-pli-postgresql-db.cwlmgwc4igdh.us-east-1.rds.amazonaws.com:5432/sigma_pli"

# Configurações do Neo4j Aura (PRINCIPAL) - NOVA INSTÂNCIA AUREA (2025-10-29)
NEO4J_CONFIG = {
    "uri": "neo4j+s://6b7fc90e.databases.neo4j.io",
    "user": "neo4j",
    "password": "RWpV06f_yQ9CAo2NbsP76jhNbInaZgE0kOxOBSdQDRs",
    "database": "neo4j",
    "instance_id": "6b7fc90e",
    "instance_name": "SIGMA-PLI-NEO4J",
    "aura_url": "https://6b7fc90e.databases.neo4j.io/db/neo4j/query/v2"
}

# Configurações do Neo4j Local (BACKUP)
NEO4J_LOCAL_CONFIG = {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "sigma123456",
    "database": "neo4j",
    "instance_id": "local",
    "instance_name": "Local Neo4j",
    "browser_url": "http://localhost:7474"
}

# Configurações adicionais
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True  # Set to False em produção
