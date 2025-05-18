# Frog_package – aplikacja sklepowa w Pythonie

## Opis

Aplikacja sklepowa z graficznym interfejsem (Tkinter), koszykiem, historią zakupów, zarządzaniem kontem klienta oraz możliwością wyboru motywu graficznego.

---

## Wymagania

- **Python 3.10 lub nowszy**
- **System:** Windows, Linux lub MacOS

---

## Instalacja bibliotek

W terminalu, w katalogu projektu, wpisz:

```bash
pip install pandas openpyxl
Struktura katalogów
frog_package/
├── data/
│   ├── customers.csv
│   └── products.xlsx
├── DATABASE/
│   └── (pliki historii zakupów klientów)
├── frog/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.ini
│   ├── customer_manager.py
│   ├── gui.py
│   ├── main.py
│   └── product_manager.py
├── venv/
│   └── (wirtualne środowisko, nie ruszaj)
└── README.md
Uruchomienie aplikacji
1. Otwórz terminal w katalogu głównym frog_package.

2. Uruchom aplikację poleceniem:
python -m frog.main
Jeśli pojawi się błąd z brakiem bibliotek, doinstaluj poleceniem:
pip install pandas openpyxl
Obsługa
Po starcie w terminalu pojawi się menu:
1) Zaloguj
2) Zarejestruj
3) GUI bez logowania
1 – logowanie: wpisz ID i hasło

2 – rejestracja: podaj imię, nazwisko, mail, telefon i hasło

3 – GUI bez logowania: otwiera sklep jako gość (bez historii zakupów)

W aplikacji możesz:

przeglądać produkty i koszyk,

kupować, usuwać produkty,

oglądać historię zakupów (po zalogowaniu),

zmieniać dane konta, hasło, telefon,

wybierać motyw graficzny.
Pliki danych
data/customers.csv – lista klientów

data/products.xlsx – lista produktów

DATABASE/ – historia zakupów klientów (po jednym pliku na klienta)
Najczęstsze problemy
Brak bibliotek: uruchom pip install pandas openpyxl

Brak katalogów: utwórz foldery data/ i DATABASE/ jeśli nie istnieją

Brak plików danych: stwórz lub skopiuj przykładowy customers.csv i products.xlsx do data/

Błąd ścieżki: uruchamiaj z katalogu głównego frog_package

Problemy z uruchomieniem: sprawdź komunikaty w terminalu oraz wersję Pythona

---





