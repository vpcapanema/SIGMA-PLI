from neo4j import GraphDatabase
from typing import List, Dict, Optional
import os

class Neo4jQueries:
    def __init__(self):
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "sigma_pass")
        
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )

    def close(self):
        self.driver.close()

    def get_arquivo_relacionamentos(self, arquivo_id: str) -> Dict:
        """Retorna todos os relacionamentos de um arquivo"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Arquivo {id: $id})
                OPTIONAL MATCH (a)-[r]->(n)
                RETURN a, collect(DISTINCT {type: type(r), node: n}) as relacionamentos
            """, id=arquivo_id)
            record = result.single()
            if not record:
                return None
            
            arquivo = dict(record["a"])
            relacionamentos = [
                {
                    "tipo": rel["type"],
                    "node": dict(rel["node"])
                }
                for rel in record["relacionamentos"]
                if rel["node"] is not None
            ]
            
            return {
                "arquivo": arquivo,
                "relacionamentos": relacionamentos
            }

    def get_produtor_arquivos(self, produtor_id: str) -> List[Dict]:
        """Retorna todos os arquivos produzidos por um produtor"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Produtor {id: $id})<-[:PRODUZIDO_POR]-(a:Arquivo)
                RETURN a
            """, id=produtor_id)
            
            return [dict(record["a"]) for record in result]

    def busca_semantica(self, termo: str) -> List[Dict]:
        """Realiza uma busca semântica por arquivos e produtores"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE (n:Arquivo OR n:Produtor)
                AND any(prop in keys(n) WHERE n[prop] CONTAINS $termo)
                RETURN n, labels(n) as tipos
            """, termo=termo)
            
            return [
                {
                    "id": dict(record["n"])["id"],
                    "tipo": record["tipos"][0],
                    "propriedades": dict(record["n"])
                }
                for record in result
            ]

    def get_grafo_relacionamentos(self, arquivo_id: str, profundidade: int = 2) -> Dict:
        """Retorna o grafo de relacionamentos de um arquivo até uma certa profundidade"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = (a:Arquivo {id: $id})-[*1..$prof]-(n)
                RETURN path
            """, id=arquivo_id, prof=profundidade)
            
            nodes = set()
            relationships = set()
            
            for record in result:
                path = record["path"]
                for node in path.nodes:
                    nodes.add((node.id, list(node.labels)[0], dict(node)))
                for rel in path.relationships:
                    relationships.add((rel.type, rel.start_node.id, rel.end_node.id))
            
            return {
                "nodes": [
                    {
                        "id": n[0],
                        "type": n[1],
                        "properties": n[2]
                    }
                    for n in nodes
                ],
                "relationships": [
                    {
                        "type": r[0],
                        "source": r[1],
                        "target": r[2]
                    }
                    for r in relationships
                ]
            }
