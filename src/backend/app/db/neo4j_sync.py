from neo4j import GraphDatabase
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Dict, List

class Neo4jSync:
    def __init__(self):
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "sigma_pass")
        self.pg_dsn = os.getenv("DATABASE_URL", "postgresql://sigma_user:sigma_pass@db:5432/sigma_pli")
        
        self.neo4j_driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )
        
    def close(self):
        self.neo4j_driver.close()

    def sync_arquivo_nodes(self, tx, arquivos: List[Dict]):
        """Sincroniza nós do tipo Arquivo"""
        for arquivo in arquivos:
            tx.run("""
                MERGE (a:Arquivo {id: $id})
                SET a.nome = $nome,
                    a.hash = $hash,
                    a.mime_type = $mime_type,
                    a.data_upload = $data_upload
            """, id=str(arquivo['id']), 
                 nome=arquivo['nome'],
                 hash=arquivo['hash'],
                 mime_type=arquivo['mime_type'],
                 data_upload=arquivo['data_upload'].isoformat())

    def sync_produtor_nodes(self, tx, produtores: List[Dict]):
        """Sincroniza nós do tipo Produtor"""
        for produtor in produtores:
            tx.run("""
                MERGE (p:Produtor {id: $id})
                SET p.nome = $nome,
                    p.email = $email,
                    p.departamento = $departamento
            """, id=str(produtor['id']),
                 nome=produtor['nome'],
                 email=produtor['email'],
                 departamento=produtor['departamento'])

    def sync_relationships(self, tx, relationships: List[Dict]):
        """Cria relacionamentos entre Arquivo e Produtor"""
        for rel in relationships:
            tx.run("""
                MATCH (a:Arquivo {id: $arquivo_id})
                MATCH (p:Produtor {id: $produtor_id})
                MERGE (a)-[r:PRODUZIDO_POR]->(p)
            """, arquivo_id=str(rel['arquivo_id']),
                 produtor_id=str(rel['produtor_id']))

    def sync_data(self):
        """Sincroniza todos os dados do PostgreSQL para o Neo4j"""
        with psycopg2.connect(self.pg_dsn) as pg_conn:
            with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Busca arquivos
                cur.execute("""
                    SELECT id, nome, hash, mime_type, data_upload 
                    FROM dicionario.arquivo
                """)
                arquivos = cur.fetchall()

                # Busca produtores
                cur.execute("""
                    SELECT id, nome, email, departamento 
                    FROM dicionario.produtor
                """)
                produtores = cur.fetchall()

                # Busca relacionamentos
                cur.execute("""
                    SELECT arquivo_id, produtor_id 
                    FROM dicionario.arquivo_produtor
                """)
                relationships = cur.fetchall()

        with self.neo4j_driver.session() as session:
            # Sincroniza nós
            session.execute_write(self.sync_arquivo_nodes, arquivos)
            session.execute_write(self.sync_produtor_nodes, produtores)
            # Sincroniza relacionamentos
            session.execute_write(self.sync_relationships, relationships)

    def create_constraints(self):
        """Cria constraints necessárias no Neo4j"""
        with self.neo4j_driver.session() as session:
            # Constraint para Arquivo
            session.run("""
                CREATE CONSTRAINT arquivo_id IF NOT EXISTS
                FOR (a:Arquivo) REQUIRE a.id IS UNIQUE
            """)
            
            # Constraint para Produtor
            session.run("""
                CREATE CONSTRAINT produtor_id IF NOT EXISTS
                FOR (p:Produtor) REQUIRE p.id IS UNIQUE
            """)

if __name__ == "__main__":
    sync = Neo4jSync()
    try:
        sync.create_constraints()
        sync.sync_data()
    finally:
        sync.close()
