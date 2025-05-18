"""
Moduł obsługi klientów sklepu Żabka – wersja funkcyjna.
Zawiera funkcje do rejestracji, usuwania, aktualizacji i historii zakupów klientów.
"""

import csv
import os
import datetime

CUSTOMERS_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'customers.csv')
RECEIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'DATABASE')

def log_operation(operation):
    """Dekorator logujący operacje na klientach/produktach."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"[LOG] Operacja: {operation}, args: {args}")
            result = func(*args, **kwargs)
            print(f"[LOG] Zakończono: {operation}")
            return result
        return wrapper
    return decorator

def load_customers():
    """Wczytuje listę klientów z pliku CSV."""
    if not os.path.exists(CUSTOMERS_CSV):
        return []
    with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))

def save_customers(customers):
    """Zapisuje listę klientów do pliku CSV."""
    if not customers:
        return
    fieldnames = list(customers[0].keys())
    with open(CUSTOMERS_CSV, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(customers)

def generate_id(customers=None):
    """Generuje nowy, unikalny numer ID klienta (4 cyfry)."""
    if customers is None:
        customers = load_customers()
    ids = [int(c['ID']) for c in customers if c.get('ID', '').isdigit()]
    if not ids:
        return "1000"
    return str(max(ids) + 1)

@log_operation("Rejestracja nowego klienta")
def register_customer(imie, nazwisko, email, password_hash, phone=""):
    """
    Rejestruje nowego klienta. Zwraca ID.
    :param imie: str
    :param nazwisko: str
    :param email: str
    :param password_hash: str
    :param phone: str (opcjonalnie)
    :return: str (ID klienta)
    """
    customers = load_customers()
    def email_exists(email_to_check, customers):
        return any(c['Email'].lower() == email_to_check.lower() for c in customers)
    if email_exists(email, customers):
        raise ValueError("Użytkownik z takim adresem email już istnieje!")
    new_id = generate_id(customers)
    registration_date = datetime.datetime.now().strftime("%Y-%m-%d")
    new_customer = {
        "ID": new_id,
        "Imię": imie,
        "Nazwisko": nazwisko,
        "Email": email,
        "Data_rejestracji": registration_date,
        "PasswordHash": password_hash,
        "Telefon": phone
    }
    customers.append(new_customer)
    try:
        save_customers(customers)
    except Exception as e:
        print("Błąd zapisu klienta:", e)
        raise
    return new_id

@log_operation("Usuwanie klienta")
def delete_customer(key, by="ID"):
    """
    Usuwa klienta po ID lub nazwisku.
    :param key: str
    :param by: 'ID' lub 'Nazwisko'
    """
    customers = load_customers()
    def matches(c):
        if by == "ID":
            return c["ID"] != key
        elif by == "Nazwisko":
            return c["Nazwisko"].lower() != key.lower()
        return True
    new_customers = list(filter(matches, customers))
    save_customers(new_customers)

@log_operation("Zakup produktów przez klienta")
def purchase_products(customer_id, cart):
    """
    Zapisuje zakup do pliku historii klienta oraz zwraca koszyk (do paragonu)
    """
    if not cart:
        return []
    try:
        os.makedirs(RECEIPTS_DIR, exist_ok=True)
        receipt_path = os.path.join(RECEIPTS_DIR, f"{customer_id}.txt")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(receipt_path, "a", encoding="utf-8") as f:
            f.write(f"{now} -> {repr(cart)}\n")
        return cart
    except Exception as e:
        print("Błąd zapisu zakupu:", e)
        raise

def filter_customers(filter_func):
    """
    Funkcja wyższego rzędu – zwraca listę klientów spełniających warunek filter_func.
    """
    return list(filter(filter_func, load_customers()))

def update_customer_phone(customer_id, new_phone):
    """Aktualizuje numer telefonu klienta."""
    customers = load_customers()
    for customer in customers:
        if customer['ID'] == customer_id:
            customer['Telefon'] = new_phone
            break
    save_customers(customers)

def update_customer_email(customer_id, new_email):
    """Aktualizuje adres email klienta."""
    customers = load_customers()
    for customer in customers:
        if customer['ID'] == customer_id:
            customer['Email'] = new_email
            break
    save_customers(customers)

def update_customer_password(customer_id, new_password_hash):
    """Aktualizuje hasło klienta."""
    customers = load_customers()
    for customer in customers:
        if customer['ID'] == customer_id:
            customer['PasswordHash'] = new_password_hash
            break
    save_customers(customers)
