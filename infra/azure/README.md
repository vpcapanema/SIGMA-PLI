Azure IaC scaffold (Terraform)

Passos resumidos:

1. Instale Azure CLI e Terraform.
2. Faça login: `az login`.

3. Crie um service principal para o Terraform (exemplo de script disponível em `create_sp.ps1`).

4. Observação: seu PostgreSQL está na AWS — este scaffold **não** cria PostgreSQL na Azure. O Terraform criado aqui provisiona apenas o Neo4j (Azure Container Instance) e o Resource Group.

5. Exporte variáveis de ambiente retornadas pelo script (CLIENT_ID, CLIENT_SECRET, TENANT_ID, SUBSCRIPTION_ID).
6. Ajuste senhas em `variables.tf` ou forneça via `terraform.tfvars`.
7. Inicialize e aplique:

```powershell
cd infra\azure
terraform init
terraform apply
```

Aviso: este scaffold cria recursos com custos associados. Revise e ajuste antes de aplicar.
