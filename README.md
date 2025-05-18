# Żabka Online – Funkcyjny sklep spożywczy

Aplikacja Python do zarządzania sklepem online Żabka, umożliwiająca:
- rejestrację klientów (z automatycznym generowaniem ID),
- logowanie oraz obsługę haseł (hashowanie SHA-256),
- przeglądanie i edycję produktów,
- robienie zakupów do koszyka oraz zapisywanie historii transakcji,
- zarządzanie danymi klienta (telefon, email, hasło),
- przyjazny interfejs graficzny (Tkinter) z obsługą skórek, autouzupełnianiem, responsywnym layoutem i historią zakupów.

---

## **Struktura katalogów**

```
frog_package/
│
├── frog/
│   ├── __init__.py
│   ├── main.py
│   ├── gui.py
│   ├── auth.py
│   ├── customer_manager.py
│   ├── product_manager.py
│   └── config.ini         # Tworzy się automatycznie przy pierwszym uruchomieniu GUI
│
├── data/
│   ├── products.xlsx
│   └── customers.csv
│
├── DATABASE/              # Folder z paragonami klientów (pliki txt)
│
└── README.md
```

---

## **Wymagania**

- Python **3.10+** (zalecany 3.11/3.12)
- Biblioteki:
    - `tkinter` (standardowy w Pythonie)
    - `pandas`
    - `openpyxl` (do obsługi plików `.xlsx` przez pandas)

Instalacja wymaganych pakietów (w terminalu/PowerShell):

```bash
pip install pandas openpyxl
```

---

## **Uruchomienie aplikacji**

1. **Sklonuj repozytorium lub rozpakuj folder projektu** w PyCharm/VSCode.
2. **Upewnij się, że struktura wygląda jak powyżej** (folder `frog`, `data`, `DATABASE`).
3. **Uzupełnij początkowe bazy** (jeśli puste):  
   - Plik `data/products.xlsx` zawiera przykładowe produkty (możesz dodać ręcznie lub przez aplikację).
   - Plik `data/customers.csv` zostanie utworzony automatycznie.
4. **Uruchom aplikację**:
   - W PyCharm kliknij `frog/main.py` i uruchom (`Shift+F10` lub zielony trójkąt).
   - Lub z terminala:
     ```
     python -m frog.main
     ```
5. **Wybierz tryb pracy**:
    - `1` – logowanie,
    - `2` – rejestracja,
    - `3` – uruchom GUI bez logowania (gość).

---

## **Główne funkcje**

- **Rejestracja i logowanie** (hasła hashowane, sprawdzanie unikalności emaili).
- **Koszyk zakupowy**: dodawanie, usuwanie, finalizacja z zapisem paragonu.
- **Edycja danych klienta**: email, telefon, zmiana hasła.
- **Historia zakupów** dla każdego klienta (oddzielny plik .txt).
- **Responsywny layout GUI**: autouzupełnianie, dynamiczne sortowanie tabel, różne motywy kolorystyczne.
- **Czysty paradygmat funkcyjny** (funkcje wyższego rzędu, dekoratory, czyste funkcje, obsługa wyjątków).
- **Łatwość rozbudowy** o kolejne funkcjonalności.

---

## **Przykładowe komendy administracyjne (konsola)**

- Dodanie produktu:
    ```python
    from frog.product_manager import add_product
    add_product({"ID": "P999", "Nazwa": "Nowy produkt", "Kategoria": "Test", "Cena": 9.99, "Ilość_w_magazynie": 10})
    ```

- Usunięcie produktu:
    ```python
    from frog.product_manager import remove_product
    remove_product("P999")
    ```

- Rejestracja klienta (konsola):
    ```
    python -m frog.main
    # wybierz opcję 2 i podaj dane
    ```

---

## **Zgłaszanie błędów i sugestii**

Jeśli coś nie działa lub masz pomysł na nową funkcjonalność, dodaj Issue na GitHubie lub napisz do autora.

---

## **Licencja**

Projekt stworzony do celów edukacyjnych w ramach kursu Python.

---

# Podsumowanie zgodności z wymaganiami projektu

- **Trzy pliki z danymi**: `products.xlsx`, `customers.csv`, folder `DATABASE/` (paragony klientów)
- **Trzy główne moduły**:
    - `product_manager.py` – dodawanie/usuwanie produktów
    - `customer_manager.py` – rejestracja/usuwanie klientów, obsługa zakupów
    - `auth.py` – logowanie, rejestracja z hashem, walidacja emaila, obsługa wyjątków
- **main.py** – funkcja główna `__main__()` uruchamia program
- **Interfejs graficzny** (GUI, Tkinter): obsługa klientów, koszyka, edycja danych, skórki, historia, responsywny layout, autouzupełnianie
- **Logika funkcyjna**:
    - **Funkcje wyższego rzędu** (np. sortowanie, menu, filtry)
    - **Dekoratory** (logowanie akcji)
    - **Funkcje wielu zmiennych wejściowych** (np. register_customer, add_product)
    - **Funkcje zagnieżdżone** (wewnątrz run_gui, obsługa zdarzeń)
    - **Obsługa wyjątków** w min. 3 funkcjach
    - **Dokumentacja** min. 3 funkcji i 2 modułów (docstringi)
- **Historia zakupów**: każdy klient ma swój plik z historią transakcji w `DATABASE/`
- **Możliwość rozwoju**: łatwa rozbudowa o nowe raporty/statystyki
- **Brak klas poza GUI** – całość oparta o funkcje

---

## **Autor:**
Projekt funkcyjny sklepu online Żabka  
2024
