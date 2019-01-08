import argparse
import subprocess
import json
from gce_client import ComputeEngineClient

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", required=True, type=str,
                        help="Google Cloud project name")
    parser.add_argument("-z", "--zone", required=True, type=str,
                        help="Zone where the instance is located")
    parser.add_argument("-i", "--instance", required=True, type=str,
                        help="Instance name")
    args = parser.parse_args()

    # subprocess.call(["gcloud", "auth", "application-default", "login"])

    compute = ComputeEngineClient(args.project, args.zone)
    compute.set_instance_startup_script(args.instance, './setup-script.sh')

if __name__ == "__main__":
    main()
