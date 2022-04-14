import psycopg2


def set_conection():
    connection = psycopg2.connect(
        user="ehsan",
        password="180788",
        host="localhost",
        port="5432",
        database="temp"
    )

    return connection


def create_tables():
    connection = set_conection()
    cursor = connection.cursor()
    commands = (
        """
        CREATE TABLE smartguard2 (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            path VARCHAR(255) NOT NULL,
            date DATE DEFAULT CURRENT_DATE,
            created_at TIME DEFAULT CURRENT_TIME
        
        )
        """)
    try:
        cursor.execute(commands)
    finally:
        connection.commit()
    return 1


def insert_query(name, pathh):
    connection = set_conection()
    cursor = connection.cursor()
    abc = "INSERT INTO public.smartguard2( name, path) VALUES('" + \
        name + "','" + pathh + "');"
    cursor.execute(abc)
    connection.commit()
    print("added")
    return 1


def get_all():
    connection = set_conection()
    cursor = connection.cursor()
    cursor.execute("Select * from smartguard2")
    print(cursor.fetchall())

    connection.commit()
    return 1


def get_by_name_date(name, datee):
    connection = set_conection()
    cursor = connection.cursor()
    cursor.execute("Select path from smartguard2 where name ='" +
                   name + "' AND date = '" + datee + "'""")
    abc = cursor.fetchall()
    cursor.execute("Select id from smartguard2 where name ='" +
                   name + "' AND date = '" + datee + "'""")
    cde = cursor.fetchall()
    connection.commit()
    return abc, cde


def get_by_name(name):
    connection = set_conection()
    cursor = connection.cursor()
    path = []
    key = []
    cursor.execute(
        "Select id,path from smartguard2 where name ='" + name + "'""")
    return cursor.fetchall()


def make_list(x):
    l1 = []
    for tup in x:
        l1.append({"uri": tup[1], "key": tup[0]})
    return l1


def drop_table():
    connection = set_conection()
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS smartguard2;")
    connection.commit()


def main():
    create_tables()


if __name__ == "__main__":
    main()
