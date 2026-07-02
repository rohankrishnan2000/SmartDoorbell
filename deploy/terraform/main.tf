terraform {
  required_version = ">= 1.6.0"
}

variable "project_name" {
  type    = string
  default = "sentinel-doorbell-ai"
}

resource "null_resource" "architecture_placeholder" {
  triggers = {
    project = var.project_name
    plan    = "registry-postgres-object-storage-kubernetes-observability"
  }
}

output "intended_topology" {
  value = {
    registry      = "container images for api/dashboard/edge"
    database      = "managed postgres"
    media_storage = "object storage bucket for event clips"
    compute       = "kubernetes or edge fleet"
    observability = "prometheus/grafana/log aggregation"
  }
}

