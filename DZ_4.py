from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, distinct, func
from sqlalchemy.orm import sessionmaker, declarative_base
import pandas as pd
from typing import List

# Настройка базы данных и SQLAlchemy
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

    # Обновление данных студента
    def update_student(self, student_id, last_name=None, first_name=None, faculty=None, course=None, grade=None):
        session = self.Session()
        student = session.query(Student).filter(Student.id == student_id).first()
        if student:
            if last_name:
                student.last_name = last_name
            if first_name:
                student.first_name = first_name
            if faculty:
                student.faculty = faculty
            if course:
                student.course = course
            if grade:
                student.grade = grade
            session.commit()
        session.close()

    # Удаление студента
    def delete_student(self, student_id):
        session = self.Session()
        student = session.query(Student).filter(Student.id == student_id).first()
        if student:
            session.delete(student)
            session.commit()
        session.close()

# Создание FastAPI приложения
app = FastAPI()
db_manager = DatabaseManager()

# Pydantic модели для валидации данных
class StudentCreate(BaseModel):
    last_name: str
    first_name: str
    faculty: str
    course: str
    grade: int

class StudentUpdate(BaseModel):
    last_name: str = None
    first_name: str = None
    faculty: str = None
    course: str = None
    grade: int = None

class StudentOut(BaseModel):
    id: int
    last_name: str
    first_name: str
    faculty: str
    course: str
    grade: int

    class Config:
        orm_mode = True

# Эндпойнты для работы с данными

@app.post("/students/", response_model=StudentOut)
def create_student(student: StudentCreate):
    db_manager.insert_student(
        student.last_name, student.first_name, student.faculty, student.course, student.grade
    )
    return student

@app.get("/students/", response_model=List[StudentOut])
def read_students():
    students = db_manager.get_students_by_faculty("")
    return students

@app.get("/students/{faculty}", response_model=List[StudentOut])
def read_students_by_faculty(faculty: str):
    students = db_manager.get_students_by_faculty(faculty)
    if not students:
        raise HTTPException(status_code=404, detail="Students not found")
    return students

@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, student: StudentUpdate):
    db_manager.update_student(
        student_id, student.last_name, student.first_name, student.faculty, student.course, student.grade
    )
    updated_student = db_manager.get_students_by_faculty("")  # Получаем обновленного студента
    return updated_student

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    db_manager.delete_student(student_id)
    return {"message": "Student deleted successfully"}

@app.get("/students/courses/", response_model=List[str])
def get_courses():
    return db_manager.get_unique_courses()

@app.get("/students/average_gpa/{faculty}", response_model=float)
def average_gpa(faculty: str):
    avg = db_manager.get_average_gpa_by_faculty(faculty)
    return avg
