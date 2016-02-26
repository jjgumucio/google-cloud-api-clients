from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build


class DatastoreClient:
    def __init__(self):
        self.credentials = GoogleCredentials.get_application_default()
        self.service = build("datastore", "v1beta2",
                             credentials=self.credentials)

    def beginTransaction(self, datasetId, isolationLevel):
        """Begin a new transaction

        Arguments:
            datasetId {str} -- Identifies the dataset
            isolationLevel {str} -- The transaction isolation level
                                    (snapshot/serializable)

        Returns:
            dict -- Containing header and transaction identifier
        """
        body = {
            "isolationLevel": "snapshot"
        }

        return self.service.datasets.beginTransaction(datasetId=datasetId,
                                                      body=body).execute()

    def commit(self, datasetId, action):
        """Commit a transaction, optionally creating, deleting or modifying
            some entities.

        Arguments:
            datasetId {str} -- Identifies the dataset
            action {str} -- Action to take (insert, update, delete, upsert)
        """

        body = {

        }

        return self.service.datasets().commit(
            datasetId=datasetId, body=body).execute()
