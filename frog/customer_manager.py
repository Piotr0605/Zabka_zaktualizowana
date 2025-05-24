"""
Moduł obsługi klientów sklepu Żabka – wersja funkcyjna.
Zawiera funkcje do rejestracji, usuwania, aktualizacji i historii zakupów klientów.
"""

import csv
import os
import datetime

# Ścieżka do pliku CSV z danymi klientów
CUSTOMERS_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'customers.csv')

# Ścieżka do katalogu z plikami historii zakupów klientów
RECEIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'DATABASE')


def log_operation(operation):
    """Dekorator logujący operacje na klientach/produktach."""
    # Funkcja przyjmuje nazwę operacji (np. "Rejestracja nowego klienta")
    # i zwraca dekorator, który wypisuje logi przed i po wykonaniu funkcji
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"[LOG] Operacja: {operation}, args: {args}")  # Log wejścia
            result = func(*args, **kwargs)                       # Wykonanie oryginalnej funkcji
            print(f"[LOG] Zakończono: {operation}")             # Log zakończenia
            return result
        return wrapper
    return decorator


def load_customers():
    """Wczytuje listę klientów z pliku CSV."""
    if not os.path.exists(CUSTOMERS_CSV):
        return []
    with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))  # Zwraca listę słowników (klientów)


def save_customers(customers):
    """Zapisuje listę klientów do pliku CSV."""
    if not customers:
        return
    fieldnames = list(customers[0].keys())  # Pobieramy nagłówki z pierwszego rekordu
    with open(CUSTOMERS_CSV, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()               # Zapisujemy nagłówki
        writer.writerows(customers)        # Zapisujemy klientów


def generate_id(customers=None):
    """Generuje nowy, unikalny numer ID klienta (4 cyfry)."""
    if customers is None:
        customers = load_customers()
    # Pobieramy tylko ID, które są liczbami
    ids = [int(c['ID']) for c in customers if c.get('ID', '').isdigit()]
    if not ids:
        return "1000"
    return str(max(ids) + 1)  # Zwiększamy najwyższe ID o 1


@log_operation("Rejestracja nowego klienta")
def register_customer(imie, nazwisko, email, password_hash, phone=""):
    """
    Rejestruje nowego klienta. Zwraca ID.
    """
    customers = load_customers()

    # Funkcja zagnieżdżona do sprawdzenia, czy email już istnieje
    def email_exists(email_to_check, customers):
        return any(c['Email'].lower() == email_to_check.lower() for c in customers)

    # Jeśli email już istnieje, przerywamy rejestrację
    if email_exists(email, customers):
        raise ValueError("Użytkownik z takim adresem email już istnieje!")

    # Generujemy nowe ID i tworzymy rekord klienta
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

    customers.append(new_customer)  # Dodajemy do listy
    try:
        save_customers(customers)   # Zapisujemy do pliku
    except Exception as e:
        print("Błąd zapisu klienta:", e)
        raise
    return new_id  # Zwracamy ID


@log_operation("Usuwanie klienta")
def delete_customer(key, by="ID"):
    """
    Usuwa klienta po ID lub nazwisku.
    :param key: wartość do wyszukania (ID lub nazwisko)
    :param by: określa, czy szukać po "ID" czy "Nazwisko"
    """
    customers = load_customers()

    # Funkcja zagnieżdżona sprawdzająca, które rekordy zostawić
    def matches(c):
        if by == "ID":
            return c["ID"] != key
        elif by == "Nazwisko":
            return c["Nazwisko"].lower() != key.lower()
        return True  # Domyślnie zostawiamy wszystko

    new_customers = list(filter(matches, customers))  # Filtrowanie listy
    save_customers(new_customers)


@log_operation("Zakup produktów przez klienta")
def purchase_products(customer_id, cart):
    """
    Zapisuje zakup do pliku historii klienta oraz zwraca koszyk (do paragonu).
    """
    if not cart:
        return []

    try:
        os.makedirs(RECEIPTS_DIR, exist_ok=True)  # Tworzy folder, jeśli nie istnieje
        receipt_path = os.path.join(RECEIPTS_DIR, f"{customer_id}.txt")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # Dopisujemy zakup do pliku historii klienta
        with open(receipt_path, "a", encoding="utf-8") as f:
            f.write(f"{now} -> {repr(cart)}\n")

        return cart  # Zwracamy zawartość koszyka
    except Exception as e:
        print("Błąd zapisu zakupu:", e)
        raise


def filter_customers(filter_func):
    """
    Funkcja wyższego rzędu – zwraca listę klientów spełniających warunek filter_func.
    Przykład: filter_customers(lambda c: c['Nazwisko'] == 'Nowak')
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
    """Aktualizuje hasło klienta (już zahashowane)."""
    customers = load_customers()
    for customer in customers:
        if customer['ID'] == customer_id:
            customer['PasswordHash'] = new_password_hash
            break
    save_customers(customers)
