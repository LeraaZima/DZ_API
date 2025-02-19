from pydantic import BaseModel, field_validator, EmailStr, Field
from datetime import date
from fastapi import FastAPI, HTTPException
import re
import json
from pathlib import Path
import uvicorn

app = FastAPI()
DATA_FILE = Path("Subscriber.json")


class Subscriber(BaseModel):
    last_name: str = Field(..., description="Фамилия с заглавной буквы, только кириллица")
    first_name: str = Field(..., description="Имя с заглавной буквы, только кириллица")
    b_date: str = Field(..., description="Дата в формате ГГГГ-ММ-ДД")
    phone_number: str = Field(..., description="Номер телефона в международном формате")
    email: EmailStr = Field(..., description="E-mail адрес")

    @field_validator("last_name", "first_name")
    def validate_cyrillic(cls, value: str):
        if not re.fullmatch(r"[А-ЯЁ][а-яё]+", value):
            raise ValueError("Должно начинаться с заглавной буквы и содержать только кириллицу")
        return value


@app.post("/submit")
def submit_form(subscriber: Subscriber):
    try:
        # Чтение существующих данных
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        # Добавление новых данных
        data.append(subscriber.dict())

        # Сохранение в файл
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return {"message": "Данные успешно сохранены", "subscriber": subscriber.dict()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении данных: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("DZ_2:app", host="0.0.0.0", port=8000)
