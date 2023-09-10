from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import connection_pool
from models import User, FlightTicket, Booking, Payment, Cart

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
def login(email: str, password: str):
    # Check if the user exists in the database and the provided password is correct
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            if user_data is None or user_data[2] != password:
                raise HTTPException(status_code=401, detail="Invalid email or password")

    # If authentication is successful, return the user data
    user = User(
        id=user_data[0],
        email=user_data[1],
        password=user_data[2],
        first_name=user_data[3],
        last_name=user_data[4]
    )
    return user

@app.get("/flight_tickets")
def get_flight_tickets():
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM flight_tickets")
            tickets = cursor.fetchall()
    
    # Convert the retrieved data to FlightTicket objects
    flight_tickets = []
    for ticket in tickets:
        flight_ticket = FlightTicket(
            id=ticket[0],
            airline=ticket[1],
            departure_city=ticket[2],
            arrival_city=ticket[3],
            departure_date=ticket[4].strftime("%Y-%m-%d"),
            arrival_date=ticket[5].strftime("%Y-%m-%d"),
            price=float(ticket[6])
        )
        flight_tickets.append(flight_ticket)

    return flight_tickets

@app.get("/flight_tickets/{ticket_id}")
def get_flight_ticket(ticket_id: int):
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM flight_tickets WHERE id = %s", (ticket_id,))
            ticket_data = cursor.fetchone()
            if ticket_data is None:
                raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Convert the retrieved data to a FlightTicket object
    flight_ticket = FlightTicket(
        id=ticket_data[0],
        airline=ticket_data[1],
        departure_city=ticket_data[2],
        arrival_city=ticket_data[3],
        departure_date=ticket_data[4].strftime("%Y-%m-%d"),
        arrival_date=ticket_data[5].strftime("%Y-%m-%d"),
        price=float(ticket_data[6])
    )

    return flight_ticket

@app.post("/bookings")
def create_booking(user_id: int, ticket_id: int):
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            # Check if the ticket is available
            cursor.execute("SELECT * FROM flight_tickets WHERE id = %s", (ticket_id,))
            ticket_data = cursor.fetchone()
            if ticket_data is None:
                raise HTTPException(status_code=404, detail="Ticket not found")
            
            # Create the booking
            cursor.execute("INSERT INTO bookings (user_id, ticket_id, booking_date) VALUES (%s, %s, NOW()) RETURNING id",
                           (user_id, ticket_id))
            booking_id = cursor.fetchone()[0]
    
    return {"booking_id": booking_id}

@app.post("/cart")
def add_to_cart(user_id: int, ticket_id: int, quantity: int):
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            # Check if the ticket is available
            cursor.execute("SELECT * FROM flight_tickets WHERE id = %s", (ticket_id,))
            ticket_data = cursor.fetchone()
            if ticket_data is None:
                raise HTTPException(status_code=404, detail="Ticket not found")
            
            # Add the ticket to the cart
            cursor.execute("INSERT INTO cart (user_id, ticket_id, quantity) VALUES (%s, %s, %s) RETURNING id",
                           (user_id, ticket_id, quantity))
            cart_id = cursor.fetchone()[0]
    
    return {"cart_id": cart_id}

@app.post("/payments")
def make_payment(user_id: int, cart_id: int):
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            # Check if the cart item exists
            cursor.execute("SELECT * FROM cart WHERE id = %s", (cart_id,))
            cart_item = cursor.fetchone()
            if cart_item is None or cart_item[1] != user_id:
                raise HTTPException(status_code=404, detail="Cart item not found")

            # Retrieve the ticket price from the flight_tickets table
            cursor.execute("SELECT price FROM flight_tickets WHERE id = %s", (cart_item[2],))
            ticket_price = cursor.fetchone()[0]

            # Calculate the total amount to be paid
            amount = ticket_price * cart_item[3]

            # For the sake of this example, we'll assume the payment is successful
            payment_successful = True

            if not payment_successful:
                raise HTTPException(status_code=400, detail="Payment failed")

            # Create the payment record
            cursor.execute("INSERT INTO payments (booking_id, amount, payment_date) VALUES (%s, %s, NOW()) RETURNING id",
                           (cart_item[0], amount))
            payment_id = cursor.fetchone()[0]

            # Remove the item from the cart
            cursor.execute("DELETE FROM cart WHERE id = %s", (cart_id,))

    return {"payment_id": payment_id}

@app.get("/payments/{payment_id}")
def get_payment(payment_id: int):
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
            payment_data = cursor.fetchone()
            if payment_data is None:
                raise HTTPException(status_code=404, detail="Payment not found")
    
    # Convert the retrieved data to a Payment object
    payment = Payment(
        id=payment_data[0],
        booking_id=payment_data[1],
        amount=float(payment_data[2]),
        payment_date=payment_data[3].strftime("%Y-%m-%d")
    )

    return payment

@app.get("/bookings/history/{user_id}")
def get_booking_history(user_id: int):
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM bookings WHERE user_id = %s", (user_id,))
            bookings_data = cursor.fetchall()

    # Convert the retrieved data to a list of Booking objects
    booking_history = []
    for booking_data in bookings_data:
        booking = Booking(
            id=booking_data[0],
            user_id=booking_data[1],
            ticket_id=booking_data[2],
            booking_date=booking_data[3].strftime("%Y-%m-%d")
        )
        booking_history.append(booking)

    return booking_history