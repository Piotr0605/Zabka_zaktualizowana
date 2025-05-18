"""
Interfejs graficzny Frog z autouzupełnianiem (ID i nazwy), zakładką Koszyk,
predefiniowanymi skórkami, responsywnym układem oraz funkcjami
dodawania i usuwania produktów, poprawionym paragonem i historią zakupów
z kwotami, możliwością dodania numeru telefonu jeśli go brak,
i prawidłowym askinteger().
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from frog.product_manager import list_products, DATA_PATH, add_product, remove_product
from frog.customer_manager import purchase_products
from frog.auth import authenticate, register_with_password, hash_password
import pandas as pd
import os
import csv
import datetime
import configparser

# --- ścieżki ---
BASE_DIR      = os.path.dirname(__file__)
RECEIPTS_DIR  = os.path.join(BASE_DIR, '..', 'DATABASE')
CUSTOMERS_CSV = os.path.join(BASE_DIR, '..', 'data', 'customers.csv')
CONFIG_INI    = os.path.join(BASE_DIR, 'config.ini')

# --- config.ini ---
config = configparser.ConfigParser()
if os.path.exists(CONFIG_INI):
    config.read(CONFIG_INI)
else:
    config['settings'] = {'theme': 'light'}
    with open(CONFIG_INI, 'w') as f:
        config.write(f)

def save_theme(theme_name):
    config['settings']['theme'] = theme_name
    with open(CONFIG_INI, 'w') as f:
        config.write(f)

# --- AutocompleteEntry dla ID i Nazwy ---
class AutocompleteEntry(ttk.Entry):
    def __init__(self, products_getter, *args, **kwargs):
        var = kwargs.get('textvariable')
        if var is None:
            var = tk.StringVar()
            kwargs['textvariable'] = var
        super().__init__(*args, **kwargs)
        self.var = var
        self.products_getter = products_getter
        self.var.trace_add('write', self._on_change)
        self.listbox = None

    def _on_change(self, *_):
        text = self.var.get().lower()
        if self.listbox:
            self.listbox.destroy()
            self.listbox = None
        if not text:
            return
        suggestions = []
        for p in self.products_getter():
            pid  = str(p.get('ID','')).lower()
            name = str(p.get('Nazwa','')).lower()
            if text in pid:
                suggestions.append(p['ID'])
            if text in name:
                suggestions.append(p['Nazwa'])
        seen = set()
        unique = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique.append(s)
            if len(unique) >= 10:
                break
        if not unique:
            return
        self.listbox = tk.Listbox(self.master, height=len(unique), bd=1)
        for s in unique:
            self.listbox.insert('end', s)
        self.listbox.place(
            x=self.winfo_x(),
            y=self.winfo_y() + self.winfo_height(),
            width=self.winfo_width()
        )
        self.listbox.bind('<<ListboxSelect>>', self._on_select)

    def _on_select(self, _):
        if not self.listbox:
            return
        sel = self.listbox.curselection()
        if sel:
            self.var.set(self.listbox.get(sel[0]))
        self.listbox.destroy()
        self.listbox = None
        self.event_generate('<KeyRelease>')


def run_gui(client_id=None):
    root = tk.Tk()
    root.title("Sklep Frog")

    # --- motywy ---
    style = ttk.Style()
    custom_themes = {
        'light':  {},
        'dark':   {'background':'#2e2e2e','foreground':'#f0f0f0'},
        'pastel': {'background':'#f7e6ff','foreground':'#5d0350'},
        'retro':  {'background':'#fff4e6','foreground':'#553300'},
    }
    current = config['settings'].get('theme','light')
    def apply_theme(name):
        style.theme_use('clam')
        cfg = custom_themes.get(name,{})
        root.configure(bg=cfg.get('background','white'))
        style.configure('.', background=cfg.get('background','white'),
                             foreground=cfg.get('foreground','black'))
        save_theme(name)
    apply_theme(current)

    # --- wybór skórki ---
    theme_frame = ttk.Frame(root)
    ttk.Label(theme_frame, text="Skórka:").pack(side='left')
    theme_cb = ttk.Combobox(theme_frame, values=list(custom_themes.keys()), state='readonly')
    theme_cb.set(current)
    theme_cb.pack(side='left', padx=5)
    theme_cb.bind('<<ComboboxSelected>>', lambda e: apply_theme(theme_cb.get()))
    theme_frame.pack(anchor='ne', padx=10, pady=5)

    # --- zakładki główne ---
    nb = ttk.Notebook(root)
    tab_products = ttk.Frame(nb)
    tab_cart     = ttk.Frame(nb)
    tab_history  = ttk.Frame(nb)
    tab_account  = ttk.Frame(nb)
    nb.add(tab_products, text="Produkty")
    nb.add(tab_cart,     text="Koszyk")
    nb.add(tab_history,  text="Historia")
    nb.add(tab_account,  text="Konto")
    nb.pack(fill='both', expand=True)

    cart = []
    search_var = tk.StringVar()

    # --- Produkty ---
    def refresh_products():
        tree_products.delete(*tree_products.get_children())
        q = search_var.get().strip().lower()
        for p in list_products():
            pid  = str(p.get('ID','')).lower()
            name = str(p.get('Nazwa','')).lower()
            cat  = str(p.get('Kategoria','')).lower()
            if q in pid or q in name or q in cat:
                tree_products.insert(
                    '', 'end',
                    values=(p['ID'], p['Nazwa'], f"{p['Cena']:.2f}", p['Ilość_w_magazynie'])
                )

    def add_to_cart():
        sel = tree_products.selection()
        if not sel:
            return
        pid, name, price, stock = tree_products.item(sel[0])['values']
        qty = simpledialog.askinteger(
            "Ilość", f"Ile sztuk {name}?",
            minvalue=1, maxvalue=int(stock), parent=root
        )
        if qty:
            cart.append((pid, qty))
            refresh_cart()

    def do_add_product():
        try:
            df = pd.read_excel(DATA_PATH)
            ids = [i for i in df['ID'].astype(str)
                   if i.startswith('P') and i[1:].isdigit()]
            nums = [int(i[1:]) for i in ids]
            next_id = f"P{max(nums)+1:03d}" if nums else "P001"

            name = simpledialog.askstring("Dodaj produkt","Nazwa produktu:", parent=root)
            if not name:
                return
            category = simpledialog.askstring("Dodaj produkt","Kategoria produktu:", parent=root)
            if not category:
                return
            price_str = simpledialog.askstring("Dodaj produkt","Cena (PLN):", parent=root)
            if not price_str:
                return
            price = float(price_str.replace(',','.'))
            stock = simpledialog.askinteger(
                "Dodaj produkt", "Ilość w magazynie:",
                minvalue=0, parent=root
            )
            if stock is None:
                return

            add_product({
                'ID': next_id,
                'Nazwa': name,
                'Kategoria': category,
                'Cena': price,
                'Ilość_w_magazynie': stock
            })
            messagebox.showinfo("Sukces", f"Dodano {name} (ID:{next_id})", parent=root)
            refresh_products()
        except ValueError:
            messagebox.showerror("Błąd","Nieprawidłowa cena.", parent=root)
        except Exception as e:
            messagebox.showerror("Błąd", str(e), parent=root)

    def do_remove_product():
        try:
            key = simpledialog.askstring("Usuń produkt","Podaj ID lub nazwę:", parent=root)
            if not key:
                return
            try:
                remove_product(key)
            except ValueError:
                remove_product(key, by='Nazwa')
            messagebox.showinfo("Sukces", f"Usunięto {key}", parent=root)
            refresh_products()
        except Exception as e:
            messagebox.showerror("Błąd", str(e), parent=root)

    # UI Produkty
    frm = ttk.Frame(tab_products)
    frm.pack(fill='x', padx=10, pady=5)
    ttk.Label(frm, text="Szukaj:").pack(side='left')
    ent_search = AutocompleteEntry(list_products, frm, textvariable=search_var)
    ent_search.pack(side='left', fill='x', expand=True, padx=5)
    ent_search.bind('<KeyRelease>', lambda e: refresh_products())

    cols = ('ID','Nazwa','Cena','Ilość')
    tree_products = ttk.Treeview(tab_products, columns=cols, show='headings')
    for c in cols:
        tree_products.heading(c, text=c)
        tree_products.column(c, anchor='center', stretch=True)
    tree_products.pack(fill='both', expand=True, padx=10, pady=5)

    btns = ttk.Frame(tab_products)
    btns.pack(fill='x', padx=10, pady=(0,10))
    ttk.Button(btns, text="Odśwież",          command=refresh_products).pack(side='left', padx=5)
    ttk.Button(btns, text="Dodaj do koszyka", command=add_to_cart).pack(side='left', padx=5)
    ttk.Button(btns, text="Dodaj produkt",    command=do_add_product).pack(side='left', padx=5)
    ttk.Button(btns, text="Usuń produkt",     command=do_remove_product).pack(side='left')

    # --- Koszyk ---
    def refresh_cart():
        tree_cart.delete(*tree_cart.get_children())
        total = 0.0
        df = pd.read_excel(DATA_PATH).set_index('ID')
        for pid, qty in cart:
            price = float(df.at[pid,'Cena'])
            total += price * qty
            tree_cart.insert('', 'end', values=(pid, qty))
        sum_var.set(f"Razem: {total:.2f} PLN")

    def remove_from_cart():
        sel = tree_cart.selection()
        if not sel:
            return
        cart.pop(tree_cart.index(sel[0]))
        refresh_cart()

    def show_receipt(cid, items):
        win = tk.Toplevel(root)
        win.title("Paragon")
        win.transient(root)
        win.lift()
        win.focus_force()
        text = tk.Text(win, width=50, height=len(items) + 6)
        total = 0.0
        df = pd.read_excel(DATA_PATH).set_index('ID')
        text.insert('end',
                    f"=== PARAGON Frog ===\nKlient: {cid}\n"
                    f"Data: {datetime.datetime.now():%Y-%m-%d %H:%M}\n\n"
                    )
        for pid, qty in items:
            cena = float(df.at[pid, 'Cena'])
            lt = cena * qty
            total += lt
            text.insert('end', f"{pid} {df.at[pid, 'Nazwa']} x{qty} @ {cena:.2f} = {lt:.2f}\n")
        text.insert('end', f"\nRAZEM: {total:.2f} PLN")
        text.config(state='disabled')
        text.pack(fill='both', expand=True)

    def checkout():
        nonlocal client_id
        if not cart:
            messagebox.showinfo("Koszyk pusty","Dodaj produkty do koszyka.", parent=root)
            return
        if not client_id:
            if messagebox.askyesno("Gość?","Kup jako gość?", parent=root):
                client_id = 'GUEST'
            else:
                nb.select(tab_account)
                return
        purchased = purchase_products(client_id, cart)
        if purchased:
            show_receipt(client_id, purchased)
            cart.clear()
            refresh_cart()
            messagebox.showinfo("Sukces","Zakup zakończony.", parent=root)
        else:
            messagebox.showwarning("Błąd","Żaden towar niedostępny.", parent=root)

    tree_cart = ttk.Treeview(tab_cart, columns=('ID','Ilość'), show='headings')
    for c in ('ID','Ilość'):
        tree_cart.heading(c, text=c)
        tree_cart.column(c, anchor='center', stretch=True)
    tree_cart.pack(fill='both', expand=True, padx=10, pady=5)

    sum_var = tk.StringVar(master=root, value="Razem: 0.00 PLN")
    ttk.Label(tab_cart, textvariable=sum_var).pack(anchor='e', padx=10)

    cart_btns = ttk.Frame(tab_cart)
    ttk.Button(cart_btns, text="Usuń",           command=remove_from_cart).pack(side='left', padx=5)
    ttk.Button(cart_btns, text="Finalizuj zakup", command=checkout).pack(side='left')
    cart_btns.pack(pady=(0,10))

    # --- Historia ---
    tree_hist = ttk.Treeview(tab_history, columns=('Data', 'Pozycje', 'Kwota'), show='headings')
    tree_hist.heading('Data', text='Data');
    tree_hist.column('Data', width=150, stretch=True)
    tree_hist.heading('Pozycje', text='Pozycje');
    tree_hist.column('Pozycje', stretch=True)
    tree_hist.heading('Kwota', text='Kwota');
    tree_hist.column('Kwota', stretch=True)
    tree_hist.pack(fill='both', expand=True, padx=10, pady=5)

    def refresh_history():
        tree_hist.delete(*tree_hist.get_children())
        if not client_id:
            return
        RECEIPTS_DIR = os.path.join(BASE_DIR, '..', 'DATABASE')
        path = os.path.join(RECEIPTS_DIR, f"{client_id}.txt")
        if os.path.exists(path):
            for line in open(path, encoding='utf-8'):
                if '->' not in line:
                    continue
                dt, items_str = line.strip().split(' -> ', 1)
                try:
                    items = eval(items_str)
                except Exception:
                    items = []
                df = pd.read_excel(DATA_PATH).set_index('ID')
                details = []
                total = 0.0
                for pid, qty in items:
                    if pid in df.index:
                        cena = float(df.at[pid, 'Cena'])
                        lt = cena * qty
                        total += lt
                        details.append(f"{pid}x{qty}={lt:.2f}")
                tree_hist.insert(
                    '', 'end',
                    values=(dt, ', '.join(details), f"{total:.2f} PLN")
                )

    nb.bind('<<NotebookTabChanged>>',
            lambda e: refresh_history() if nb.index('current') == 2 else None)

    nb.bind('<<NotebookTabChanged>>',
            lambda e: refresh_history() if nb.index('current') == 2 else None)

    # --- Konto ---
    acct_nb = ttk.Notebook(tab_account)
    tab_login = ttk.Frame(acct_nb)
    tab_info  = ttk.Frame(acct_nb)
    acct_nb.pack(fill='both', expand=True, padx=10, pady=10)

    def build_login_tab():
        for w in tab_login.winfo_children():
            w.destroy()
        ttk.Label(tab_login, text="ID:").grid(row=0, column=0, sticky='e')
        ent_id = ttk.Entry(tab_login); ent_id.grid(row=0, column=1)
        ttk.Label(tab_login, text="Hasło:").grid(row=1, column=0, sticky='e')
        ent_pwd = ttk.Entry(tab_login, show='*'); ent_pwd.grid(row=1, column=1)

        def do_login():
            nonlocal client_id
            if authenticate(ent_id.get(), ent_pwd.get()):
                client_id = ent_id.get()
                messagebox.showinfo("OK","Zalogowano", parent=root)
                build_account_tabs()
                refresh_history()
            else:
                messagebox.showerror("Błąd","Niepoprawne dane", parent=root)

        ttk.Button(tab_login, text="Zaloguj", command=do_login).grid(
            row=2, columnspan=2, pady=5)

        def do_register():
            nonlocal client_id
            im = simpledialog.askstring("Imię","Podaj imię:", parent=root)
            if not im:
                return
            nm = simpledialog.askstring("Nazwisko","Podaj nazwisko:", parent=root)
            if not nm:
                return
            email = simpledialog.askstring("Email","Podaj email:", parent=root)
            if not email:
                return
            pwd = simpledialog.askstring("Hasło","Podaj hasło:", show='*', parent=root)
            if not pwd:
                return
            phone = simpledialog.askstring("Telefon","Podaj telefon (9 cyfr):", parent=root)
            if phone is None or not(phone.isdigit() and len(phone)==9):
                messagebox.showerror("Błąd","Telefon musi mieć 9 cyfr", parent=root)
                return
            try:
                cid = register_with_password(im, nm, email, pwd, phone)
                client_id = cid
                messagebox.showinfo("OK", f"Zarejestrowano ID={cid}", parent=root)
                build_account_tabs()
                refresh_history()
            except ValueError as e:
                messagebox.showerror("Błąd", str(e), parent=root)

        ttk.Button(tab_login, text="Rejestracja", command=do_register).grid(
            row=3, columnspan=2, pady=5)

    def build_info_tab():
        for w in tab_info.winfo_children():
            w.destroy()
        user_data = {}
        with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if r['ID'] == client_id:
                    user_data = r
                    break

        ttk.Label(tab_info, text=f"ID: {user_data.get('ID','')}").pack(anchor='w', pady=(5,0))
        ttk.Label(tab_info, text=f"Email: {user_data.get('Email','')}").pack(anchor='w')

        phone = user_data.get('Telefon','').strip() if 'Telefon' in user_data else ''
        ttk.Label(tab_info, text=f"Telefon: {phone}").pack(anchor='w')
        if not phone:
            def add_phone():
                ph = simpledialog.askstring("Telefon","Podaj telefon (9 cyfr):", parent=root)
                if ph is None or not(ph.isdigit() and len(ph)==9):
                    messagebox.showerror("Błąd","Telefon musi mieć 9 cyfr", parent=root)
                    return
                rows = []
                with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        if r['ID'] == client_id:
                            r['Telefon'] = ph
                        rows.append(r)
                with open(CUSTOMERS_CSV, 'w', newline='', encoding='utf-8') as f:
                    wr = csv.DictWriter(f, fieldnames=reader.fieldnames)
                    wr.writeheader()
                    wr.writerows(rows)
                messagebox.showinfo("OK","Telefon dodany", parent=root)
                build_info_tab()
            ttk.Button(tab_info, text="Dodaj telefon", command=add_phone).pack(pady=5)
        else:
            def change_phone():
                ph = simpledialog.askstring("Telefon","Nowy telefon (9 cyfr):", initialvalue=phone, parent=root)
                if ph is None or not(ph.isdigit() and len(ph)==9):
                    messagebox.showerror("Błąd","Telefon musi mieć 9 cyfr", parent=root)
                    return
                rows = []
                with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        if r['ID'] == client_id:
                            r['Telefon'] = ph
                        rows.append(r)
                with open(CUSTOMERS_CSV, 'w', newline='', encoding='utf-8') as f:
                    wr = csv.DictWriter(f, fieldnames=reader.fieldnames)
                    wr.writeheader()
                    wr.writerows(rows)
                messagebox.showinfo("OK","Telefon zmieniony", parent=root)
                build_info_tab()
            ttk.Button(tab_info, text="Zmień telefon", command=change_phone).pack(pady=5)

        def change_email():
            new = simpledialog.askstring("Nowy email","Podaj nowy email:", parent=root)
            if not new:
                return
            rows = []
            with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if r['ID'] == client_id:
                        r['Email'] = new
                    rows.append(r)
            with open(CUSTOMERS_CSV, 'w', newline='', encoding='utf-8') as f:
                wr = csv.DictWriter(f, fieldnames=reader.fieldnames)
                wr.writeheader()
                wr.writerows(rows)
            messagebox.showinfo("OK","Email zmieniony", parent=root)

        ttk.Button(tab_info, text="Zmień email", command=change_email).pack(pady=5)

        def change_pwd():
            old = simpledialog.askstring("Stare hasło","Podaj stare:", show='*', parent=root)
            if old is None:
                return
            if not authenticate(client_id, old):
                messagebox.showerror("Błąd","Niepoprawne hasło", parent=root)
                return
            new = simpledialog.askstring("Nowe hasło","Podaj nowe:", show='*', parent=root)
            if not new:
                return
            h = hash_password(new)
            rows = []
            with open(CUSTOMERS_CSV, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if r['ID'] == client_id:
                        r['PasswordHash'] = h
                    rows.append(r)
            with open(CUSTOMERS_CSV, 'w', newline='', encoding='utf-8') as f:
                wr = csv.DictWriter(f, fieldnames=reader.fieldnames)
                wr.writeheader()
                wr.writerows(rows)
            messagebox.showinfo("OK","Hasło zmienione", parent=root)

        ttk.Button(tab_info, text="Zmień hasło", command=change_pwd).pack(pady=5)

        def logout():
            nonlocal client_id
            client_id = None
            messagebox.showinfo("Wylogowano","Wylogowano", parent=root)
            build_account_tabs()
            refresh_history()

        ttk.Button(tab_info, text="Wyloguj", command=logout).pack(pady=5)

    def build_account_tabs():
        for tab in acct_nb.tabs():
            acct_nb.forget(tab)
        if client_id:
            acct_nb.add(tab_info, text='Informacje')
            build_info_tab()
        else:
            acct_nb.add(tab_login, text='Logowanie / Rejestracja')
            build_login_tab()

    # --- Konto: tworzenie i start ---
    acct_nb = ttk.Notebook(tab_account)
    tab_login = ttk.Frame(acct_nb)
    tab_info  = ttk.Frame(acct_nb)
    acct_nb.pack(fill='both', expand=True, padx=10, pady=10)
    build_account_tabs()

    # --- Uruchomienie ---
    refresh_products()
    refresh_cart()
    root.mainloop()


if __name__ == '__main__':
    run_gui()
