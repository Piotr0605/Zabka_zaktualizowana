"""
Moduł główny uruchamiający aplikację Frog (paradygmat funkcyjny).
"""

# --- Importy niezbędnych funkcji z innych modułów ---
import sys
from frog.product_manager import add_product, remove_product
from frog.customer_manager import register_customer, delete_customer, purchase_products
from frog.auth import authenticate, register_with_password
from frog.gui import run_gui

# --- Dekorator logujący operacje główne ---
def log_operation(operation):
    """
    Dekorator – wypisuje w konsoli nazwę operacji i ewentualny błąd.
    Używany nad funkcjami głównymi (logowanie, rejestracja, itp.).
    """
    def decorator(func):
        # --- Funkcja zagnieżdżona ---
        def wrapper(*args, **kwargs):
            print(f"[LOG] {operation}")
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[BŁĄD] {operation}: {e}")
                return None
        return wrapper
    return decorator

# --- Funkcja wyższego rzędu obsługująca wybór użytkownika ---
def menu_choice(handlers):
    """
    Obsługuje wybór użytkownika z menu.
    :param handlers: słownik, gdzie klucze to opcje (np. '1', '2'), a wartości to funkcje
    """
    choice = input("1) Zaloguj 2) Zarejestruj 3) GUI bez logowania: ")

    # --- Funkcja zagnieżdżona domyślna (lambda) uruchamia GUI ---
    return handlers.get(choice, handlers.get('default', lambda: run_gui()))()

# --- Funkcja logowania użytkownika i uruchomienia GUI ---
@log_operation("Logowanie i uruchamianie GUI")
def log_in():
    cid = input("Podaj ID klienta: ")
    pwd = input("Podaj hasło: ")
    if authenticate(cid, pwd):
        print("Zalogowano pomyślnie.")
        run_gui(client_id=cid)
    else:
        print("Nieprawidłowe dane.")

# --- Funkcja rejestracji nowego klienta i uruchomienia GUI ---
@log_operation("Rejestracja i uruchamianie GUI")
def register():
    im = input("Imię: ")
    nm = input("Nazwisko: ")
    email = input("Email: ")
    pwd = input("Ustaw hasło: ")
    try:
        cid = register_with_password(im, nm, email, pwd)
        print(f"Zarejestrowano ID={cid}")
        run_gui(client_id=cid)
    except Exception as e:
        print(f"Błąd rejestracji: {e}")

# --- Funkcja uruchamiająca GUI bez logowania (gość) ---
@log_operation("Uruchomienie GUI jako gość")
def run_as_guest():
    run_gui()

# --- Główna funkcja startowa ---
def __main__():
    """
    Główna funkcja aplikacji.
    Tworzy menu wyboru i obsługuje opcje:
    1 – logowanie, 2 – rejestracja, 3 – tryb gościa.
    """
    handlers = {
        '1': log_in,
        '2': register,
        '3': run_as_guest,
        'default': run_as_guest  # domyślnie – uruchom GUI jako gość
    }
    menu_choice(handlers)

# --- Punkt wejścia aplikacji ---
if __name__ == '__main__':
    __main__()
