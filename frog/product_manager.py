"""
Moduł obsługi produktów sklepu Żabka – wersja funkcyjna.
Zawiera funkcje do dodawania, usuwania i listowania produktów spożywczych.
"""

# --- Importy ---
import pandas as pd   # Obsługa plików Excel
import os             # Obsługa plików i ścieżek

# --- Ścieżka do pliku z produktami ---
BASE_DIR = os.path.dirname(__file__)  # Ścieżka katalogu tego pliku
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'products.xlsx')  # Lokalizacja pliku Excel z produktami

# --- Dekorator logujący operacje na produktach ---
def log_operation(operation):
    """
    Dekorator – wypisuje w terminalu nazwę operacji oraz przekazane argumenty.
    Używany np. przy dodawaniu lub usuwaniu produktów.
    """
    def decorator(func):
        # --- Funkcja zagnieżdżona ---
        def wrapper(*args, **kwargs):
            print(f"[LOG] {operation}, args: {args}, kwargs: {kwargs}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# --- Funkcja zwracająca wszystkie produkty ---
def list_products():
    """
    Wczytuje produkty z pliku Excel i zwraca jako listę słowników (dict).
    Każdy słownik to jeden produkt z polami: ID, Nazwa, Kategoria, Cena, Ilość_w_magazynie.
    """
    if not os.path.exists(DATA_PATH):
        return []
    df = pd.read_excel(DATA_PATH)
    return df.to_dict(orient='records')

# --- Funkcja dodająca nowy produkt ---
@log_operation("Dodanie produktu")
def add_product(product):
    """
    Dodaje nowy produkt do pliku Excel.
    :param product: dict z kluczami: ID, Nazwa, Kategoria, Cena, Ilość_w_magazynie
    """
    try:
        # Jeśli plik nie istnieje – utwórz pustą tabelę
        if not os.path.exists(DATA_PATH):
            df = pd.DataFrame(columns=['ID', 'Nazwa', 'Kategoria', 'Cena', 'Ilość_w_magazynie'])
        else:
            df = pd.read_excel(DATA_PATH)
        # Dodaj nowy produkt
        df = pd.concat([df, pd.DataFrame([product])], ignore_index=True)
        df.to_excel(DATA_PATH, index=False)
    except Exception as e:
        print("Błąd dodawania produktu:", e)
        raise

# --- Funkcja usuwająca produkt ---
@log_operation("Usuwanie produktu")
def remove_product(key, by='ID'):
    """
    Usuwa produkt na podstawie ID lub nazwy.
    :param key: ID lub nazwa produktu
    :param by: 'ID' (domyślnie) lub 'Nazwa'
    """
    try:
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError("Brak bazy produktów.")
        df = pd.read_excel(DATA_PATH)
        if by == 'ID':
            df = df[df['ID'] != key]
        else:
            # Porównanie nazw nie rozróżnia wielkości liter
            df = df[df['Nazwa'].str.lower() != str(key).lower()]
        df.to_excel(DATA_PATH, index=False)
    except Exception as e:
        print("Błąd usuwania produktu:", e)
        raise

# --- Funkcja zliczająca produkty (opcjonalnie z filtrem) ---
def count_products(filter_func=None):
    """
    Zwraca liczbę produktów spełniających podany warunek (funkcję filtrującą).
    Jeśli nie podano warunku, zwraca liczbę wszystkich produktów.
    :param filter_func: funkcja filtrująca (np. lambda p: p['Kategoria'] == 'Napoje')
    """
    products = list_products()
    if filter_func is None:
        return len(products)
    return len([p for p in products if filter_func(p)])
