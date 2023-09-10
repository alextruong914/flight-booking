from pydantic import BaseModel

class User(BaseModel):
    id: int
    email: str
    password: str
    first_name: str
    last_name: str

class FlightTicket(BaseModel):
    id: int
    airline: str
    departure_city: str
    arrival_city: str
    departure_date: str
    arrival_date: str
    price: float

class Booking(BaseModel):
    id: int
    user_id: int
    ticket_id: int
    booking_date: str

class Payment(BaseModel):
    id: int
    booking_id: int
    amount: float
    payment_date: str

class Cart(BaseModel):
    id: int
    user_id: int
    ticket_id: int
    quantity: int