import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# database engine object from SQLAlchemy that manages connections to the database
engine = create_engine(os.getenv("DATABASE_URL"))

# create a 'scoped session' that ensures different users' interactions with the
# database are kept separate
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, name VARCHAR NOT NULL, username VARCHAR NOT NULL, password VARCHAR NOT NULL)")
    db.execute("CREATE TABLE reviews(isbn VARCHAR NOT NULL, review VARCHAR NOT NULL, rating INTEGER NOT NULL, username VARCHAR NOT NULL)")
    db.execute("CREATE TABLE books(isbn VARCHAR PRIMARY KEY, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL)")
    sesame=open("books.csv")
    reader=csv.reader(sesame)
    for isbn, title, author, year in reader:
        if year == "year":
            print("first line skipped")
        else:
            db.execute("INSERT INTO books(isbn, title, author, year) VALUES(:isbn,:title,:author,:year)", {"isbn":isbn, "title":title, "author":author,"year":year})
    print("inserted")
    db.commit()

if __name__ == '__main__':
    main()