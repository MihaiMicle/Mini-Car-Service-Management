import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database


class ServiceAutoApp:
    def __init__(self):
        self.conn = database.get_connection()
        database.init_db(self.conn)

        self.root = tk.Tk()
        self.root.title("Service Auto - Istoric Intervenții")
        self.root.state("zoomed")

        self._build_input_frame()
        self._build_buttons()
        self._build_table()
        self._build_info_frame()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_input_frame(self):
        input_frame = tk.Frame(self.root, padx=20, pady=20)
        input_frame.pack(fill="x")

        # Rând 1
        labels = ["Nr înmatriculare", "VIN", "Marcă", "Model"]
        entries = []
        for i, text in enumerate(labels):
            tk.Label(input_frame, text=text + ":", font=("Segoe UI", 12)).grid(
                row=0, column=i * 2, sticky="e", padx=5
            )
            entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=25)
            entry.grid(row=0, column=i * 2 + 1, padx=5)
            entries.append(entry)
        self.entry_nr, self.entry_vin, self.entry_marca, self.entry_model = entries
        self.entry_nr.bind("<FocusOut>", self.autocomplete_date_masina)

        # Rând 2
        labels2 = [
            "Nr. km",
            "Data fabricație (MM-YYYY)",
            "Capacitate (cm³)",
            "Putere (kW)",
        ]
        entries2 = []
        for i, text in enumerate(labels2):
            tk.Label(input_frame, text=text + ":", font=("Segoe UI", 12)).grid(
                row=1, column=i * 2, sticky="e", padx=5
            )
            entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=25)
            entry.grid(row=1, column=i * 2 + 1, padx=5)
            entries2.append(entry)
        self.entry_km, self.entry_an, self.entry_capacitate, self.entry_putere = (
            entries2
        )

        # Rând 3
        labels3 = ["Dată (intervenție)", "Nr. factură", "Furnizor piese"]
        entries3 = []
        for i, text in enumerate(labels3):
            tk.Label(input_frame, text=text + ":", font=("Segoe UI", 12)).grid(
                row=2, column=i * 2, sticky="e", padx=5
            )
            entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=25)
            entry.grid(row=2, column=i * 2 + 1, padx=5)
            entries3.append(entry)
        self.entry_data, self.entry_factura, self.entry_furnizor = entries3

        # Client
        tk.Label(input_frame, text="Nume client:", font=("Segoe UI", 12)).grid(
            row=3, column=0, sticky="e", padx=5, pady=5
        )
        self.entry_nume_client = tk.Entry(input_frame, font=("Segoe UI", 12), width=25)
        self.entry_nume_client.grid(row=3, column=1, padx=5)

        tk.Label(input_frame, text="Telefon client:", font=("Segoe UI", 12)).grid(
            row=3, column=2, sticky="e", padx=5, pady=5
        )
        self.entry_tel_client = tk.Entry(input_frame, font=("Segoe UI", 12), width=25)
        self.entry_tel_client.grid(row=3, column=3, padx=5)

        # Intervenție
        tk.Label(input_frame, text="Intervenție:", font=("Segoe UI", 12)).grid(
            row=4, column=0, sticky="ne", padx=5, pady=5
        )
        self.entry_descriere = tk.Text(
            input_frame, font=("Segoe UI", 12), width=130, height=4
        )
        self.entry_descriere.grid(
            row=4, column=1, columnspan=7, padx=5, pady=5, sticky="w"
        )

    def _build_buttons(self):
        btn_frame = tk.Frame(self.root, pady=10)
        btn_frame.pack()
        tk.Button(
            btn_frame,
            text="Adaugă Intervenție",
            font=("Segoe UI", 11, "bold"),
            command=self.adauga_masina_si_interventie,
        ).pack(side="left", padx=10)
        tk.Button(
            btn_frame,
            text="Afișează Istoric",
            font=("Segoe UI", 11, "bold"),
            command=self.afiseaza_istoric,
        ).pack(side="left", padx=10)
        tk.Button(
            btn_frame,
            text="Șterge Intervenție",
            font=("Segoe UI", 11, "bold"),
            command=self.sterge_interventie,
        ).pack(side="left", padx=10)
        tk.Button(
            btn_frame,
            text="Editează Intervenție",
            font=("Segoe UI", 11, "bold"),
            command=self.editeaza_interventie,
        ).pack(side="left", padx=10)

    def _build_table(self):
        self.tree_columns = (
            "ID",
            "Nr",
            "VIN",
            "KM",
            "Marcă",
            "Model",
            "An",
            "Capacitate",
            "Putere",
            "Dată",
            "Factură",
            "Furnizor",
            "Nume client",
            "Telefon client",
            "Descriere",
        )
        self.tree = ttk.Treeview(self.root, columns=self.tree_columns, show="headings")
        for col in self.tree_columns:
            if col == "Descriere":
                continue
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _build_info_frame(self):
        self.info_frame = tk.Frame(self.root, padx=20, pady=10)
        self.info_frame.pack(fill="x")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def adauga_masina_si_interventie(self):
        nr = self.entry_nr.get().strip().upper()
        vin = self.entry_vin.get().strip()
        marca = self.entry_marca.get().strip()
        model = self.entry_model.get().strip()
        an = self.entry_an.get().strip()
        capacitate = self.entry_capacitate.get().strip()
        putere = self.entry_putere.get().strip()
        data = self.entry_data.get().strip()
        descriere = self.entry_descriere.get("1.0", tk.END).strip()
        km = self.entry_km.get().strip()
        factura = self.entry_factura.get().strip()
        furnizor = self.entry_furnizor.get().strip()
        nume_client = self.entry_nume_client.get().strip()
        tel_client = self.entry_tel_client.get().strip()

        if not (nr and descriere):
            messagebox.showerror(
                "Eroare",
                "Completează cel puțin numărul de înmatriculare și intervenția.",
            )
            return

        if not data:
            data = datetime.now().strftime("%d-%m-%Y")

        masina = {
            "nr_inmatriculare": nr,
            "vin": vin,
            "marca": marca,
            "model": model,
            "data_fabricatie": an,
            "capacitate_cm3": capacitate,
            "putere_kw": putere,
        }
        interventie = {
            "data": data,
            "descriere": descriere,
            "km": km,
            "nr_factura": factura,
            "furnizor_piese": furnizor,
            "nume_client": nume_client,
            "telefon_client": tel_client,
        }
        database.add_masina_si_interventie(self.conn, masina, interventie)

        messagebox.showinfo("Succes", "Intervenție adăugată cu succes!")

        for entry in [
            self.entry_descriere,
            self.entry_data,
            self.entry_km,
            self.entry_factura,
            self.entry_furnizor,
            self.entry_nume_client,
            self.entry_tel_client,
        ]:
            if isinstance(entry, tk.Text):
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)

    def afiseaza_istoric(self):
        popup = tk.Toplevel(self.root)
        popup.title("Caută istoric după nr. înmatriculare")
        popup.geometry("400x120")
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text="Număr înmatriculare:", font=("Segoe UI", 12)).pack(
            pady=10
        )
        entry_popup = tk.Entry(popup, font=("Segoe UI", 12), width=30)
        entry_popup.pack()
        entry_popup.focus()

        def cauta_si_afiseaza():
            nr_cautat = entry_popup.get().strip().upper()
            popup.destroy()
            if not nr_cautat:
                messagebox.showwarning(
                    "Avertisment", "Introdu un număr de înmatriculare."
                )
                return

            for row in self.tree.get_children():
                self.tree.delete(row)

            results = database.get_istoric_by_plate(self.conn, nr_cautat)
            if not results:
                messagebox.showinfo(
                    "Info", f"Nicio intervenție găsită pentru: {nr_cautat}"
                )
            else:
                for row in results:
                    self.tree.insert("", "end", values=row)

        tk.Button(
            popup,
            text="Caută",
            font=("Segoe UI", 11, "bold"),
            command=cauta_si_afiseaza,
        ).pack(pady=10)

    def sterge_interventie(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selectează", "Selectează o intervenție din tabel.")
            return

        values = self.tree.item(selected)["values"]
        if not values:
            return

        confirm = messagebox.askyesno(
            "Confirmare", "Ești sigur că vrei să ștergi această intervenție?"
        )
        if not confirm:
            return

        interventie_id = values[0]
        database.delete_interventie(self.conn, interventie_id)
        self.tree.delete(selected)

        for widget in self.info_frame.winfo_children():
            widget.destroy()

        messagebox.showinfo("Șters", "Intervenția a fost ștearsă cu succes.")

    def editeaza_interventie(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selectează", "Selectează o intervenție din tabel.")
            return

        values = self.tree.item(selected)["values"]
        if not values or len(values) < 15:
            return

        popup = tk.Toplevel(self.root)
        popup.title("Editează Intervenția")
        popup.geometry("800x500")
        popup.transient(self.root)
        popup.grab_set()

        fields = [
            "KM",
            "Dată",
            "Factură",
            "Furnizor",
            "Nume client",
            "Telefon client",
            "Descriere",
        ]
        field_value_index = [3, 9, 10, 11, 12, 13]
        entries = {}

        for i, field in enumerate(fields):
            tk.Label(popup, text=field + ":", font=("Segoe UI", 12)).grid(
                row=i, column=0, sticky="e", padx=10, pady=5
            )
            if field == "Descriere":
                txt = tk.Text(popup, font=("Segoe UI", 12), width=80, height=6)
                txt.insert("1.0", values[14])
                txt.grid(row=i, column=1, padx=10, pady=5)
                entries[field] = txt
            else:
                entry = tk.Entry(popup, font=("Segoe UI", 12), width=50)
                entry.insert(0, values[field_value_index[fields.index(field)]])
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

                database.update_interventie(
                    self.conn,
                    values[0],
                    km,
                    data,
                    factura,
                    furnizor,
                    nume,
                    telefon,
                    descriere,
                )
                popup.destroy()
                self.afiseaza_istoric()
                messagebox.showinfo("Salvat", "Modificările au fost salvate.")
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la salvare: {e}")

        tk.Button(
            popup,
            text="Salvează modificările",
            font=("Segoe UI", 11, "bold"),
            command=salveaza_modificari,
        ).grid(row=len(fields), columnspan=2, pady=20)

    def autocomplete_date_masina(self, event=None):
        nr_inmatriculare = self.entry_nr.get().strip().upper()
        if not nr_inmatriculare:
            return

        try:
            masina = database.get_masina_by_plate(self.conn, nr_inmatriculare)
            if masina:
                _, _, vin, marca, model, data_fabricatie, capacitate, putere = masina

                self.entry_vin.delete(0, tk.END)
                self.entry_vin.insert(0, vin)

                self.entry_marca.delete(0, tk.END)
                self.entry_marca.insert(0, marca)

                self.entry_model.delete(0, tk.END)
                self.entry_model.insert(0, model)

                self.entry_an.delete(0, tk.END)
                self.entry_an.insert(0, data_fabricatie)

                self.entry_capacitate.delete(0, tk.END)
                self.entry_capacitate.insert(0, capacitate)

                self.entry_putere.delete(0, tk.END)
                self.entry_putere.insert(0, putere)

            client = database.get_last_client_for_masina(self.conn, nr_inmatriculare)
            if client:
                nume_client, telefon_client = client

                self.entry_nume_client.delete(0, tk.END)
                self.entry_nume_client.insert(0, nume_client)

                self.entry_tel_client.delete(0, tk.END)
                self.entry_tel_client.insert(0, telefon_client)

        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare la autocompletare:\n{e}")

    def on_select(self, event):
        selected = self.tree.focus()
        if not selected:
            for widget in self.info_frame.winfo_children():
                widget.destroy()
            return

        values = self.tree.item(selected)["values"]
        if not values or len(values) < 15:
            return

        for widget in self.info_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.info_frame, text="Detalii intervenție:", font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 5))

        labels = [
            f"Data: {values[9]}",
            f"KM: {values[3]}",
            f"Factură: {values[10]}",
            f"Furnizor: {values[11]}",
            f"Nume client: {values[12]}",
            f"Telefon client: {values[13]}",
        ]

        for txt in labels:
            tk.Label(self.info_frame, text=txt, font=("Segoe UI", 12)).pack(
                anchor="w", pady=1
            )

        tk.Label(
            self.info_frame, text="Descriere:", font=("Segoe UI", 12, "underline")
        ).pack(anchor="w", pady=(10, 2))
        tk.Message(
            self.info_frame,
            text=values[14],
            font=("Segoe UI", 12),
            width=1400,
            anchor="w",
            justify="left",
        ).pack(anchor="w")

    
    def run(self):
        self.root.mainloop()
