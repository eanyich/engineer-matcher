from pydantic import BaseModel, EmailStr

class SupportTicket(BaseModel):
    id: int
    description: str
    customer_country: str

class Engineer(BaseModel):
    id: int
    name: str
    skillsets: str
    workload: int
    status: str
    region: str
    seniority: int
    manager_email: EmailStr
