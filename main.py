from fastapi import FastAPI, HTTPException, Body, Depends
from pydantic import BaseModel
from datetime import date, datetime
import asyncpg
from asyncpg.pool import Pool

# Database connection information
DATABASE_URL = "postgresql://postgres:Vikash8435@localhost:5432/mydatabase"

# FastAPI app instance
app = FastAPI()

# Pydantic models for request and response
class Employee(BaseModel):
    first_name: str
    middle_name: str = None
    last_name: str
    joining_date: str = None
    date_of_birth: str = None
    confirmation_date: str = None
    gender: str = None
    email: str = None
    mobile_number: str = None
    residence_phone: str = None
    emergency_contact: str = None
    employee_code: str = None
    biometric_code: str = None

    class Config:
        orm_mode = True

class EmployeeInDB(Employee):
    id: int

    class Config:
        orm_mode = True

# Function to create a database connection pool
async def get_database_pool() -> Pool:
    return await asyncpg.create_pool(DATABASE_URL)

# Endpoint to handle POST requests to create an employee
@app.post("/employees/", response_model=EmployeeInDB)
async def create_employee(employee: Employee = Body(...), db_pool: Pool = Depends(get_database_pool)):
    query = """
        INSERT INTO employee
        (first_name, middle_name, last_name, joining_date, date_of_birth, confirmation_date,
         gender, email, mobile_number, residence_phone, emergency_contact,
         employee_code, biometric_code)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        RETURNING id
    """

    # Convert date strings to datetime.date objects if they are provided
    values = (
        employee.first_name, employee.middle_name, employee.last_name,
        parse_date(employee.joining_date), parse_date(employee.date_of_birth), parse_date(employee.confirmation_date),
        employee.gender, employee.email, employee.mobile_number,
        employee.residence_phone, employee.emergency_contact,
        employee.employee_code, employee.biometric_code
    )

    async with db_pool.acquire() as connection:
        employee_id = await connection.fetchval(query, *values)
        return {**employee.dict(), "id": employee_id}

# Function to parse date strings to datetime.date objects
def parse_date(date_str: str) -> date:
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return None
