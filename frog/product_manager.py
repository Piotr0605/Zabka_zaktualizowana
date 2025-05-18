"""
Moduł do zarządzania produktami (dodawanie, usuwanie, listowanie).
"""

import pandas as pd
import os
from functools import wraps

# Ścieżka do pliku Excel z produktami
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.xlsx')


def handle_exceptions(func):
    """Dekorator obsługujący wyjątki I/O oraz ValueError."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IOError, ValueError) as e:
            print(f"Błąd w {func.__name__}: {e}")
    return wrapper


@handle_exceptions
def add_product(product: dict):
    """
    Dodaje nowy produkt do bazy Excel.
    :param product: słownik z kluczami ID, Nazwa, Kategoria, Cena, Ilość_w_magazynie
    """
    df = pd.read_excel(DATA_PATH)
    if product['ID'] in df['ID'].values:
        raise ValueError("Produkt o tym ID już istnieje.")
    # od Pandas 2.x append() jest usunięte, więc używamy concat
    new_row = pd.DataFrame([product])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(DATA_PATH, index=False)
    print(f"Produkt {product['Nazwa']} dodany.")


@handle_exceptions
def remove_product(identifier, by='ID'):
    """
    Usuwa produkt po ID lub nazwie.
    :param identifier: ID lub nazwa produktu
    :param by: 'ID' lub 'Nazwa'
    """
    df = pd.read_excel(DATA_PATH)
    initial = len(df)
    df = df[df[by] != identifier]
    if len(df) == initial:
        raise ValueError("Nie znaleziono produktu.")
    df.to_excel(DATA_PATH, index=False)
    print(f"Produkt(y) z {by}={identifier} usunięto.")


@handle_exceptions
def list_products() -> list[dict]:
    """
    Zwraca listę wszystkich produktów jako listę słowników.
    Każdy słownik zawiera pola: ID, Nazwa, Kategoria, Cena, Ilość_w_magazynie.
    :return: lista słowników z danymi produktów
    """
    df = pd.read_excel(DATA_PATH)
    return df.to_dict(orient='records')

