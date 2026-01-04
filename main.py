import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime

# === Baza de date ===
conn = sqlite3.connect("service_auto.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS masini (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nr_inmatriculare TEXT,
    vin TEXT,
    marca TEXT,
    model TEXT,
    data_fabricatie TEXT,
    capacitate_cm3 TEXT,
    putere_kw TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS interventii (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    masina_id INTEGER,
    data TEXT,
    descriere TEXT,
    km TEXT,
    nr_factura TEXT,
    furnizor_piese TEXT,
    nume_client TEXT,
    telefon_client TEXT,
    FOREIGN KEY (masina_id) REFERENCES masini(id)
)
''')

conn.commit()

# === Funcții ===
def adauga_masina_si_interventie():
    nr = entry_nr.get().strip().upper()
    vin = entry_vin.get().strip()
    marca = entry_marca.get().strip()
    model = entry_model.get().strip()
    an = entry_an.get().strip()
    capacitate = entry_capacitate.get().strip()
    putere = entry_putere.get().strip()
    data = entry_data.get().strip()
    descriere = entry_descriere.get("1.0", tk.END).strip()
    km = entry_km.get().strip()
    factura = entry_factura.get().strip()
    furnizor = entry_furnizor.get().strip()
    nume_client = entry_nume_client.get().strip()
    tel_client = entry_tel_client.get().strip()

    if not (nr and descriere):
        messagebox.showerror("Eroare", "Completează cel puțin numărul de înmatriculare și intervenția.")
        return

    if not data:
        data = datetime.now().strftime("%d-%m-%Y")

    cursor.execute("SELECT id FROM masini WHERE nr_inmatriculare=?", (nr,))
    masina = cursor.fetchone()

    if masina:
        masina_id = masina[0]
    else:
        cursor.execute('''
            INSERT INTO masini (nr_inmatriculare, vin, marca, model, data_fabricatie, capacitate_cm3, putere_kw)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nr, vin, marca, model, an, capacitate, putere))
        masina_id = cursor.lastrowid

    cursor.execute('''
        INSERT INTO interventii (masina_id, data, descriere, km, nr_factura, furnizor_piese, nume_client, telefon_client)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (masina_id, data, descriere, km, factura, furnizor, nume_client, tel_client))

    conn.commit()
    messagebox.showinfo("Succes", "Intervenție adăugată cu succes!")

    for entry in [entry_descriere, entry_data, entry_km, entry_factura, entry_furnizor, entry_nume_client, entry_tel_client]:
        if isinstance(entry, tk.Text):
            entry.delete("1.0", tk.END)
        else:
            entry.delete(0, tk.END)

def afiseaza_istoric():
    def cauta_si_afiseaza():
        nr_cautat = entry_popup.get().strip().upper()
        popup.destroy()
        if not nr_cautat:
            messagebox.showwarning("Avertisment", "Introdu un număr de înmatriculare.")
            return

        for row in tree.get_children():
            tree.delete(row)

        cursor.execute('''
            SELECT i.id, m.nr_inmatriculare, m.vin, i.km, m.marca, m.model, m.data_fabricatie,
                   m.capacitate_cm3, m.putere_kw, i.data, i.nr_factura, i.furnizor_piese,
                   i.nume_client, i.telefon_client, i.descriere
            FROM interventii i
            JOIN masini m ON i.masina_id = m.id
            WHERE m.nr_inmatriculare=?
            ORDER BY i.data DESC
        ''', (nr_cautat,))

        results = cursor.fetchall()
        if not results:
            messagebox.showinfo("Info", f"Nicio intervenție găsită pentru: {nr_cautat}")
        else:
            for row in results:
                tree.insert("", "end", values=row)

    popup = tk.Toplevel(root)
    popup.title("Caută istoric după nr. înmatriculare")
    popup.geometry("400x120")
    popup.transient(root)
    popup.grab_set()

    tk.Label(popup, text="Număr înmatriculare:", font=("Segoe UI", 12)).pack(pady=10)
    entry_popup = tk.Entry(popup, font=("Segoe UI", 12), width=30)
    entry_popup.pack()
    entry_popup.focus()

    tk.Button(popup, text="Caută", font=("Segoe UI", 11, "bold"), command=cauta_si_afiseaza).pack(pady=10)


def sterge_interventie():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Selectează", "Selectează o intervenție din tabel.")
        return

    values = tree.item(selected)["values"]
    if not values:
        return

    confirm = messagebox.askyesno("Confirmare", "Ești sigur că vrei să ștergi această intervenție?")
    if not confirm:
        return

    id_interventie = values[0]
    cursor.execute("DELETE FROM interventii WHERE id=?", (id_interventie,))
    conn.commit()
    tree.delete(selected)

    for widget in info_frame.winfo_children():
        widget.destroy()

    messagebox.showinfo("Șters", "Intervenția a fost ștearsă cu succes.")


def editeaza_interventie():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Selectează", "Selectează o intervenție din tabel.")
        return

    values = tree.item(selected)["values"]
    if not values or len(values) < 15:
        return

    popup = tk.Toplevel(root)
    popup.title("Editează Intervenția")
    popup.geometry("800x500")
    popup.transient(root)
    popup.grab_set()

    fields = [
        "KM", "Dată", "Factură", "Furnizor", "Nume client", "Telefon client", "Descriere"
    ]
    entries = {}

    for i, field in enumerate(fields):
        tk.Label(popup, text=field + ":", font=("Segoe UI", 12)).grid(row=i, column=0, sticky="e", padx=10, pady=5)
        if field == "Descriere":
            txt = tk.Text(popup, font=("Segoe UI", 12), width=80, height=6)
            txt.insert("1.0", values[14])
            txt.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = txt
        else:
            entry = tk.Entry(popup, font=("Segoe UI", 12), width=50)
            entry.insert(0, values[[3, 9, 10, 11, 12, 13][fields.index(field)]])
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

    def salveaza_modificari():
        try:
            km = entries["KM"].get()
            data = entries["Dată"].get()
            factura = entries["Factură"].get()
            furnizor = entries["Furnizor"].get()
            nume = entries["Nume client"].get()
            telefon = entries["Telefon client"].get()
            descriere = entries["Descriere"].get("1.0", tk.END).strip()

            cursor.execute('''
                UPDATE interventii
                SET km=?, data=?, nr_factura=?, furnizor_piese=?, nume_client=?, telefon_client=?, descriere=?
                WHERE id=?
            ''', (km, data, factura, furnizor, nume, telefon, descriere, values[0]))
            conn.commit()
            popup.destroy()
            afiseaza_istoric()  # Reîncarcă tabelul
            messagebox.showinfo("Salvat", "Modificările au fost salvate.")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la salvare: {e}")

    tk.Button(popup, text="Salvează modificările", font=("Segoe UI", 11, "bold"), command=salveaza_modificari).grid(row=len(fields), columnspan=2, pady=20)


def autocomplete_date_masina(event=None):
    nr_inmatriculare = entry_nr.get().strip().upper()
    if not nr_inmatriculare:
        return

    # Autocompletare date mașină
    cursor.execute("SELECT * FROM masini WHERE nr_inmatriculare=?", (nr_inmatriculare,))
    row = cursor.fetchone()
    if row:
        _, _, vin, marca, model, data_fabricatie, capacitate, putere = row

        entry_vin.delete(0, tk.END)
        entry_vin.insert(0, vin)

        entry_marca.delete(0, tk.END)
        entry_marca.insert(0, marca)

        entry_model.delete(0, tk.END)
        entry_model.insert(0, model)

        entry_an.delete(0, tk.END)
        entry_an.insert(0, data_fabricatie)

        entry_capacitate.delete(0, tk.END)
        entry_capacitate.insert(0, capacitate)

        entry_putere.delete(0, tk.END)
        entry_putere.insert(0, putere)

    def autocomplete_date_masina(event=None):
        nr_inmatriculare = entry_nr.get().strip().upper()
        if not nr_inmatriculare:
            return

        try:
            # Caută datele mașinii
            cursor.execute(
                "SELECT vin, marca, model, data_fabricatie, capacitate_cm3, putere_kw FROM masini WHERE nr_inmatriculare=?",
                (nr_inmatriculare,))
            masina = cursor.fetchone()
            if masina:
                vin, marca, model, data_fabricatie, capacitate_cm3, putere_kw = masina

                entry_vin.delete(0, tk.END)
                entry_vin.insert(0, vin)

                entry_marca.delete(0, tk.END)
                entry_marca.insert(0, marca)

                entry_model.delete(0, tk.END)
                entry_model.insert(0, model)

                entry_an.delete(0, tk.END)
                entry_an.insert(0, data_fabricatie)

                entry_capacitate.delete(0, tk.END)
                entry_capacitate.insert(0, capacitate_cm3)

                entry_putere.delete(0, tk.END)
                entry_putere.insert(0, putere_kw)

            # Caută ultimul client asociat
            cursor.execute('''
                SELECT i.nume_client, i.telefon_client
                FROM interventii i
                JOIN masini m ON i.masina_id = m.id
                WHERE m.nr_inmatriculare = ?
                ORDER BY i.data DESC
                LIMIT 1
            ''', (nr_inmatriculare,))
            client = cursor.fetchone()
            if client:
                nume_client, telefon_client = client

                entry_nume_client.delete(0, tk.END)
                entry_nume_client.insert(0, nume_client)

                entry_tel_client.delete(0, tk.END)
                entry_tel_client.insert(0, telefon_client)

        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare la autocompletare:\n{e}")


def on_select(event):
    selected = tree.focus()
    if not selected:
        for widget in info_frame.winfo_children():
            widget.destroy()
        return

    values = tree.item(selected)["values"]
    if not values or len(values) < 15:
        return

    for widget in info_frame.winfo_children():
        widget.destroy()

    tk.Label(info_frame, text="Detalii intervenție:", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 5))

    labels = [
        f"Data: {values[9]}",
        f"KM: {values[3]}",
        f"Factură: {values[10]}",
        f"Furnizor: {values[11]}",
        f"Nume client: {values[12]}",
        f"Telefon client: {values[13]}"
    ]

    for txt in labels:
        tk.Label(info_frame, text=txt, font=("Segoe UI", 12)).pack(anchor="w", pady=1)

    tk.Label(info_frame, text="Descriere:", font=("Segoe UI", 12, "underline")).pack(anchor="w", pady=(10, 2))
    tk.Message(info_frame, text=values[14], font=("Segoe UI", 12), width=1400, anchor="w", justify="left").pack(
        anchor="w")


# === GUI ===
root = tk.Tk()
root.title("Service Auto - Istoric Intervenții")
root.state('zoomed')

input_frame = tk.Frame(root, padx=20, pady=20)
input_frame.pack(fill="x")

# Rând 1
labels = ["Nr înmatriculare", "VIN", "Marcă", "Model"]
entries = []
for i, text in enumerate(labels):
    tk.Label(input_frame, text=text+":", font=("Segoe UI", 12)).grid(row=0, column=i*2, sticky="e", padx=5)
    entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=25)
    entry.grid(row=0, column=i*2+1, padx=5)
    entries.append(entry)
entry_nr, entry_vin, entry_marca, entry_model = entries
entry_nr.bind("<FocusOut>", autocomplete_date_masina)

# Rând 2
labels2 = ["Nr. km", "Data fabricație (MM-YYYY)", "Capacitate (cm³)", "Putere (kW)"]
entries2 = []
for i, text in enumerate(labels2):
    tk.Label(input_frame, text=text+":", font=("Segoe UI", 12)).grid(row=1, column=i*2, sticky="e", padx=5)
    entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=25)
    entry.grid(row=1, column=i*2+1, padx=5)
    entries2.append(entry)
entry_km, entry_an, entry_capacitate, entry_putere = entries2

# Rând 3
labels3 = ["Dată (intervenție)", "Nr. factură", "Furnizor piese"]
entries3 = []
for i, text in enumerate(labels3):
    tk.Label(input_frame, text=text+":", font=("Segoe UI", 12)).grid(row=2, column=i*2, sticky="e", padx=5)
    entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=25)
    entry.grid(row=2, column=i*2+1, padx=5)
    entries3.append(entry)
entry_data, entry_factura, entry_furnizor = entries3

# Rând nou - Client
tk.Label(input_frame, text="Nume client:", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
entry_nume_client = tk.Entry(input_frame, font=("Segoe UI", 12), width=25)
entry_nume_client.grid(row=3, column=1, padx=5)

tk.Label(input_frame, text="Telefon client:", font=("Segoe UI", 12)).grid(row=3, column=2, sticky="e", padx=5, pady=5)
entry_tel_client = tk.Entry(input_frame, font=("Segoe UI", 12), width=25)
entry_tel_client.grid(row=3, column=3, padx=5)

# Intervenție
tk.Label(input_frame, text="Intervenție:", font=("Segoe UI", 12)).grid(row=4, column=0, sticky="ne", padx=5, pady=5)
entry_descriere = tk.Text(input_frame, font=("Segoe UI", 12), width=130, height=4)
entry_descriere.grid(row=4, column=1, columnspan=7, padx=5, pady=5, sticky="w")

# Butoane
btn_frame = tk.Frame(root, pady=10)
btn_frame.pack()
tk.Button(btn_frame, text="Adaugă Intervenție", font=("Segoe UI", 11, "bold"), command=adauga_masina_si_interventie).pack(side="left", padx=10)
tk.Button(btn_frame, text="Afișează Istoric", font=("Segoe UI", 11, "bold"), command=afiseaza_istoric).pack(side="left", padx=10)
tk.Button(btn_frame, text="Șterge Intervenție", font=("Segoe UI", 11, "bold"), command=sterge_interventie).pack(side="left", padx=10)
tk.Button(btn_frame, text="Editează Intervenție", font=("Segoe UI", 11, "bold"), command=editeaza_interventie).pack(side="left", padx=10)


# Tabel
tree_columns = ("ID", "Nr", "VIN", "KM", "Marcă", "Model", "An", "Capacitate", "Putere", "Dată", "Factură", "Furnizor", "Nume client", "Telefon client", "Descriere")
tree = ttk.Treeview(root, columns=tree_columns, show="headings")
for col in tree_columns:
    if col == "Descriere":
        continue
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")
tree.pack(expand=True, fill="both", padx=20, pady=10)
tree.bind("<<TreeviewSelect>>", on_select)

# Info intervenție
info_frame = tk.Frame(root, padx=20, pady=10)
info_frame.pack(fill="x")

root.mainloop()