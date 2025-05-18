# Frog_package – aplikacja sklepowa w Pythonie

## Opis

Aplikacja sklepowa z graficznym interfejsem (Tkinter), koszykiem, historią zakupów, zarządzaniem kontem klienta oraz możliwością wyboru motywu graficznego.

---

## Wymagania

- Python 3.10 lub nowszy
- System: Windows, Linux lub MacOS

---

## Instalacja bibliotek

W terminalu, w katalogu projektu, wpisz:

```bash
pip install pandas openpyxl


## Struktura

```
frog_package/
│
├── data/
│     customers.csv
│     products.xlsx
│
├── DATABASE/
│     (pliki historii zakupów klientów)
│
├── frog/
│     __init__.py
│     auth.py
│     config.ini
│     customer_manager.py
│     gui.py
│     main.py
│     product_manager.py
│
├── venv/
│     (wirtualne środowisko, nie ruszaj)
│
└── README.md


```

## Uruchomienie

```bash
python -m frog.main
```
