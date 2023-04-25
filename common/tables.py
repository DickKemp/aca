from azure.data.tables import TableClient, TableTransactionError
from azure.core.exceptions import ResourceExistsError


def divide_range_into_chunks(total_len, chunksize):
    for b,e in [(x,x+chunksize) for x in range(0, total_len, chunksize)]:
        yield (b, e if e < total_len else total_len+1)

class EntityStore():
    connection_string = None

    @staticmethod
    def initialize(connection_string):
        EntityStore.connection_string = connection_string

    def __init__(self, table_name:str):
        if not self.connection_string:
            raise Exception("Table connection creds null")
        self.table_client = TableClient.from_connection_string(conn_str=EntityStore.connection_string, table_name=table_name)
        try:
            self.table_client.create_table()
            print("Created table")
        except ResourceExistsError:
            print("Table already exists")

    def insert(self, id, partition, vals):
        keys = {"PartitionKey": partition, "RowKey": id}
        entity = {**keys, **vals}
        self.table_client.create_entity(entity)

    def upsert(self, id, partition, vals):
        keys = {"PartitionKey": partition, "RowKey": id}
        entity = {**keys, **vals}
        self.table_client.upsert_entity(entity)

    def query(self, partition, filter=None):
        if filter:
            result = self.table_client.query_entities(query_filter=f"PartitionKey eq @pk and {filter}", parameters={"pk": partition})
        else:
            result = self.table_client.query_entities(query_filter="PartitionKey eq @pk", parameters={"pk": partition})            
        return result
    
    def delete(self, partition, filter=None):
        results = self.query(partition, filter)
        to_delete = []
        try:
            for item in results:
                to_delete.append({"PartitionKey": partition, "RowKey": item['RowKey']})
            self.batch_delete(to_delete)
            return '', 204
        except:
            print("error during delete")
        return '', 404

    def batch_delete(self, entities):
        return self.batch_operation("delete", entities)

    def batch_insert(self, entities):
        return self.batch_operation("upsert", entities)
    
    def batch_operation(self, op, entities):        
        CHUNK_SIZE=50
        elen = len(entities)
        # break up the potentially long list of entities into chunks
        for start,end in divide_range_into_chunks(elen, CHUNK_SIZE):
            operations = [ (op, e) for e in entities[start:end] ]
            try:
                self.table_client.submit_transaction(operations)
            except TableTransactionError as e:
                print("There was an error with the transaction operation")
                print(e)
