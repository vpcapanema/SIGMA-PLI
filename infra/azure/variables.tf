variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "sigma-pli-rg"
}

variable "location" {
  description = "Azure location"
  type        = string
  default     = "eastus"
}

variable "neo4j_name" {
  description = "Neo4j container DNS name label"
  type        = string
  default     = "sigma-pli-neo4j"
}

variable "neo4j_password" {
  description = "Neo4j initial password"
  type        = string
  default     = "ChangeMe123!"
}
