"""
Moduł główny uruchamiający aplikację Frog.
"""

import sys
from frog.product_manager import add_product, remove_product
from frog.customer_manager import register_customer, delete_customer, purchase_products
from frog.auth import authenticate, register_with_password
from frog.gui import run_gui

def __main__():
    """Uruchomienie logowania/rejestracji i GUI."""
    choice = input("1) Zaloguj 2) Zarejestruj 3) GUI bez logowania: ")
    if choice == '1':
        cid = input("Podaj ID klienta: ")
        pwd = input("Podaj hasło: ")
        if authenticate(cid, pwd):
            print("Zalogowano pomyślnie.")
            run_gui(client_id=cid)
        else:
            print("Nieprawidłowe dane.")
    elif choice == '2':
        im = input("Imię: ")
        nm = input("Nazwisko: ")
        email = input("Email: ")
        pwd = input("Ustaw hasło: ")
        cid = register_with_password(im, nm, email, pwd)
        print(f"Zarejestrowano ID={cid}")
        run_gui(client_id=cid)
    else:
        run_gui()

if __name__ == '__main__':
    __main__()
