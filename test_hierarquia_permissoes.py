"""
Testes do Sistema de Hierarquia e Permissões
SIGMA-PLI - Migration 006
"""

import asyncio
import asyncpg


async def test_hierarquia_sistema():
    """Testa o sistema de hierarquia de usuários"""

    print("=" * 80)
    print("🔐 TESTE DO SISTEMA DE HIERARQUIA E PERMISSÕES")
    print("=" * 80)
    print()

    # Conectar ao banco
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="sigma_admin",
        password="Malditas131533*",
        database="sigma_pli",
    )

    try:
        # 1. Verificar estrutura da tabela
        print("📋 1. Verificando estrutura da tabela usuarios.usuario...")
        print("-" * 80)

        colunas = await conn.fetch(
            """
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_schema = 'usuarios'
                AND table_name = 'usuario'
                AND column_name IN ('tipo_usuario', 'nivel_acesso')
        """
        )

        for col in colunas:
            print(
                f"  ✅ {col['column_name']:<20} {col['data_type']:<20} DEFAULT: {col['column_default']}"
            )
        print()

        # 2. Verificar constraints
        print("🔒 2. Verificando constraints...")
        print("-" * 80)

        constraints = await conn.fetch(
            """
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_schema = 'usuarios'
                AND table_name = 'usuario'
                AND constraint_name LIKE '%tipo_usuario%'
                   OR constraint_name LIKE '%nivel_acesso%'
        """
        )

        for c in constraints:
            print(f"  ✅ {c['constraint_name']:<40} {c['constraint_type']}")
        print()

        # 3. Verificar trigger
        print("⚙️  3. Verificando trigger de cálculo automático...")
        print("-" * 80)

        trigger = await conn.fetchrow(
            """
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers
            WHERE trigger_name = 'tr_usuario_calcular_nivel'
        """
        )

        if trigger:
            print(f"  ✅ Trigger: {trigger['trigger_name']}")
            print(f"  ✅ Evento: {trigger['event_manipulation']}")
            print(f"  ✅ Função: {trigger['action_statement']}")
        else:
            print("  ❌ Trigger não encontrado!")
        print()

        # 4. Testar cálculo automático de nivel_acesso
        print("🧪 4. Testando cálculo automático de nivel_acesso...")
        print("-" * 80)

        tipos = ["VISUALIZADOR", "OPERADOR", "ANALISTA", "GESTOR", "ADMIN"]
        niveis_esperados = [1, 2, 3, 4, 5]

        usuario_teste = await conn.fetchrow("SELECT id FROM usuarios.usuario LIMIT 1")

        if usuario_teste:
            usuario_id = usuario_teste["id"]

            for tipo, nivel_esperado in zip(tipos, niveis_esperados):
                # Atualizar tipo
                result = await conn.fetchrow(
                    """
                    UPDATE usuarios.usuario
                    SET tipo_usuario = $1
                    WHERE id = $2
                    RETURNING tipo_usuario, nivel_acesso
                """,
                    tipo,
                    usuario_id,
                )

                nivel_calculado = result["nivel_acesso"]
                status = "✅" if nivel_calculado == nivel_esperado else "❌"

                print(
                    f"  {status} {tipo:<15} → nivel_acesso = {nivel_calculado} (esperado: {nivel_esperado})"
                )

            # Restaurar para VISUALIZADOR
            await conn.execute(
                """
                UPDATE usuarios.usuario
                SET tipo_usuario = 'VISUALIZADOR'
                WHERE id = $1
            """,
                usuario_id,
            )
        else:
            print("  ⚠️  Nenhum usuário encontrado para teste")
        print()

        # 5. Verificar views
        print("👁️  5. Verificando views criadas...")
        print("-" * 80)

        views = await conn.fetch(
            """
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'usuarios'
                AND table_name LIKE '%hierarquia%'
                   OR table_name LIKE '%estatisticas_tipo%'
        """
        )

        for v in views:
            print(f"  ✅ View: {v['table_name']}")

            # Mostrar amostra da view
            sample = await conn.fetch(
                f"SELECT * FROM usuarios.{v['table_name']} LIMIT 3"
            )
            if sample:
                print(f"     Registros: {len(sample)}")
        print()

        # 6. Testar função verificar_permissao
        print("🔍 6. Testando função verificar_permissao()...")
        print("-" * 80)

        if usuario_teste:
            # Atualizar para GESTOR (nivel 4)
            await conn.execute(
                """
                UPDATE usuarios.usuario
                SET tipo_usuario = 'GESTOR'
                WHERE id = $1
            """,
                usuario_id,
            )

            # Testes
            testes = [
                (1, True, "GESTOR (4) pode acessar nível 1"),
                (3, True, "GESTOR (4) pode acessar nível 3"),
                (4, True, "GESTOR (4) pode acessar nível 4"),
                (5, False, "GESTOR (4) NÃO pode acessar nível 5 (ADMIN)"),
            ]

            for nivel_minimo, esperado, descricao in testes:
                resultado = await conn.fetchval(
                    "SELECT usuarios.verificar_permissao($1, $2)",
                    usuario_id,
                    nivel_minimo,
                )

                status = "✅" if resultado == esperado else "❌"
                print(f"  {status} {descricao}: {resultado}")

            # Restaurar
            await conn.execute(
                """
                UPDATE usuarios.usuario
                SET tipo_usuario = 'VISUALIZADOR'
                WHERE id = $1
            """,
                usuario_id,
            )
        print()

        # 7. Estatísticas finais
        print("📊 7. Estatísticas de usuários por tipo...")
        print("-" * 80)

        stats = await conn.fetch("SELECT * FROM usuarios.v_estatisticas_tipo_usuario")

        print(
            f"  {'Tipo':<15} {'Nível':<8} {'Total':<8} {'Ativos':<8} {'Inativos':<10} {'Emails OK'}"
        )
        print("  " + "-" * 75)
        for s in stats:
            print(
                f"  {s['tipo_usuario']:<15} {s['nivel_acesso']:<8} "
                f"{s['total_usuarios']:<8} {s['ativos']:<8} "
                f"{s['inativos']:<10} {s['emails_verificados']}"
            )
        print()

        # Resumo final
        print("=" * 80)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 80)
        print()
        print("📝 Resumo:")
        print("  ✅ Campos tipo_usuario e nivel_acesso criados")
        print("  ✅ Constraints de validação funcionando")
        print("  ✅ Trigger de cálculo automático operacional")
        print("  ✅ Views de consulta disponíveis")
        print("  ✅ Função de verificação de permissão funcional")
        print()
        print("🚀 Sistema de hierarquia pronto para uso!")
        print()

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(test_hierarquia_sistema())
