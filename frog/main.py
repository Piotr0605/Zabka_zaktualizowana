"""
Moduł główny uruchamiający aplikację Frog (paradygmat funkcyjny).
"""

import sys
from frog.product_manager import add_product, remove_product
from frog.customer_manager import register_customer, delete_customer, purchase_products
from frog.auth import authenticate, register_with_password
from frog.gui import run_gui

def log_operation(operation):
    """Dekorator logujący operacje główne."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"[LOG] {operation}")
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[BŁĄD] {operation}: {e}")
                return None
        return wrapper
    return decorator

def menu_choice(handlers):
    """
    Funkcja wyższego rzędu – obsługuje wybór użytkownika przez mapowanie opcji na funkcje.
    :param handlers: dict {opcja: funkcja}
    """
    choice = input("1) Zaloguj 2) Zarejestruj 3) GUI bez logowania: ")
    return handlers.get(choice, handlers.get('default', lambda: run_gui()))()

@log_operation("Logowanie i uruchamianie GUI")
def log_in():
    cid = input("Podaj ID klienta: ")
    pwd = input("Podaj hasło: ")
    if authenticate(cid, pwd):
        print("Zalogowano pomyślnie.")
        run_gui(client_id=cid)
    else:
        print("Nieprawidłowe dane.")

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

@log_operation("Uruchomienie GUI jako gość")
def run_as_guest():
    run_gui()

def __main__():
    """
    Główna funkcja startująca aplikację – wybór logowania/rejestracji/trybu gościa.
    """
    handlers = {
        '1': log_in,
        '2': register,
        '3': run_as_guest,
        'default': run_as_guest
    }
    menu_choice(handlers)

if __name__ == '__main__':
    __main__()
