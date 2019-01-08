from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build
import json


class ComputeEngineClient:
    def __init__(self, project, zone):
        self.PROJECT = project
        self.ZONE = zone
        self.credentials = GoogleCredentials.get_application_default()
        self.service = build('compute', 'v1', credentials=self.credentials)

    def get_instance(self, instance):
        """Gets intance resource

        Arguments:
            instance {string} -- Name of the instance
        Returns:
            dict -- All the instance data
        """

        return self.service.instances().get(project=self.PROJECT, zone=self.ZONE, instance=instance).execute()

    def get_instance_fingerprint(self, instance):
        """Gets intance fingerprint

        Arguments:
            instance {string} -- Name of the instance
        Returns:
            string -- The instance current fingerprint
        """

        instance_data = self.get_instance(instance)
        return instance_data['metadata']['fingerprint']

    def set_instance_startup_script(self, instance, path):
        """Sets intance startup script

        Arguments:
            instance {string} -- Name of the instance
            path {string} -- Path to the startup script
        """

        fingerprint = self.get_instance_fingerprint(instance)
        print(f"fingerprint: {fingerprint}")
        script_file = ''
        with open(path, 'r') as ss:
            script_file = ss.read()

        body = {
            "kind": "compute#metadata",
            "fingerprint": fingerprint,
            "items": [
                {
                "key": "startup-script",
                "value": script_file
                }
            ]
        }
        self.service.instances().setMetadata(project=self.PROJECT, zone=self.ZONE, instance=instance, body=json.dumps(body)).execute()


    # -- [START] Managed instance group --
    def create_instance_template(self, name, image, acc_email, machine_type="n1-standard-1", sScript_url=""):
        """Creates a new Google Compute Engine template instance

        Arguments:
            name {string} -- Name of the template instance
            image {string} -- Name of the custom image to use
            acc_email {string} -- Service account email
            machine_type {string} -- GCE machine type to use (ex: "n1-standard-1")
            sScript_url {string} -- Url to get the startup script
        """

        body = {
            "name": name,
            "properties": {
                "machineType": machine_type,
                "networkInterfaces": [
                    {
                        "network": "https://www.googleapis.com/compute/v1/projects/" + self.PROJECT + "/global/networks/default",
                        "accessConfigs":
                        [
                            {
                                "name": "external-IP",
                                "type": "ONE_TO_ONE_NAT"
                            }
                        ]
                    }
                ],
                "disks":
                    [
                        {
                            "type": "PERSISTENT",
                            "boot": "true",
                            "mode": "READ_WRITE",
                            "initializeParams":
                                {
                                    "sourceImage": "global/images/" + image
                                }
                        }
                    ],
                "metadata": {
                    "kind": "compute#metadata",
                    "items": [
                      {
                        "key": "startup-script",
                        "value": sScript_url
                      },
                      {
                        "key": "service_account_scopes",
                        "value": "https://www.googleapis.com/auth/cloud-platform"
                      }
                    ]
                    },
                    "serviceAccounts": [
                        {
                            "email": acc_email,
                            "scopes": [
                                "https://www.googleapis.com/auth/devstorage.read_write",
                                "https://www.googleapis.com/auth/logging.write",
                                "https://www.googleapis.com/auth/taskqueue",
                                "https://www.googleapis.com/auth/cloud-taskqueue",
                                "https://www.googleapis.com/auth/cloud-platform",
                                "https://www.googleapis.com/auth/compute"
                            ]
                        }
                    ],
            }
        }

        return self.service.instanceTemplates().insert(project=self.PROJECT,
                                                       body=body).execute()

    def create_managed_instance_group(self, base_name, group_name, template_url, size=1):
        """Creates a Managed Instance Group

        Arguments:
            base_name {string} -- All instances in the group will have this preppended
            group_name {string} -- The name for the group
            template_url {string} -- Url of the template instance to use
            size {integer} -- Number of instances to initialize

        Returns:
            [type] -- [description]
        """

        body = {
            "baseInstanceName": base_name,
            "instanceTemplate": template_url,
            "name": group_name,
            "targetSize": size
        }

        return self.service.instanceGroupManagers().insert(project=self.PROJECT,
                                                           zone=self.ZONE,
                                                           body=body).execute()

    def create_cpu_autoscaler(self, group_name, group_url, max_replicas, cpu_percentage, cooldown):
        """Creates an Autoscaler policy based on CPU usage

        Arguments:
            group_name {string} -- Name of the managed instance group to target
            group_url {string} -- Url of the target group
            max_replicas {integer} -- Maximum number of instances to be up at max utilization
            cpu_percentage {float} -- Representing max CPU usage percentage to start new instances
            cooldown {integer} -- Number of seconds to wait before collecting usage data again
        """

        body = {
            "name": group_name,
            "target": group_url,
            "autoscalingPolicy": {
                "maxNumReplicas": max_replicas,
                "cpuUtilization": {
                    "utilizationTarget": cpu_percentage
                },
                "coolDownPeriodSec": cooldown
            }
        }

        return self.service.autoscalers().insert(project=self.PROJECT,
                                                 zone=self.ZONE,
                                                 body=body).execute()

    # -- [END] Managed instance group --
