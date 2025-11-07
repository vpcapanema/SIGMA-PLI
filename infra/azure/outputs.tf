output "resource_group" {
  value = azurerm_resource_group.rg.name
}

output "neo4j_fqdn" {
  value = azurerm_container_group.neo4j.fqdn
}
