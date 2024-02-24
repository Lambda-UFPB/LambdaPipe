import psycopg2

# ESPERAR CONECTAR

def connect_to_db():
    try:
        connection = psycopg2.connect(
            user="web",
            password="web",
            host="192.168.0.1",
            port="5433",
            database="vs"
        )

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print(connection.get_dsn_parameters(), "\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

connect_to_db()