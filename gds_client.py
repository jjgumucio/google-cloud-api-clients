from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build


class DatastoreClient:
    def __init__(self):
        self.credentials = GoogleCredentials.get_application_default()
        self.service = build("datastore", "v1beta2",
                             credentials=self.credentials)

    def beginTransaction(self, datasetId, isolationLevel="snapshot"):
        """Begin a new transaction

        Arguments:
            datasetId {str} -- Identifies the dataset
            isolationLevel {str} -- The transaction isolation level
                                    (snapshot/serializable)

        Returns:
            dict -- Containing header and transaction identifier
        """
        body = {
            "isolationLevel": isolationLevel
        }

        return self.service.datasets.beginTransaction(datasetId=datasetId,
                                                      body=body).execute()

    def commit(self, datasetId, trasactionId, mutation):
        """Commit a transaction, optionally creating, deleting or modifying
            some entities.

        Arguments:
            datasetId {str} -- Identifies the dataset
            transactionId {str} -- Id returned from a call to beginTransaction
            mutation {dict} -- A set of changes to apply

            ref: https://developers.google.com/resources/api-libraries/documentation/datastore/v1beta2/python/latest/datastore_v1beta2.datasets.html#commit
        """

        body = {
            "ignoreReadOnly": "True",
            "trasaction": trasactionId,
            "mode": "TRASACTIONAL",
            "mutation": mutation
        }

        return self.service.datasets().commit(
            datasetId=datasetId, body=body).execute()
