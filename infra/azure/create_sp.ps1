param(
    [string]$Name = "sigma-pli-tf-sp",
    [string]$Role = "Contributor",
    [string]$Scope = "/subscriptions/$(az account show --query id -o tsv)"
)

# Create a service principal and output credentials for Terraform
$sp = az ad sp create-for-rbac --name $Name --role $Role --scopes $Scope --sdk-auth | ConvertFrom-Json

Write-Host "Service Principal criado. Exporte as variáveis abaixo para uso no Terraform:"
Write-Host "CLIENT_ID=$($sp.clientId)"
Write-Host "CLIENT_SECRET=$($sp.clientSecret)"
Write-Host "TENANT_ID=$($sp.tenantId)"
Write-Host "SUBSCRIPTION_ID=$(az account show --query id -o tsv)"
