import argparse
import csv
import os
from neo4j import GraphDatabase
import zipfile
import io

CSV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'neo4j_dicionario_de_dados'))

def resolve_csv_dir(provided=None):
    candidates = []
    if provided:
        candidates.append(os.path.abspath(provided))
    candidates.append(CSV_DIR)
    # also check common alternative path (workspace sibling)
    candidates.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'SEMIL', 'PLI', 'Demandas', '02_Aplicacoes', 'sigma_pli', 'banco_de_dados', 'neo4j_dicionario_de_dados')))
    for c in candidates:
        if not c:
            continue
        if os.path.isdir(c):
            return c
        if os.path.isfile(c) and zipfile.is_zipfile(c):
            return c
    return None

def read_csv(name, csv_dir):
    # support csv_dir being a directory or a zip file
    if os.path.isfile(csv_dir) and zipfile.is_zipfile(csv_dir):
        with zipfile.ZipFile(csv_dir) as zf:
            try:
                with zf.open(name) as f:
                    text = io.TextIOWrapper(f, encoding='utf-8')
                    reader = csv.DictReader(text)
                    for row in reader:
                        yield {k: (v if v!='' else None) for k,v in row.items()}
            except KeyError:
                raise FileNotFoundError(name)
    else:
        path = os.path.join(csv_dir, name)
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield {k: (v if v!='' else None) for k,v in row.items()}

def import_nodes(driver, dry_run=False, csv_dir=None):
    with driver.session() as session:
        # Example: import Instituicao
        for row in read_csv('nodes_instituicao.csv', csv_dir):
            if dry_run:
                print('DRY RUN - Instituicao', row.get('id'))
                continue
            session.run("MERGE (i:Instituicao {id:$id}) SET i.nome=$nome, i.sigla=$sigla, i.cnpj=$cnpj, i.tipo=$tipo",
                        row)

        # Add other nodes similarly
        for row in read_csv('nodes_projeto.csv', csv_dir):
            if dry_run:
                print('DRY RUN - Projeto', row.get('id'))
                continue
            session.run("MERGE (p:Projeto {id:$id}) SET p.nome=$nome, p.sigla=$sigla, p.descricao=$descricao, p.status=$status, p.data_inicio=$data_inicio, p.data_fim=$data_fim",
                        row)

        for row in read_csv('nodes_pessoa.csv', csv_dir):
            if dry_run:
                print('DRY RUN - Pessoa', row.get('id'))
                continue
            session.run("MERGE (ps:Pessoa {id:$id}) SET ps.nome=$nome, ps.email=$email, ps.funcao=$funcao, ps.instituicao_id=$instituicao_id",
                        row)

        # datasets, camadas, licenca, tag, pasta, arquivo
        for row in read_csv('nodes_licenca.csv', csv_dir):
            if dry_run:
                print('DRY RUN - Licenca', row.get('id'))
                continue
            session.run("MERGE (l:Licenca {id:$id}) SET l.nome=$nome, l.url=$url, l.codigo=$codigo", row)

        for row in read_csv('nodes_palavra_chave.csv', csv_dir):
            if dry_run:
                print('DRY RUN - Tag', row.get('id'))
                continue
            session.run("MERGE (t:Tag {id:$id}) SET t.tag=$tag", row)

        for row in read_csv('nodes_dataset.csv', csv_dir):
            if dry_run:
                print('DRY RUN - Dataset', row.get('id'))
                continue
            session.run("MERGE (d:Dataset {id:$id}) SET d.titulo=$titulo, d.descricao=$descricao, d.tema=$tema, d.cobertura_espacial=$cobertura_espacial, d.cobertura_temporal_inicio=$cobertura_temporal_inicio, d.cobertura_temporal_fim=$cobertura_temporal_fim, d.formato_principal=$formato_principal, d.srid=$srid, d.licenca_id=$licenca_id, d.projeto_id=$projeto_id", row)

        for row in read_csv('nodes_camada.csv', csv_dir):
            if dry_run:
                print('DRY RUN - Camada', row.get('id'))
                continue
            session.run("MERGE (c:Camada {id:$id}) SET c.nome=$nome, c.tipo=$tipo, c.srid=$srid, c.formato=$formato, c.url_publicacao=$url_publicacao, c.servico=$servico, c.projeto_id=$projeto_id, c.dataset_id=$dataset_id, c.estilo=$estilo", row)

        for row in read_csv('nodes_pasta.csv', csv_dir):
            if dry_run:
                print('DRY RUN - Pasta', row.get('id'))
                continue
            session.run("MERGE (p:Pasta {id:$id}) SET p.caminho=$caminho, p.nome=$nome, p.nivel=$nivel, p.pai_id=$pai_id, p.projeto_id=$projeto_id", row)

        for row in read_csv('nodes_arquivo.csv', csv_dir):
            if dry_run:
                print('DRY RUN - Arquivo', row.get('id'))
                continue
            session.run("MERGE (a:Arquivo {id:$id}) SET a.nome=$nome, a.extensao=$extensao, a.mime_type=$mime_type, a.tamanho_bytes=$tamanho_bytes, a.hash_sha256=$hash_sha256, a.versao=$versao, a.caminho=$caminho, a.data_criacao=$data_criacao, a.data_modificacao=$data_modificacao, a.tipo_documento=$tipo_documento, a.resumo=$resumo, a.projeto_id=$projeto_id, a.instituicao_id=$instituicao_id, a.pessoa_autor_id=$pessoa_autor_id", row)

def import_rels(driver, dry_run=False, csv_dir=None):
    with driver.session() as session:
        for row in read_csv('rels_arquivo_em_pasta.csv', csv_dir):
            if dry_run:
                print('DRY RUN - REL EM_PASTA', row)
                continue
            session.run("MATCH (a:Arquivo {id:$arquivo_id}), (p:Pasta {id:$pasta_id}) MERGE (a)-[:EM_PASTA]->(p)", row)

        for row in read_csv('rels_arquivo_refere_dataset.csv', csv_dir):
            if dry_run:
                print('DRY RUN - REL REFERE_DATASET', row)
                continue
            session.run("MATCH (a:Arquivo {id:$arquivo_id}), (d:Dataset {id:$dataset_id}) MERGE (a)-[:REFERE_DATASET]->(d)", row)

        for row in read_csv('rels_dataset_publicado_como_camada.csv', csv_dir):
            if dry_run:
                print('DRY RUN - REL PUBLICADO_COMO', row)
                continue
            session.run("MATCH (d:Dataset {id:$dataset_id}), (c:Camada {id:$camada_id}) MERGE (d)-[:PUBLICADO_COMO]->(c)", row)

        for row in read_csv('rels_arquivo_produzido_por_instituicao.csv', csv_dir):
            if dry_run:
                print('DRY RUN - REL PRODUZIDO_POR', row)
                continue
            session.run("MATCH (a:Arquivo {id:$arquivo_id}), (i:Instituicao {id:$instituicao_id}) MERGE (a)-[:PRODUZIDO_POR]->(i)", row)

        for row in read_csv('rels_arquivo_autor_pessoa.csv', csv_dir):
            if dry_run:
                print('DRY RUN - REL AUTOR', row)
                continue
            session.run("MATCH (a:Arquivo {id:$arquivo_id}), (ps:Pessoa {id:$pessoa_id}) MERGE (a)-[:AUTOR]->(ps)", row)

        for row in read_csv('rels_arquivo_tem_tag.csv', csv_dir):
            if dry_run:
                print('DRY RUN - REL TEM_TAG arquivo', row)
                continue
            session.run("MATCH (a:Arquivo {id:$arquivo_id}), (t:Tag {id:$tag_id}) MERGE (a)-[:TEM_TAG]->(t)", row)

        for row in read_csv('rels_dataset_tem_tag.csv', csv_dir):
            if dry_run:
                print('DRY RUN - REL TEM_TAG dataset', row)
                continue
            session.run("MATCH (d:Dataset {id:$dataset_id}), (t:Tag {id:$tag_id}) MERGE (d)-[:TEM_TAG]->(t)", row)

        for row in read_csv('rels_camada_tem_tag.csv', csv_dir):
            if dry_run:
                print('DRY RUN - REL TEM_TAG camada', row)
                continue
            session.run("MATCH (c:Camada {id:$camada_id}), (t:Tag {id:$tag_id}) MERGE (c)-[:TEM_TAG]->(t)", row)

        for row in read_csv('rels_dataset_licenciado_por.csv', csv_dir):
            if dry_run:
                print('DRY RUN - REL LICENCIADO_POR', row)
                continue
            session.run("MATCH (d:Dataset {id:$dataset_id}), (l:Licenca {id:$licenca_id}) MERGE (d)-[:LICENCIADO_POR]->(l)", row)

        for row in read_csv('rels_arquivo_precede_arquivo.csv', csv_dir):
            if dry_run:
                print('DRY RUN - REL PRECEDE', row)
                continue
            session.run("MATCH (a1:Arquivo {id:$arquivo_id_atual}), (a2:Arquivo {id:$arquivo_id_anterior}) MERGE (a1)-[:PRECEDE]->(a2)", row)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--uri', default='bolt://localhost:7687')
    p.add_argument('--user', default='neo4j')
    p.add_argument('--password', default='neo4j')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--csv-dir', default=None, help='Path to CSV directory')
    args = p.parse_args()

    csv_dir = resolve_csv_dir(args.csv_dir)
    if not csv_dir:
        raise SystemExit('CSV directory not found; provide --csv-dir')

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    try:
        import_nodes(driver, dry_run=args.dry_run, csv_dir=csv_dir)
        import_rels(driver, dry_run=args.dry_run, csv_dir=csv_dir)
    finally:
        driver.close()

if __name__ == '__main__':
    main()
