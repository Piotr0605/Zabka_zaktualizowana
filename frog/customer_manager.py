import csv
import os
import datetime

BASE_DIR = os.path.dirname(__file__)
CUSTOMERS_CSV = os.path.join(BASE_DIR, '..', 'data', 'customers.csv')
RECEIPTS_DIR = os.path.join(BASE_DIR, '..', 'DATABASE')

class Customer:
    def __init__(self, id, first_name, last_name, email, registration_date, password_hash, phone=""):
        self.id = str(id)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.registration_date = registration_date
        self.password_hash = password_hash
        self.phone = phone

    def to_dict(self):
        return {
            "ID": self.id,
            "Imię": self.first_name,
            "Nazwisko": self.last_name,
            "Email": self.email,
            "Data_rejestracji": self.registration_date,
            "PasswordHash": self.password_hash,
            "Telefon": self.phone
        }

def generate_id():
    if not os.path.exists(CUSTOMERS_CSV):
        return "1000"
    with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        ids = [int(row['ID']) for row in reader if row.get('ID', '').isdigit()]
        return str(max(ids) + 1) if ids else "1000"

def load_customers():
    customers = []
    if not os.path.exists(CUSTOMERS_CSV):
        return customers
    with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            customers.append(Customer(
                id=row.get("ID", ""),
                first_name=row.get("Imię", ""),
                last_name=row.get("Nazwisko", ""),
                email=row.get("Email", ""),
                registration_date=row.get("Data_rejestracji", ""),
                password_hash=row.get("PasswordHash", ""),
                phone=row.get("Telefon", "")
            ))
    return customers

def save_customers(customers):
    fieldnames = ["ID", "Imię", "Nazwisko", "Email", "Data_rejestracji", "PasswordHash", "Telefon"]
    with open(CUSTOMERS_CSV, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for customer in customers:
            writer.writerow(customer.to_dict())

def register_customer(imie, nazwisko, email, password_hash, phone=""):
    customers = load_customers()
    for c in customers:
        if c.email.lower() == email.lower():
            raise ValueError("Użytkownik z takim adresem email już istnieje!")
    new_id = generate_id()
    registration_date = datetime.datetime.now().strftime("%Y-%m-%d")
    new_customer = Customer(new_id, imie, nazwisko, email, registration_date, password_hash, phone)
    customers.append(new_customer)
    save_customers(customers)
    return new_id

def delete_customer(customer_id):
    customers = load_customers()
    customers = [c for c in customers if str(c.id) != str(customer_id)]
    save_customers(customers)

def find_customer_by_id(customer_id):
    customers = load_customers()
    for customer in customers:
        if str(customer.id) == str(customer_id):
            return customer
    return None

def purchase_products(customer_id, cart):
    """
    Zapisuje zakup do pliku historii klienta oraz zwraca koszyk (do paragonu)
    """
    if not cart:
        return []
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    receipt_path = os.path.join(RECEIPTS_DIR, f"{customer_id}.txt")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    # Zapisujemy: data -> [(id_produktu, ilosc), ...]
    with open(receipt_path, "a", encoding="utf-8") as f:
        f.write(f"{now} -> {repr(cart)}\n")
    return cart

def update_customer_phone(customer_id, new_phone):
    customers = load_customers()
    for customer in customers:
        if str(customer.id) == str(customer_id):
            customer.phone = new_phone
            break
    save_customers(customers)

def update_customer_email(customer_id, new_email):
    customers = load_customers()
    for customer in customers:
        if str(customer.id) == str(customer_id):
            customer.email = new_email
            break
    save_customers(customers)

def update_customer_password(customer_id, new_password_hash):
    customers = load_customers()
    for customer in customers:
        if str(customer.id) == str(customer_id):
            customer.password_hash = new_password_hash
            break
    save_customers(customers)
