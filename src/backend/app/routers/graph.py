from fastapi import APIRouter, HTTPException
from app.db.neo4j_sync import Neo4jSync
from app.db.neo4j_queries import Neo4jQueries
from typing import Dict, List

router = APIRouter(prefix="/graph", tags=["graph"])

@router.post("/sync")
async def sync_graph():
    """Sincroniza dados do PostgreSQL com o Neo4j"""
    sync = Neo4jSync()
    try:
        sync.create_constraints()
        sync.sync_data()
        return {"message": "Sincronização concluída com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        sync.close()

@router.get("/arquivo/{arquivo_id}/relacionamentos")
async def get_arquivo_relacionamentos(arquivo_id: str) -> Dict:
    """Retorna todos os relacionamentos de um arquivo"""
    queries = Neo4jQueries()
    try:
        result = queries.get_arquivo_relacionamentos(arquivo_id)
        if not result:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        return result
    finally:
        queries.close()

@router.get("/produtor/{produtor_id}/arquivos")
async def get_produtor_arquivos(produtor_id: str) -> List[Dict]:
    """Retorna todos os arquivos produzidos por um produtor"""
    queries = Neo4jQueries()
    try:
        return queries.get_produtor_arquivos(produtor_id)
    finally:
        queries.close()

@router.get("/busca/{termo}")
async def busca_semantica(termo: str) -> List[Dict]:
    """Realiza uma busca semântica por arquivos e produtores"""
    queries = Neo4jQueries()
    try:
        return queries.busca_semantica(termo)
    finally:
        queries.close()

@router.get("/arquivo/{arquivo_id}/grafo")
async def get_grafo_relacionamentos(arquivo_id: str, profundidade: int = 2) -> Dict:
    """Retorna o grafo de relacionamentos de um arquivo"""
    queries = Neo4jQueries()
    try:
        return queries.get_grafo_relacionamentos(arquivo_id, profundidade)
    finally:
        queries.close()
