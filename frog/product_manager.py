"""
Moduł obsługi produktów sklepu Żabka – wersja funkcyjna.
Zawiera funkcje do dodawania, usuwania i listowania produktów spożywczych.
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'products.xlsx')

def log_operation(operation):
    """Dekorator logujący operacje na produktach."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"[LOG] {operation}, args: {args}, kwargs: {kwargs}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def list_products():
    """
    Zwraca listę produktów jako listę słowników.
    """
    if not os.path.exists(DATA_PATH):
        return []
    df = pd.read_excel(DATA_PATH)
    return df.to_dict(orient='records')

@log_operation("Dodanie produktu")
def add_product(product):
    """
    Dodaje nowy produkt do bazy produktów.
    :param product: dict z kluczami: ID, Nazwa, Kategoria, Cena, Ilość_w_magazynie
    """
    try:
        if not os.path.exists(DATA_PATH):
            df = pd.DataFrame(columns=['ID', 'Nazwa', 'Kategoria', 'Cena', 'Ilość_w_magazynie'])
        else:
            df = pd.read_excel(DATA_PATH)
        df = pd.concat([df, pd.DataFrame([product])], ignore_index=True)
        df.to_excel(DATA_PATH, index=False)
    except Exception as e:
        print("Błąd dodawania produktu:", e)
        raise

@log_operation("Usuwanie produktu")
def remove_product(key, by='ID'):
    """
    Usuwa produkt na podstawie ID lub nazwy.
    :param key: ID lub nazwa produktu
    :param by: 'ID' lub 'Nazwa'
    """
    try:
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError("Brak bazy produktów.")
        df = pd.read_excel(DATA_PATH)
        if by == 'ID':
            df = df[df['ID'] != key]
        else:
            df = df[df['Nazwa'].str.lower() != str(key).lower()]
        df.to_excel(DATA_PATH, index=False)
    except Exception as e:
        print("Błąd usuwania produktu:", e)
        raise

def count_products(filter_func=None):
    """
    Funkcja wyższego rzędu: Zwraca liczbę produktów spełniających filter_func (lub wszystkich).
    :param filter_func: funkcja filtrująca lub None
    """
    products = list_products()
    if filter_func is None:
        return len(products)
    return len([p for p in products if filter_func(p)])
