"""
Moduł odpowiedzialny za logowanie i uwierzytelnianie (wersja funkcyjna).
Zawiera funkcje: hash_password, authenticate, register_with_password, email_exists, generate_id.
"""

import csv                     # Do obsługi plików CSV (baza klientów)
import os                      # Do operacji na ścieżkach i plikach
import hashlib                 # Do szyfrowania hasła (SHA-256)
import datetime                # Do zapisywania daty rejestracji

# Ścieżka do pliku z danymi klientów
CUSTOMERS_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'customers.csv')

# Katalog na pliki związane z klientem (np. historia zakupów)
DATABASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'DATABASE')


def hash_password(password: str) -> str:
    """Zwraca SHA-256 hash hasła."""
    # Funkcja bierze hasło jako tekst i zwraca jego hash (czyli zakodowaną wersję)
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def email_exists(email: str) -> bool:
    """Sprawdza, czy email już jest w bazie."""
    # Jeśli plik nie istnieje, nie ma żadnych klientów
    if not os.path.exists(CUSTOMERS_CSV):
        return False
    # Otwórz plik i sprawdź, czy jakiś wiersz ma taki sam email
    with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return any(row.get('Email') == email for row in reader)


def generate_id() -> str:
    """Generuje nowe 4-cyfrowe ID klienta."""
    # Jeśli plik nie istnieje, zaczynamy od ID 1000
    if not os.path.exists(CUSTOMERS_CSV):
        return "1000"
    with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Pobieramy wszystkie numery ID, konwertujemy na int, szukamy największego i dodajemy 1
        ids = [int(row['ID']) for row in reader if row.get('ID', '').isdigit()]
        return str(max(ids) + 1) if ids else "1000"


def authenticate(customer_id: str, password: str) -> bool:
    """
    Weryfikuje, czy podane hasło pasuje do zapisanego dla klienta.
    :param customer_id: ID klienta
    :param password: hasło w postaci jawnej
    :return: True jeśli poprawne, False w przeciwnym razie
    """
    hashed = hash_password(password)  # Hashujemy podane hasło
    try:
        with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Szukamy klienta z takim ID i porównujemy hash hasła
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

    # Generujemy nowe ID
    cid = generate_id()

    # Hashujemy hasło
    pwd_hash = hash_password(password)

    # Zapisujemy bieżącą datę jako datę rejestracji
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    # Pola, które będą zapisane w pliku CSV
    fieldnames = ['ID', 'Imię', 'Nazwisko', 'Email', 'Data_rejestracji', 'PasswordHash', 'Telefon']

    # Sprawdzenie czy trzeba dodać nagłówek do pliku CSV
    header_needed = (not os.path.exists(CUSTOMERS_CSV)) or \
                    ('PasswordHash' not in open(CUSTOMERS_CSV, encoding='utf-8').readline())

    # Tworzenie folderu na wypadek, gdyby nie istniał
    os.makedirs(os.path.dirname(CUSTOMERS_CSV), exist_ok=True)

    # Dopisanie nowego klienta do pliku
    with open(CUSTOMERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if header_needed:
            writer.writeheader()  # Dodajemy nagłówki, jeśli trzeba
        writer.writerow({
            'ID': cid,
            'Imię': imie,
            'Nazwisko': nazwisko,
            'Email': email,
            'Data_rejestracji': now,
            'PasswordHash': pwd_hash,
            'Telefon': phone
        })

    # Tworzymy plik z historią zakupów klienta (pusty plik tekstowy)
    os.makedirs(DATABASE_DIR, exist_ok=True)
    open(os.path.join(DATABASE_DIR, f"{cid}.txt"), 'a', encoding='utf-8').close()

    return cid  # Zwracamy nowo utworzone ID klienta
