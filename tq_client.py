import logging
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials


class TaskqueueClient:
    def __init__(self, project, taskqueue):

        self.PROJECT = project
        self.TASKQUEUE = taskqueue

        # Get default credentials for the current project
        # - Other posible auth method is using oauth2cleint.gce
        #   AppAssertionCredentials as described in:
        #   https://developers.google.com/identity/protocols/OAuth2ServiceAccount
        self.credentials = GoogleCredentials.get_application_default()

        # Initialize API client
        self.service = build('taskqueue', 'v1beta2',
                             credentials=self.credentials)

    def get_taskqueue(self):
        result = self.service.taskqueues().get(project=self.PROJECT,
                                               taskqueue=self.TASKQUEUE
                                               ).execute()

        return result

    def list_tasks(self):
        tasks_list = self.service.tasks().list(project=self.PROJECT,
                                               taskqueue=self.TASKQUEUE
                                               ).execute()

        return tasks_list

    def create_task(self, payload):
        body = {
            "kind": "taskqueue#task",
            "queueName": self.TASKQUEUE,
            "payloadBase64": payload
        }

        return self.service.tasks().insert(project=self.PROJECT,
                                           taskqueue=self.TASKQUEUE,
                                           body=body).execute()

    def get_task(self, task_name):
        t = self.service.tasks().get(
            project=self.PROJECT, taskqueue=self.TASKQUEUE,
            task=task_name)

        return t.execute()

    def lease_task(self, numTasks, leaseSecs):
        result = self.service.tasks().lease(project=self.PROJECT,
                                            taskqueue=self.TASKQUEUE,
                                            numTasks=numTasks,
                                            leaseSecs=leaseSecs
                                            ).execute()
        return result

    def delete_task(self, task):
        result = self.service.tasks().delete(project="s~" + self.PROJECT,
                                             taskqueue=self.TASKQUEUE,
                                             task=task
                                             ).execute()
        return result


def run(project, zone, instance_name, action):
    pass


def main():
    use_defaults = raw_input("Use dafult values? (Y/N): ")

    if use_defaults == "N":
        project = raw_input("Please enter the project ID: ")
        taskqueue_name = raw_input("Please enter the taskqueue name: ")

        action = raw_input("Enter action to perform ('list', 'delete'): ")

        run(project, taskqueue_name, action)

    elif use_defaults == "Y":
        action = raw_input("Enter action to perform ('list', 'delete'): ")

        project = "juusto-testing"
        taskqueue_name = "documentation-compiler-queue"

        run(project, taskqueue_name, action)

if __name__ == '__main__':
    main()
