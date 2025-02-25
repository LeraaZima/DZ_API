from sqlalchemy import create_engine, Column, Integer, String, Float, distinct, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import csv
import pandas as pd
# # sqlalchemy — это библиотека для работы с базами данных.
# # create_engine — создаёт соединение с базой данных.
# # Column, Integer, String, Float — используются для определения колонок в таблице.
# # distinct, func — помогают делать запросы (например, находить уникальные значения и вычислять среднее).
# # declarative_base — базовый класс, от которого наследуются модели данных.
# # sessionmaker — создаёт сессию для работы с базой данных.
# # relationship — используется для связей между таблицами (в этом коде не используется).
# # csv — библиотека для работы с файлами CSV.


Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    faculty = Column(String, nullable=False)
    course = Column(String, nullable=False)
    grade = Column(Integer, nullable=False)

class DatabaseManager:
    def __init__(self, db_url='sqlite:///students.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def insert_student(self, last_name, first_name, faculty, course, grade):
        session = self.Session()
        student = Student(last_name=last_name, first_name=first_name, faculty=faculty, course=course, grade=grade)
        session.add(student)
        session.commit()
        session.close()
    
    def load_from_csv(self, file_path):
        session = self.Session()
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            student = Student(
                last_name=row['Фамилия'],
                first_name=row['Имя'],
                faculty=row['Факультет'],
                course=row['Курс'],
                grade=int(row['Оценка'])
            )
            session.add(student)
        session.commit()
        session.close()
    
    def get_students_by_faculty(self, faculty):
        session = self.Session()
        students = session.query(Student).filter(Student.faculty == faculty).all()
        session.close()
        return students
    
    def get_unique_courses(self):
        session = self.Session()
        courses = session.query(distinct(Student.course)).all()
        session.close()
        return [course[0] for course in courses]
    
    def get_average_gpa_by_faculty(self, faculty):
        session = self.Session()
        avg_grade = session.query(func.avg(Student.grade)).filter(Student.faculty == faculty).scalar()
        session.close()
        return avg_grade
    


