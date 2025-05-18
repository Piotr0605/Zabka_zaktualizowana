# Frog

Pakiet obsługi sklepu online Frog.

## Instalacja

```bash
pip install pandas openpyxl
```

## Struktura

```
frog_package/
├── DATABASE/
├── data/
│   ├── products.xlsx
│   └── customers.csv
├── frog/
│   ├── __init__.py
│   ├── main.py
│   ├── product_manager.py
│   ├── customer_manager.py
│   ├── auth.py
│   └── gui.py
└── README.md
```

## Uruchomienie

```bash
python -m frog.main
```
