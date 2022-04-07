import psycopg2
connection = psycopg2.connect(
    user="ehsan",
    password="180788",
    host="localhost",
    port="5432",
    database="temp"
)


def create_tables():

    commands = (
        """
        CREATE TABLE smartguard2 (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            path VARCHAR(255) NOT NULL
        )
        """)
    return commands


cursor = connection.cursor()
commands1 = create_tables()
cursor.execute(commands1)

#cursor.execute("DROP TABLE IF EXISTS smartguard2;")
