import os
import yaml

def yaml_to_tf(yaml_path, tf_directory):
    # Load YAML file
    with open(yaml_path, 'r') as f:
        yaml_data = yaml.safe_load(f)

    # Extract relevant fields from YAML data
    name = yaml_data['metadata']['name']
    image = yaml_data['spec']['template']['spec']['containers'][0]['image']
    container_port = yaml_data['spec']['template']['spec']['containers'][0]['ports'][0]['containerPort']
    cpu_limit = yaml_data['spec']['template']['spec']['containers'][0]['resources']['limits']['cpu']
    memory_limit = yaml_data['spec']['template']['spec']['containers'][0]['resources']['limits']['memory']
    service_account = yaml_data['spec']['template']['spec']['serviceAccountName']

    # Generate Terraform configuration
    tf_config = f'''
# Define Cloud Run service
resource "google_cloud_run_v2_service" "{name}" {{
  name     = "{name}"
  location = "europe-west1" # Same location as specified in the YAML

  template {{
    spec {{
      containers {{
        image = "{image}" # Same image reference as specified in the YAML
        ports {{
          container_port = {container_port}
          name           = "http1"
        }}
        resources {{
          limits = {{
            cpu    = "{cpu_limit}"
            memory = "{memory_limit}"
          }}
        }}
        startup_probe {{
          failure_threshold = 1
          period_seconds   = 240
          tcp_socket {{
            port = {container_port}
          }}
          timeout_seconds = 240
        }}
      }}
      service_account_name = "{service_account}"
      timeout_seconds      = 300
    }}
  }}
}}
'''

    # Write Terraform configuration to a file in the specified directory
    tf_file = os.path.join(tf_directory, f"{name}.tf")
    with open(tf_file, 'w') as f:
        f.write(tf_config)

    print(f"Terraform configuration generated for {name} service in {tf_file}.")

# Path to directory containing YAML files
yaml_directory = "/yaml_files/"

# Path to directory to save TF files
tf_directory = "/tf_file"

# Iterate over YAML files in the directory
for filename in os.listdir(yaml_directory):
    if filename.endswith(".yaml") or filename.endswith(".yml"):
        yaml_path = os.path.join(yaml_directory, filename)
        yaml_to_tf(yaml_path, tf_directory)
