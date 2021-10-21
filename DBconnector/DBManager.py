import psycopg2

class dbcon():
    def __init__(self) -> None:
        self.host = '192.168.0.8'
        self.dbname = 'WarCats'
        self.user = 'postgres'
        self.password = '5042'
        self.port = 5432
        self.options = '-c search_path=dbo,kiwoom'

        self.db = psycopg2.connect(host=self.host, dbname=self.dbname,user=self.user,
        password=self.password, port=self.port, options=self.options)
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()
        self.cursor.close()

    def execute(self, query, args={}):
        self.cursor.execute(query, args)
        # row = self.cursor.fetchall()
        # return row

    def commit(self):
        self.db.commit()    

    def insertDB(self, schema, table, column, data):
        sql = 'INSERT INTO {schema}.{table} ({column}) VALUES ({data});'\
            .format(schema=schema, table=table, column=column, data=data)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print('Insert DB ', e)

    def selectDB(self, schema, table, column, condition):
        sql = 'SELECT {schema} FROM {table}.{column} WHERE {condition} ; '\
            .format(column=column,schema=schema,table=table, condition=condition)
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e :
            result = (" Read DB err",e)
        return result

    def updateDB(self,schema,table,column,value,condition):
        sql = " UPDATE {schema}.{table} SET {colum}='{value}' WHERE {colum}='{condition}';"\
            .format(schema=schema, table=table , column=column, value=value, condition=condition )
        try :
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e :
            print(" Update DB err",e)

    def deleteDB(self,schema,table,condition):
        sql = " DELETE FROM {schema}.{table} WHERE {condition} ; ".format(schema=schema,table=table,
        condition=condition)
        try :
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print( "Delete DB err", e)

    # def insertUpdate(self, schema, table, column, data, key):
    #     for d in data:
    #         excd = "'excluded.".join(d) + ""
    #     sql = 'INSERT INTO {schema}.{table} ({column}) VALUES ({data}) \
    #         ON CONFLICT({key}) \
    #             DO UPDATE SET ({column}) = ({excd})'.format



    # def Connection(self):
    #     return psycopg2.connect(host=self.host, dbname=self.dbname,user=self.user,
    #     password=self.password, port=self.port, options=self.options)


