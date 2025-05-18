"""
Moduł odpowiedzialny za logowanie i uwierzytelnianie (wersja funkcyjna).
Zawiera funkcje: hash_password, authenticate, register_with_password, email_exists, generate_id.
"""

import csv
import os
import hashlib
import datetime

CUSTOMERS_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'customers.csv')
DATABASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'DATABASE')

def hash_password(password: str) -> str:
    """Zwraca SHA-256 hash hasła."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def email_exists(email: str) -> bool:
    """Sprawdza, czy email już jest w bazie."""
    if not os.path.exists(CUSTOMERS_CSV):
        return False
    with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return any(row.get('Email') == email for row in reader)

def generate_id() -> str:
    """Generuje nowe 4-cyfrowe ID klienta."""
    if not os.path.exists(CUSTOMERS_CSV):
        return "1000"
    with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ids = [int(row['ID']) for row in reader if row.get('ID', '').isdigit()]
        return str(max(ids) + 1) if ids else "1000"

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

def register_with_password(imie: str, nazwisko: str, email: str, password: str, phone: str = "") -> str:
    """
    Rejestruje nowego klienta z hasłem i numerem telefonu.
    Zwraca ID nowego klienta lub podnosi wyjątek jeśli email już istnieje.
    """
    # Sprawdzenie czy email już istnieje
    if email_exists(email):
        raise ValueError("Użytkownik z takim emailem już istnieje.")
    # Generowanie ID
    cid = generate_id()
    pwd_hash = hash_password(password)
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    fieldnames = ['ID', 'Imię', 'Nazwisko', 'Email', 'Data_rejestracji', 'PasswordHash', 'Telefon']
    header_needed = (not os.path.exists(CUSTOMERS_CSV)) or \
                    ('PasswordHash' not in open(CUSTOMERS_CSV, encoding='utf-8').readline())
    os.makedirs(os.path.dirname(CUSTOMERS_CSV), exist_ok=True)
    with open(CUSTOMERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if header_needed:
            writer.writeheader()
        writer.writerow({
            'ID': cid,
            'Imię': imie,
            'Nazwisko': nazwisko,
            'Email': email,
            'Data_rejestracji': now,
            'PasswordHash': pwd_hash,
            'Telefon': phone
        })
    # Utworzenie pliku historii zakupów
    os.makedirs(DATABASE_DIR, exist_ok=True)
    open(os.path.join(DATABASE_DIR, f"{cid}.txt"), 'a', encoding='utf-8').close()
    return cid

