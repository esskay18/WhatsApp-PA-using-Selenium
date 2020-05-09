import sqlite3
from sqlite3 import Error
import os

source_directory = os.path.dirname(os.path.realpath(__file__))
database = os.path.join(source_directory, "Databases", "database.db")
print(database)

def appendTuple(tup, append_value):
    '''Helper function for dealing with tuples'''
    tup = list(tup)
    tup.append(append_value)
    tup = tuple(tup)

    return tup


def createConnection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None


def createTable(table_name, cols):
    base_str = "create table if not exists " + table_name + "("
    for col in cols:
        base_str += col + ", "

    base_str = base_str[:len(base_str) - 2] + ");"  # Done to remove the last comma

    try:
        conn = createConnection(database)
        c = conn.cursor()
        c.execute(base_str)
    except Error as e:
        print(e)


def updateTable(conn, table_name, where_col, where_value, update_col, update_value):
    base_str = "update ? set ? = ? where ? = ?"
    params = (table_name, update_col, update_value, where_col, where_value)

    try:
        conn = createConnection(conn)
        cursor = conn.cursor()
        cursor.execute(base_str, params)
        conn.commit()
    except Error as e:
        print(e)


def clearTable(table_name):
    base_str = "delete from ?"
    params = (table_name)

    try:
        conn = createConnection(database)
        cursor = conn.cursor()
        cursor.execute(base_str, params)
        conn.commit()
    except Error as e:
        print(e)


def addRow(table_name, values):
    base_str = "insert into " + table_name + " values(NULL, '"

    for value in values:
        base_str += value + "','"

    base_str = base_str[:len(base_str) - 3] + "');"
    print(base_str)

    try:
        conn = createConnection(database)
        cursor = conn.cursor()
        cursor.execute(base_str)
        conn.commit()
    except Error as e:
        print(e)


def deleteRow(table_name, where_col, where_value):
    base_str = "delete from " + table_name + " where " + where_col + " = ?"
    params = (where_value, )

    try:
        conn = createConnection(database)
        cursor = conn.cursor()
        cursor.execute(base_str, params)
        conn.commit()
    except Error as e:
        print(e)


def searchTable(table_name, ret_cols = None, where_col = None, where_value = None):
    base_str = "select "

    if ret_cols is not None:
        returnCols = ""
        for col in ret_cols:
            returnCols += col + ","
        print(returnCols)
        returnCols = returnCols[:len(returnCols) - 1]
        base_str += returnCols + " from " + table_name
    else:
        base_str += "* from" + table_name
    '''
    if where_col is not None:
        params = appendTuple(params, where_col)
        params = appendTuple(params, where_value)
    '''
    if where_col is not None:
        base_str += " where " + where_col + " = \"" + where_value + "\";"
    try:
        print(base_str)
        conn = createConnection(database)
        cursor = conn.cursor()
        cursor.execute(base_str)
        selection = cursor.fetchall()

        return selection
    except Error as e:
        print(e)

    return None


if __name__ == "__main__":

    createTable("notes", ["id integer primary key autoincrement", "title text NOT NULL", "content text NOT NULL"])
    createTable("birthdays", ["id integer primary key autoincrement", "name text NOT NULL", "birth_date date"])
    createTable("reminder", ["id integer primary key autoincrement", "title text NOT NULL", "remind_date date"])
