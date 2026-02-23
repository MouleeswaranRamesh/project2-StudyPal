import os
from dotenv import load_dotenv
from vectorize_book import vectorize_book_and_store_to_db,vectorize_chapters

load_dotenv()

SUBJECT_NAME=os.getenv("SUBJECT_NAME")

vectorize_book_and_store_to_db(SUBJECT_NAME,"Books_vector_DB")
vectorize_chapters(SUBJECT_NAME)
#print("end")