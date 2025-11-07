terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# PostgreSQL Flexible Server
# Neo4j will run in Azure Container Instance as a simple option (not production grade)
resource "azurerm_container_group" "neo4j" {
  name                = var.neo4j_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"

  container {
    name   = "neo4j"
    image  = "neo4j:5"
    cpu    = "1"
    memory = "2"

    ports {
      port     = 7474
      protocol = "TCP"
    }
    ports {
      port     = 7687
      protocol = "TCP"
    }

    environment_variables = {
      NEO4J_AUTH = "neo4j/${var.neo4j_password}"
    }
  }

  ip_address_type = "Public"
  dns_name_label  = lower(var.neo4j_name)
}
