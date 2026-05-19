import pymysql
from api import app, db
from models import User

DB_USER = "root"
DB_PASS = "Samuel@2004"
DB_HOST = "localhost"
DB_NAME = "Predictive_maintenance"

def init_database():
    # Connect directly via PyMySQL to ensure the database exists
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
    conn.commit()
    cursor.close()
    conn.close()

    # Now use SQLAlchemy to create tables
    with app.app_context():
        db.create_all()
        print(f"Database '{DB_NAME}' and tables verified/created successfully.")

        # Check if admin user exists, if not create one
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin")
            admin.set_password("password123")
            db.session.add(admin)
            db.session.commit()
            print("Admin user created (username: admin, password: password123)")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    init_database()
