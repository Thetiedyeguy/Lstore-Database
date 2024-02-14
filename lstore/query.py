from table import Table, Record
from index import Index
from datetime import datetime
from config import *

class Query:
    """
    # Creates a Query object that can perform different queries on the specified table 
    Queries that fail must return False
    Queries that succeed should return the result or True
    Any query that crashes (due to exceptions) should return False
    """
    def __init__(self, table):
        self.table = table
        pass

    
    """
    # internal Method
    # Read a record with specified RID
    # Returns True upon succesful deletion
    # Return False if record doesn't exist or is locked due to 2PL
    """
    def delete(self, primary_key):
        if primary_key not in self.table.page_directory or primary_key is None:
            return False
        base_address = self.table.page_directory[primary_key]
        self.table.update_value(self.table.RID_COLUMN, base_address, None)
        return True
    
    
    """
    # Insert a record with specified columns
    # Return True upon succesful insertion
    # Returns False if insert fails for whatever reason
    """
    def insert(self, *columns):

        #Check if key exists, if it doesnt then return false
        if self.insert_helper_record_exists(columns[self.table.key]):
            return False

        #Obtain Info for meta_data
        rid = self.insert_helper_generate_rid()
        indirection = 2**64 - 1
        time = datetime.now().strftime("%Y%m%d%H%M%S")
        schema_encoding = '0' * self.table.num_columns 
        schema_encoding = int(schema_encoding)

        meta_data = [indirection, rid, int(time), schema_encoding]
        #new_record = Record(rid, columns[self.table.key], columns)
        columns = list(columns)
        meta_data.extend(columns)

        self.table.base_write(meta_data)
        return True

    #Helper function: retrieves number of records current exist, +1 to obtain new rid
    def insert_helper_generate_rid(self):
        rid = self.table.records + 1
        return rid
    
    def insert_helper_record_exists(self, key):
        key_index = self.table.index
        locations = key_index.locate(self.table.key, key)
        return len(locations) > 0
    
    def select(self, search_key, search_key_index, projected_columns_index):

        # search_key: the value you want to search based on
        # search_key_index: the column index you want to search based on
        # projected_columns_index: what columns to return. array of 1 or 0 values
        
        output = []
        matchingRIDs = []

        matchingRIDs = table.get_rid(search_key_index, search_key)
    
        for eachRID in matchingRIDs:
            for eachColumn in projected_columns_index:
                if eachColumn == 1: output.append(table.get_record(eachRID))
    
        return output
        # we may assume that select will never be called on a key that doesn't exist
    
    """
    # Read matching record with specified search key
    # :param search_key: the value you want to search based on
    # :param search_key_index: the column index you want to search based on
    # :param projected_columns_index: what columns to return. array of 1 or 0 values.
    # :param relative_version: the relative version of the record you need to retreive.
    # Returns a list of Record objects upon success
    # Returns False if record locked by TPL
    # Assume that select will never be called on a key that doesn't exist
    """
    def select_version(self, search_key, search_key_index, projected_columns_index, relative_version):
        pass

    
    """
    # Update a record with specified key and columns
    # Returns True if update is succesful
    # Returns False if no records exist with given key or if the target record cannot be accessed due to 2PL locking
    """
    def update(self, primary_key, *columns):
        columnList = list(columns)
        rid = self.table.index.locate(self.table.key, primary_key)
        if rid not in self.table.page_directory or rid is None: 
            return False
        base_record = self.table.get_record(rid)
        base_indirection = base_record[self.table.INDIRECTION_COLUMN]


        #information for metadata
        time = datetime.now().strftime("%Y%m%d%H%M%S")
        new_tail_rid = self.table.num_records
        new_tail_encoding = ''
        new_tail_indirection = None

        #non cumulative tail record encoding
        for i, val in enumerate(columnList):
            if columnList[i] == None:
                new_tail_encoding += '0'
            else:
                new_tail_encoding += '1'

        #set indirection to base record or last tail record
        if base_indirection == None:
            new_tail_indirection = rid
        else:
            last_tail = self.table.get_record(base_indirection)
            new_tail_indirection =  last_tail[self.table.RID_COLUMN]

        meta_data = [new_tail_indirection, new_tail_rid, int(time), new_tail_encoding]
        meta_data.extend(columnList)
        self.table.tail_write(meta_data)

        #change base encoding if needed
        base_encoding = base_record[self.table.SCHEMA_ENCODING_COLUMN]
        new_base_encoding = base_encoding or new_tail_encoding

        base_address = self.table.page_directory[rid]
        self.table.update_value(self.table.INDIRECTION_COLUMN, base_address, new_tail_rid)
        self.table.update_value(self.table.SCHEMA_ENCODING_COLUMN, base_address, new_base_encoding)

        return True
    
    """
    :param start_range: int         # Start of the key range to aggregate 
    :param end_range: int           # End of the key range to aggregate 
    :param aggregate_columns: int  # Index of desired column to aggregate
    # this function is only called on the primary key.
    # Returns the summation of the given range upon success
    # Returns False if no record exists in the given range
    """
    def sum(self, start_range, end_range, aggregate_column_index):
        total_sum = 0;
        column_index = aggregate_column_index + METADATA
        for key in range(start_range, end_range + 1):
            if key in self.table.key_to_rid.keys():
                rid = self.table.key_to_rid[key]
                record = self.table.get_record(rid)
                # Record can be updated or never updated
                # Record was updated (has tail pages)
                if record[INDIRECTION_COLUMN] != None:
                    tail_rid = record[INDIRECTION_COLUMN]
                    record = self.table.get_record(tail_rid)
                total_sum += record[column_index]
            else:
                # Returns False if no record exists in the given range
                return False
        # Returns the summation of the given range upon success
        return total_sum

    
    """
    :param start_range: int         # Start of the key range to aggregate 
    :param end_range: int           # End of the key range to aggregate 
    :param aggregate_columns: int  # Index of desired column to aggregate
    :param relative_version: the relative version of the record you need to retreive.
    # this function is only called on the primary key.
    # Returns the summation of the given range upon success
    # Returns False if no record exists in the given range
    """
    def sum_version(self, start_range, end_range, aggregate_column_index, relative_version):
        pass

    
    """
    incremenets one column of the record
    this implementation should work if your select and update queries already work
    :param key: the primary of key of the record to increment
    :param column: the column to increment
    # Returns True is increment is successful
    # Returns False if no record matches key or if target record is locked by 2PL.
    """
    def increment(self, key, column):
        r = self.select(key, self.table.key, [1] * self.table.num_columns)[0]
        if r is not False:
            updated_columns = [None] * self.table.num_columns
            updated_columns[column] = r[column] + 1
            u = self.update(key, *updated_columns)
            return u
        return False
