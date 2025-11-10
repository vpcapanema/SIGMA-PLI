"""Verifica todos os imports usados no código"""
import os
import re

print("🔍 Procurando todos os imports no código...\n")

imports = set()

def extract_imports(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Encontrar imports
            for match in re.finditer(r'^(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE):
                module = match.group(1)
                # Ignorar imports locais (app.*) e stdlib
                if not module.startswith('app') and module not in ['os', 'sys', 're', 'json', 'datetime', 'typing', 'pathlib', 'asyncio', 'collections']:
                    imports.add(module)
    except Exception as e:
        pass

# Procurar em app/
for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            extract_imports(os.path.join(root, file))

print("📦 Módulos de terceiros encontrados:")
for imp in sorted(imports):
    print(f"   - {imp}")

print(f"\nTotal: {len(imports)} módulos")
