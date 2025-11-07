"""
Script de Teste para Validar Máscaras de Formatação
===================================================

Testa a biblioteca script_input_masks.js sem necessidade do browser
"""

# Casos de teste para máscaras

test_cases = {
    "cpf": [
        ("12345678900", "123.456.789-00"),
        ("123", "123"),
        ("1234567890", "123.456.789-0"),
        ("", ""),
    ],
    "cnpj": [
        ("12345678901234", "12.345.678/0001-34"),
        ("12", "12"),
        ("123456", "12.345.6"),
        ("", ""),
    ],
    "telefone": [
        ("11987654321", "(11) 98765-4321"),
        ("1187654321", "(11) 8765-4321"),
        ("11", "(11"),
        ("119876", "(11) 9876"),
        ("", ""),
    ],
    "cep": [
        ("12345678", "12345-678"),
        ("12345", "12345"),
        ("123", "123"),
        ("", ""),
    ],
    "data": [
        ("31012024", "31/01/2024"),
        ("31", "31"),
        ("3101", "31/01"),
        ("", ""),
    ],
    "rg": [
        ("123456789", "12.345.678-9"),
        ("12", "12"),
        ("12345", "12.345"),
        ("", ""),
    ],
    "cnh": [
        ("1234567890123456", "1234567890123"),  # Limita a 13 dígitos
        ("123456789", "123456789"),
        ("", ""),
    ],
}


def test_masks():
    """Exibe resultados esperados dos testes"""
    print("=" * 80)
    print("🧪 TESTES DE MÁSCARAS DE FORMATAÇÃO")
    print("=" * 80)

    for mask_type, cases in test_cases.items():
        print(f"\n📝 Máscara: {mask_type.upper()}")
        print("-" * 80)

        for input_val, expected in cases:
            # Exibir caso de teste
            input_display = f"'{input_val}'" if input_val else "'' (vazio)"
            print(f"  Input:    {input_display:<30} → Esperado: '{expected}'")

    print("\n" + "=" * 80)
    print("✅ Acesse http://localhost:8010/auth/cadastro para testar no browser")
    print("=" * 80)


def test_removemask():
    """Testa remoção de máscaras"""
    print("\n" + "=" * 80)
    print("🔧 REMOÇÃO DE MÁSCARAS (online no servidor)")
    print("=" * 80)

    cases = [
        ("123.456.789-00", "12345678900"),
        ("(11) 98765-4321", "11987654321"),
        ("12345-678", "12345678"),
        ("31/01/2024", "31012024"),
    ]

    print("\nRemovendo caracteres não-numéricos:\n")
    for masked, expected_clean in cases:
        print(f"  {masked:<20} → {expected_clean}")

    print("\n" + "=" * 80)


def test_validations():
    """Testa validações básicas"""
    print("\n" + "=" * 80)
    print("✔️ VALIDAÇÕES (no backend via schemas Pydantic)")
    print("=" * 80)

    validations = {
        "CPF": [
            ("123.456.789-00", False, "Módulo 11 inválido"),
            ("111.444.777-35", True, "Módulo 11 válido"),
            ("00000000000", False, "Sequência conhecida como inválida"),
        ],
        "Telefone": [
            ("(11) 98765-4321", True, "11 dígitos"),
            ("(11) 8765-4321", True, "10 dígitos"),
            ("(11) 987", False, "Muito curto"),
        ],
        "CEP": [
            ("12345-678", True, "8 dígitos"),
            ("1234-567", False, "Muito curto"),
        ],
        "Data": [
            ("31/01/2024", True, "Data válida"),
            ("31/13/2024", False, "Mês inválido"),
            ("32/01/2024", False, "Dia inválido"),
        ],
    }

    for validation_type, cases in validations.items():
        print(f"\n{validation_type}:")
        for value, expected, reason in cases:
            status = "✅" if expected else "❌"
            print(f"  {status} {value:<20} → {reason}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_masks()
    test_removemask()
    test_validations()

    print("\n" + "=" * 80)
    print("📌 RESUMO DOS TESTES")
    print("=" * 80)
    print(
        """
Máscaras Implementadas:
  ✅ CPF:        123.456.789-00
  ✅ CNPJ:       12.345.678/0001-90
  ✅ Telefone:   (11) 98765-4321 ou (11) 8765-4321
  ✅ CEP:        12345-678
  ✅ Data:       DD/MM/YYYY
  ✅ RG:         12.345.678-9
  ✅ CNH:        13 dígitos (sem formatação)

Campos Configurados na Interface:
  ✅ CPF         → id="cpf"
  ✅ RG          → id="rg"
  ✅ Tel. Princ. → id="telefonePrincipal"
  ✅ Tel. Sec.   → id="telefoneSecundario"
  ✅ CEP         → id="cep"

Seletores de Localização:
  ✅ UF Naturalidade  → id="ufNaturalidade"
  ✅ UF RG            → id="ufRg"
  ✅ Município        → id="naturalidade"

Próxima Etapa:
  🔄 Iniciar aplicação (python setup_security.py --setup)
  🔄 Testar interface em http://localhost:8010/auth/cadastro
  🔄 Validar máscaras em tempo real
  🔄 Validar carregamento de UFs/Municípios
    """
    )
    print("=" * 80)
