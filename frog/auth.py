"""
Moduł odpowiedzialny za logowanie i uwierzytelnianie.
"""

import csv
import os
import hashlib
import datetime

CUSTOMERS_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'customers.csv')


def hash_password(password: str) -> str:
    """Zwraca SHA-256 hash hasła."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def authenticate(customer_id: str, password: str) -> bool:
    """
    Weryfikuje, czy podane hasło pasuje do zapisanego dla klienta.
    :param customer_id: ID klienta
    :param password: hasło w postaci jawnej
    :return: True jeśli poprawne, False w przeciwnym razie
    """
    hashed = hash_password(password)
    try:
        with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('ID') == customer_id and row.get('PasswordHash') == hashed:
                    return True
    except FileNotFoundError:
        return False
    return False


def register_with_password(imie, nazwisko, email, password, phone=""):
    from frog.customer_manager import register_customer
    password_hash = hash_password(password)
    return register_customer(imie, nazwisko, email, password_hash, phone)

    """
    Rejestruje nowego klienta z hasłem, zapisuje hash hasła.
    Sprawdza, czy użytkownik o podanym emailu już istnieje.
    :param first_name: imię klienta
    :param last_name: nazwisko klienta
    :param email: adres email (jednoznaczny identyfikator)
    :param password: hasło w formie jawnej
    :return: ID nowo utworzonego klienta
    :raises ValueError: jeśli email jest już zarejestrowany
    """
    # Sprawdzenie obecności pliku i unikalności email
    if os.path.exists(CUSTOMERS_CSV):
        with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Email') == email:
                    raise ValueError("Użytkownik z takim emailem już istnieje.")
    # Generowanie ID i hash hasła
    from frog.customer_manager import generate_id
    cid = generate_id()
    pwd_hash = hash_password(password)
    now = datetime.datetime.now().isoformat()
    fieldnames = ['ID', 'Imię', 'Nazwisko', 'Email', 'Data_rejestracji', 'PasswordHash']
    # Sprawdzenie czy należy dodać header
    header_needed = not os.path.exists(CUSTOMERS_CSV) or 'PasswordHash' not in open(CUSTOMERS_CSV, encoding='utf-8').readline()
    os.makedirs(os.path.dirname(CUSTOMERS_CSV), exist_ok=True)
    with open(CUSTOMERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if header_needed:
            writer.writeheader()
        writer.writerow({
            'ID': cid,
            'Imię': first_name,
            'Nazwisko': last_name,
            'Email': email,
            'Data_rejestracji': now,
            'PasswordHash': pwd_hash
        })
    # Utworzenie pliku transakcji klienta
    db_folder = os.path.join(os.path.dirname(__file__), '..', 'DATABASE')
    os.makedirs(db_folder, exist_ok=True)
    open(os.path.join(db_folder, f"{cid}.txt"), 'w', encoding='utf-8').close()
    return cid

