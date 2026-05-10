import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    classification_report
)

from modules.data import *
def nlp_modeli_egit(df):
    X_text = df["Hata_Aciklamasi"]
    y = df["Hata_Kodu"]
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4),
                                  max_features=500, sublinear_tf=True)
    X = vectorizer.fit_transform(X_text)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.25, random_state=42, stratify=y_enc)
    model = MultinomialNB(alpha=0.8)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    cv_scores = cross_val_score(model, X, y_enc, cv=5, scoring="accuracy")
    rapor = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True)
    return model, vectorizer, le, rapor, cv_scores
def rf_modeli_egit(df):
    df2 = df.copy()
    encoders = {}
    for col in ["Hata_Kodu", "Vardiya", "Istasyon"]:
        le = LabelEncoder()
        df2[col + "_enc"] = le.fit_transform(df2[col])
        encoders[col] = le
    ozellikler = ["O", "S", "D", "Hata_Kodu_enc", "Vardiya_enc", "Istasyon_enc", "Ay", "Hafta"]
    X = df2[ozellikler]
    y = df2["RPN"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=200, max_depth=12,
                                min_samples_split=4, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    importances = pd.Series(rf.feature_importances_, index=ozellikler)
    return rf, encoders, mae, r2, importances, y_test, y_pred