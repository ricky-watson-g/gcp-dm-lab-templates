variable "instance_name" {
    default = "vm_instance"
}
variable "instance_zone" {
    default = "us-central1-f"
}
variable "instance_type" {
  default = "n1-standard-1"
  }

resource "google_compute_instance" "vm_instance" {
  name         = "${var.instance_name}"
  zone         = "${var.instance_zone}"
  machine_type = "${var.instance_type}"
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
      }
  }
  network_interface {
    network = "default"
    access_config {
    }
  }
}