import sqlite3

DB_NAME = "service_auto.db"


def get_connection(db_name: str = DB_NAME) -> sqlite3.Connection:
    """Open (or create) the SQLite database file."""
    return sqlite3.connect(db_name)


def init_db(conn: sqlite3.Connection) -> None:
    """Create the required tables if they don't already exist."""
    cursor = conn.cursor()

    cursor.execute("""
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
    """)

    cursor.execute("""
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
    """)

    conn.commit()


def get_masina_by_plate(conn: sqlite3.Connection, nr_inmatriculare: str):
    """Return the full 'masini' row for a plate number, or None if not found."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM masini WHERE nr_inmatriculare=?", (nr_inmatriculare,))
    return cursor.fetchone()


def get_last_client_for_masina(conn: sqlite3.Connection, nr_inmatriculare: str):
    """Return (nume_client, telefon_client) from the car's most recent intervention."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT i.nume_client, i.telefon_client
        FROM interventii i
        JOIN masini m ON i.masina_id = m.id
        WHERE m.nr_inmatriculare = ?
        ORDER BY i.data DESC
        LIMIT 1
    """,
        (nr_inmatriculare,),
    )
    return cursor.fetchone()


def add_masina_si_interventie(
    conn: sqlite3.Connection, masina: dict, interventie: dict
) -> None:
    """
    Insert a new intervention, creating the car record first if a car
    with the same plate number doesn't already exist.

    masina: dict with keys nr_inmatriculare, vin, marca, model,
            data_fabricatie, capacitate_cm3, putere_kw
    interventie: dict with keys data, descriere, km, nr_factura,
                 furnizor_piese, nume_client, telefon_client
    """
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM masini WHERE nr_inmatriculare=?",
        (masina["nr_inmatriculare"],),
    )
    row = cursor.fetchone()

    if row:
        masina_id = row[0]
    else:
        cursor.execute(
            """
            INSERT INTO masini (nr_inmatriculare, vin, marca, model, data_fabricatie, capacitate_cm3, putere_kw)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                masina["nr_inmatriculare"],
                masina["vin"],
                masina["marca"],
                masina["model"],
                masina["data_fabricatie"],
                masina["capacitate_cm3"],
                masina["putere_kw"],
            ),
        )
        masina_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO interventii (masina_id, data, descriere, km, nr_factura, furnizor_piese, nume_client, telefon_client)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            masina_id,
            interventie["data"],
            interventie["descriere"],
            interventie["km"],
            interventie["nr_factura"],
            interventie["furnizor_piese"],
            interventie["nume_client"],
            interventie["telefon_client"],
        ),
    )

    conn.commit()


def get_istoric_by_plate(conn: sqlite3.Connection, nr_inmatriculare: str):
    """Return every intervention for a car, most recent first."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT i.id, m.nr_inmatriculare, m.vin, i.km, m.marca, m.model, m.data_fabricatie,
               m.capacitate_cm3, m.putere_kw, i.data, i.nr_factura, i.furnizor_piese,
               i.nume_client, i.telefon_client, i.descriere
        FROM interventii i
        JOIN masini m ON i.masina_id = m.id
        WHERE m.nr_inmatriculare=?
        ORDER BY i.data DESC
    """,
        (nr_inmatriculare,),
    )
    return cursor.fetchall()


def delete_interventie(conn: sqlite3.Connection, interventie_id) -> None:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM interventii WHERE id=?", (interventie_id,))
    conn.commit()


def update_interventie(
    conn: sqlite3.Connection,
    interventie_id,
    km,
    data,
    nr_factura,
    furnizor_piese,
    nume_client,
    telefon_client,
    descriere,
) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE interventii
        SET km=?, data=?, nr_factura=?, furnizor_piese=?, nume_client=?, telefon_client=?, descriere=?
        WHERE id=?
    """,
        (
            km,
            data,
            nr_factura,
            furnizor_piese,
            nume_client,
            telefon_client,
            descriere,
            interventie_id,
        ),
    )
    conn.commit()
