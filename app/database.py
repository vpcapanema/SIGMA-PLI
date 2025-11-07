"""
SIGMA-PLI - Conexões de Banco de Dados
PostgreSQL + Neo4j
"""

import asyncpg
from neo4j import GraphDatabase
from app.config import settings

# PostgreSQL
postgres_pool: asyncpg.Pool = None


async def init_postgres():
    """Inicializar pool de conexões PostgreSQL"""
    global postgres_pool
    if not settings.enable_postgres:
        print("ℹ️ PostgreSQL desabilitado por configuração (enable_postgres=False)")
        return
    try:
        # Se tiver DATABASE_URL, usa ela (prioritário para deploys)
        if settings.database_url:
            postgres_pool = await asyncpg.create_pool(
                dsn=settings.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
        else:
            # Senão, usa as credenciais individuais
            postgres_pool = await asyncpg.create_pool(
                host=settings.postgres_host,
                port=settings.postgres_port,
                database=settings.postgres_database,
                user=settings.postgres_user,
                password=(
                    settings.postgres_password.get_secret_value()
                    if hasattr(settings.postgres_password, "get_secret_value")
                    else settings.postgres_password
                ),
                ssl="require" if settings.postgres_sslmode == "require" else None,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
        print("✅ PostgreSQL conectado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao conectar PostgreSQL: {e}")
        # Não raise - permitir que o app inicie mesmo sem DB


async def close_postgres():
    """Fechar pool PostgreSQL"""
    global postgres_pool
    if postgres_pool:
        await postgres_pool.close()
        print("✅ PostgreSQL desconectado")


# Neo4j
neo4j_driver = None


def init_neo4j():
    """Inicializar driver Neo4j com lazy loading"""
    global neo4j_driver
    if not settings.enable_neo4j:
        print("ℹ️ Neo4j desabilitado por configuração (enable_neo4j=False)")
        return

    # Só tenta conectar se ainda não conectou
    if neo4j_driver is not None:
        return

    # Tentar conectar ao Neo4j local primeiro
    try:
        print("🔄 Conectando ao Neo4j local...")
        neo4j_driver = GraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
        )
        # Verificar conectividade com uma query simples ao invés de verify_connectivity()
        with neo4j_driver.session(database=settings.neo4j_database) as session:
            session.run("RETURN 1").consume()
        print("✅ Neo4j local conectado com sucesso")
    except Exception as e:
        print(f"⚠️ Neo4j local falhou: {str(e)[:50]}...")
        neo4j_driver = None

        # Tentar Aura como fallback
        try:
            print("🔄 Tentando Neo4j Aura...")
            neo4j_driver = GraphDatabase.driver(
                settings.neo4j_aura_uri,
                auth=(settings.neo4j_aura_user, settings.neo4j_aura_password),
            )
            with neo4j_driver.session(database=settings.neo4j_database) as session:
                session.run("RETURN 1").consume()
            print("✅ Neo4j Aura conectado com sucesso")
        except Exception as e2:
            print(f"❌ Neo4j Aura também falhou: {str(e2)[:50]}...")
            neo4j_driver = None


def close_neo4j():
    """Fechar driver Neo4j"""
    global neo4j_driver
    if neo4j_driver:
        neo4j_driver.close()
        print("✅ Neo4j desconectado")


async def init_db():
    """Inicializar todas as conexões de banco"""
    await init_postgres()
    # Neo4j será inicializado sob demanda (lazy loading)
    # init_neo4j()  # Removido para evitar problemas no startup


async def close_db():
    """Fechar todas as conexões de banco"""
    await close_postgres()
    close_neo4j()


# Funções utilitárias para obter conexões
async def get_pg_pool():
    """Obter pool de conexões PostgreSQL"""
    global postgres_pool
    if not postgres_pool:
        await init_postgres()
    return postgres_pool


async def get_postgres_connection():
    """Obter conexão PostgreSQL do pool"""
    if not postgres_pool:
        await init_postgres()
    return await postgres_pool.acquire()


async def get_neo4j_session(database: str = None):
    """Obter sessão Neo4j"""
    if not neo4j_driver:
        init_neo4j()
    if neo4j_driver:
        return neo4j_driver.session(database=database or settings.neo4j_database)
    return None


async def execute_neo4j_query(
    query: str, parameters: dict = None, database: str = None
):
    """
    Executar query Neo4j usando sessões tradicionais

    Args:
        query: Query Cypher
        parameters: Parâmetros da query (não concatenar, usar placeholders)
        database: Nome do banco de dados

    Returns:
        tuple: (records, summary, keys) ou (None, None, None) se erro
    """
    # Tentar inicializar se necessário
    if neo4j_driver is None:
        init_neo4j()

    if neo4j_driver is None:
        print("❌ Neo4j não disponível")
        return None, None, None

    try:
        # Usar sessão tradicional ao invés de execute_query()
        with neo4j_driver.session(
            database=database or settings.neo4j_database
        ) as session:
            result = session.run(query, parameters or {})
            records = list(result)
            summary = result.consume()
            keys = result.keys()
            return records, summary, keys
    except Exception as e:
        print(f"❌ Erro na query Neo4j: {e}")
        return None, None, None


async def create_neo4j_example_graph():
    """
    Criar um grafo de exemplo seguindo as instruções oficiais
    """
    query = """
    CREATE (a:Person {name: $name})
    CREATE (b:Person {name: $friendName})
    CREATE (a)-[:KNOWS]->(b)
    """

    records, summary, keys = await execute_neo4j_query(
        query, {"name": "Alice", "friendName": "David"}
    )

    if summary:
        print(
            "✅ Grafo de exemplo criado: {nodes_created} nós em {time} ms.".format(
                nodes_created=summary.counters.nodes_created,
                time=summary.result_available_after,
            )
        )
        return True
    return False


async def query_neo4j_example():
    """
    Fazer uma query de exemplo seguindo as instruções oficiais
    """
    query = """
    MATCH (p:Person)-[:KNOWS]->(:Person)
    RETURN p.name AS name
    """

    records, summary, keys = await execute_neo4j_query(query)

    if records:
        print(
            f"📊 Query retornou {len(records)} registros em {summary.result_available_after} ms."
        )
        for record in records:
            print(f"   - {record.data()}")
        return records

    return None
