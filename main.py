import tkinter as tk
from tkinter import *
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import numpy as np
from tkinter import filedialog
import PyPDF2
import docx

root = tk.Tk()  # Tworzenie okna głównego aplikacji

# Ustawienie nazwy okna na "Sprawdź tekst"
root.title("Sprawdź tekst")

# Ustawienie domyślnej wielkości okna
root.geometry("800x500")

# Dodanie obrazka tła do okna
root.configure(bg='#a8d0ff')

# Dodanie nagłówka "Sprawdź tekst"
header = tk.Label(root, text="Sprawdź tekst", font=("Arial", 16))
header.pack(side=tk.TOP, pady=20)



# Dodanie pola tekstowego
text_input = tk.Text(width=80, height=20, wrap=WORD)
text_input.pack(side=tk.TOP, pady=10)

# Wyśrodkowanie przycisku "Sprawdź"

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"),
                                                      ("Word Files", "*.doc;*.docx")])
    if file_path.endswith(".pdf"):
        #  PDF
        pdf_file = open(file_path, "rb")
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        pdf_file.close()
    elif file_path.endswith(".doc") or file_path.endswith(".docx"):
        # .doc/docx
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    else:
        text = "Invalid file format"

    text_input.delete("1.0", tk.END)  #
    text_input.insert(tk.END, text)



def check():
    text = text_input.get("1.0", "end-1c")
    if len(text) < 20:
        print("za krotki tekst")
        return

    # Wczytanie danych z pliku CSV
    data_plagiat = pd.read_csv("dane1.csv")

    # Usunięcie zbędnych kolumn
    data_plagiat = data_plagiat.drop(['UserName', 'ScreenName', 'Location', 'TweetAt', 'Sentiment'], axis=1)
    data_plagiat['label'] = 1
    data_plagiat.rename(columns={'OriginalTweet': 'text'}, inplace=True)

    # Wczytanie danych z pliku CSV
    data_non_plagiat = pd.read_csv("dane0.csv")

    # Usunięcie zbędnych kolumn
    data_non_plagiat = data_non_plagiat.drop(['author', 'claps', 'reading_time', 'link', 'title'], axis=1)
    data_non_plagiat['label'] = 0

    # Połączenie danych z plagiatami i bez plagiatów
    data = pd.concat([data_plagiat, data_non_plagiat], ignore_index=True)

    # Podział danych na zbiór treningowy i testowy
    X_train, X_test, y_train, y_test = train_test_split(data.iloc[:, 0], data.iloc[:, 1], test_size=0.2,
                                                        random_state=42)
    print(data)
    # Tworzenie wektorów tf-idf na podstawie tekstu
    vectorizer = TfidfVectorizer()
    X_train_vectors = vectorizer.fit_transform(X_train)
    X_test_vectors = vectorizer.transform(X_test)

    # Trenowanie klasyfikatora SVM
    classifier = SVC(probability=True)
    classifier.fit(X_train_vectors, y_train)

    # Testowanie klasyfikatora
    y_pred = classifier.predict(X_test_vectors)
    y_pred_proba = classifier.predict_proba(X_test_vectors)

    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)

    # Przykładowe testowanie na pojedynczym zdaniu
    test_sentence = text
    test_sentence_vector = vectorizer.transform([test_sentence])
    test_result = classifier.predict_proba(test_sentence_vector)[0][1]
    print("Test sentence probability:", test_result)

    if test_result > 0.6:
        result_label.config(text="PLAGIAT", font=("Arial", 16))
        result_label.configure(bg='red')  # zmiana koloru tła labela na czerwony
    else:
        result_label.config(text="NIEPLAGIAT", font=("Arial", 16))
        result_label.configure(bg='green')  # zmiana koloru tła labela na zielony

    print("Sprawdzam tekst:", text)

check_button = tk.Button(text="Sprawdź", command=check, font=("Arial", 20, "bold"), height=1, width=8)
check_button.pack(side=tk.TOP, padx=10, pady=10)
check_button.place(relx=0.5, rely=0.9, anchor=CENTER)

load_button = tk.Button(root, text="Load File", command=browse_file)
load_button.pack(padx=20, pady=20,anchor=SE)

result_label = tk.Label(root, text="", font=("Arial", 24, "bold"), bg='#a8d0ff', height=1, width=10)
result_label.pack(side=tk.LEFT, pady=10, padx=10, anchor=W)
result_label.place(relx=0.1, rely=0.9)

# Uruchomienie pętli głównej aplikacji
root.mainloop()




