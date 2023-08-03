from db import create_postgres_connection

def create_tables():
    try:
        connection = create_postgres_connection()
        cursor = connection.cursor()

        # Create Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                phone VARCHAR(20) NOT NULL UNIQUE
            )
        """)

        # Create Profile table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profile (
                profile_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES Users(user_id) UNIQUE,
                profile_picture TEXT
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()
        print("Tables created sucessfully")

    except Exception as e:
        print("Error creating tables:", e)


if __name__ == '__main__':
    create_tables()
