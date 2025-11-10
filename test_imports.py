"""Script para testar se todas as dependências podem ser importadas"""
import sys

print("🔍 Testando imports das dependências...\n")

dependencies = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("pydantic", "Pydantic"),
    ("pydantic_settings", "Pydantic Settings"),
    ("asyncpg", "AsyncPG"),
    ("jinja2", "Jinja2"),
    ("aiofiles", "AIOFiles"),
    ("aiohttp", "AIOHTTP"),
    ("email_validator", "Email Validator"),
    ("passlib", "Passlib"),
    ("jose", "Python-JOSE"),
    ("neo4j", "Neo4j"),
    ("openpyxl", "OpenPyXL"),
]

failed = []
success = []

for module, name in dependencies:
    try:
        __import__(module)
        print(f"✅ {name:20} - OK")
        success.append(name)
    except ImportError as e:
        print(f"❌ {name:20} - FALTANDO")
        failed.append((name, str(e)))

print(f"\n{'='*50}")
print(f"✅ Sucesso: {len(success)}/{len(dependencies)}")
print(f"❌ Falhas: {len(failed)}/{len(dependencies)}")

if failed:
    print(f"\n❌ Dependências faltando:")
    for name, error in failed:
        print(f"   - {name}")
    sys.exit(1)
else:
    print(f"\n🎉 Todas as dependências estão OK!")
    sys.exit(0)
