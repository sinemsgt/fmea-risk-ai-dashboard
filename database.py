import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect("fmea_kayitlari.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS risk_kayitlari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarih TEXT,
    hata_kodu TEXT,
    hata_turu TEXT,
    proses TEXT,
    istasyon TEXT,
    vardiya TEXT,
    O INTEGER,
    S INTEGER,
    D INTEGER,
    geleneksel_rpn INTEGER,
    agirlikli_rpn REAL,
    ml_rpn REAL,
    risk_seviyesi TEXT,
    onlem TEXT
)
""")

conn.commit()


def kayit_ekle(hata_kodu, hata_turu, proses, istasyon, vardiya,
               O, S, D, geleneksel_rpn, agirlikli_rpn,
               ml_rpn, risk_seviyesi, onlem):
    cursor.execute("""
    INSERT INTO risk_kayitlari (
        tarih, hata_kodu, hata_turu, proses, istasyon, vardiya,
        O, S, D, geleneksel_rpn, agirlikli_rpn,
        ml_rpn, risk_seviyesi, onlem
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        hata_kodu,
        hata_turu,
        proses,
        istasyon,
        vardiya,
        O,
        S,
        D,
        geleneksel_rpn,
        agirlikli_rpn,
        ml_rpn,
        risk_seviyesi,
        onlem
    ))

    conn.commit()


def kayitlari_getir():
    return pd.read_sql_query(
        "SELECT * FROM risk_kayitlari ORDER BY id DESC",
        conn
    )