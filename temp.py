from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from uuid import uuid4
from pydantic import BaseModel
from db import create_postgres_connection

class UserRegistration(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str

app = FastAPI()

connection = create_postgres_connection()

@app.post('/user/')
def register_user(user_data: UserRegistration, profile_picture: UploadFile = File(None)):
    try:
        # Check if email already exists in PostgreSQL
        connection = create_postgres_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT email FROM users WHERE email = %s", (user_data.email,))
        result = cursor.fetchone()
        if result:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=400, detail="Email already exists")

        # Save user data in PostgreSQL Users table
        cursor.execute("""
            INSERT INTO users (full_name, email, password, phone)
            VALUES (%s, %s, %s, %s) RETURNING user_id
        """, (user_data.full_name, user_data.email, user_data.password, user_data.phone))
        user_id = cursor.fetchone()[0]
        print("save done")
        # Save user profile picture in PostgreSQL Profile table
        if profile_picture:
            profile_picture_data = profile_picture.file.read()
            cursor.execute("""
                INSERT INTO profile (user_id, profile_picture)
                VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE
                SET profile_picture = excluded.profile_picture
            """, (user_id, profile_picture_data))

        connection.commit()
        cursor.close()
        connection.close()

        return {"message": "User registered successfully", "user_id": user_id}
    except Exception as e:
        print("Error registering user:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get('/users/')
def get_all_users():
    try:
        connection = create_postgres_connection()
        cursor = connection.cursor()

        # Fetch all users from Users table
        cursor.execute("SELECT * FROM Users")
        users_data = cursor.fetchall()

        # Initialize the list to store all users with profile pictures
        all_users = []

        for user_data in users_data:
            user_id = user_data[0]

            # Fetch profile picture from Profile table for each user
            cursor.execute("SELECT profile_picture FROM Profile WHERE user_id = %s", (user_id,))
            profile_picture = cursor.fetchone()
            profile_picture_url = profile_picture[0] if profile_picture else None

            user_with_profile = {
            "user_id":user_data[0],
            "full_name":user_data[1],
            "email":user_data[2],
            "phone":user_data[3],
            "profile_picture":profile_picture_url
            }
            all_users.append(user_with_profile)

        cursor.close()
        connection.close()

        return all_users
    except Exception as e:
        print("Error fetching all users:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get('/user/{user_id}')
def get_registered_user_details(user_id: int):
    try:
        connection = create_postgres_connection()
        cursor = connection.cursor()

        # Fetch user data from Users table
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch profile picture from Profile table
        cursor.execute("SELECT profile_picture FROM Profile WHERE user_id = %s", (user_id,))
        profile_picture = cursor.fetchone()
        profile_picture_url = profile_picture[0] if profile_picture else None

        cursor.close()
        connection.close()

        user_profile = {
            "user_id":user_data[0],
            "full_name":user_data[1],
            "email":user_data[2],
            "phone":user_data[3],
            "profile_picture":profile_picture_url
        }
        return user_profile
    except Exception as e:
        print("Error fetching user details:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
