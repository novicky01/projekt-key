import tkinter
from tkinter import ttk
import sv_ttk
from tkinter import font
import json
from tkinter import messagebox
from models.classes import Osoba, Bibliotekarz, Czytelnik, Ksiazka, Biblioteka
import datetime

def wczytaj_ksiazki_z_json():
    try:
        with open('books.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            for book_data in data['ksiazki']:
                ksiazka = Ksiazka(book_data['tytul'], book_data['autor'], book_data['isbn'])
                ksiazka.status = book_data['status']
                if 'wypozyczajacy' in book_data:
                    ksiazka.wypozyczajacy = book_data['wypozyczajacy']
                if 'data_wypozyczenia' in book_data:
                    ksiazka.data_wypozyczenia = book_data['data_wypozyczenia']
                biblioteka.ksiazki.append(ksiazka)
    except FileNotFoundError:
        messagebox.showerror("Błąd", "Plik books.json nie istnieje!")
    except json.JSONDecodeError:
        messagebox.showerror("Błąd", "Nieprawidłowy format pliku books.json!")

root = tkinter.Tk()
root.geometry("300x350")
sv_ttk.set_theme("dark")

# Inicjalizacja biblioteki
biblioteka = Biblioteka()
wczytaj_ksiazki_z_json()
current_user = None

def selectScreen(actualScreen, newScreen):
    if actualScreen != None:
        actualScreen.pack_forget()
    newScreen.pack()

def checkLogin():
    global current_user
    try:
        with open('users.json', 'r') as file:
            users = json.load(file)
            
        login = login_entry.get()
        password = password_entry.get()
        
        for user in users['users']:
            if user['login'] == login and user['password'] == password:
                # Tworzenie odpowiedniego obiektu użytkownika w zależności od roli
                if user['role'] == "Bibliotekarz":
                    current_user = Bibliotekarz(user['imie'], user['nazwisko'], user['login'])
                else:  # Czytelnik
                    current_user = Czytelnik(user['imie'], user['nazwisko'], user['login'])
                
                messagebox.showinfo("Sukces", f"Zalogowano pomyślnie jako {user['role']}!")
                role_label.config(text=f"Zalogowano jako: {user['role']}")
                login_entry.delete(0, 'end')
                password_entry.delete(0, 'end')
                
                # Aktualizacja przycisków w zależności od roli
                if user['role'] == "Bibliotekarz":
                    add_book_button.pack(pady=5)
                    remove_book_button.pack(pady=5)
                    borrow_book_button.pack(pady=5)
                    return_book_button.pack(pady=5)
                    reserve_book_button.pack(pady=5)
                    check_penalty_button.pack(pady=5)
                else:  # Czytelnik
                    add_book_button.pack_forget()
                    remove_book_button.pack_forget()
                    borrow_book_button.pack(pady=5)
                    return_book_button.pack(pady=5)
                    reserve_book_button.pack(pady=5)
                    check_penalty_button.pack(pady=5)
                
                # Odśwież listę książek
                refresh_books_list()
                root.geometry("900x600")
                selectScreen(ekran1, ekran2)
                return
                
        messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło!")
    except FileNotFoundError:
        messagebox.showerror("Błąd", "Plik users.json nie istnieje!")
    except json.JSONDecodeError:
        messagebox.showerror("Błąd", "Nieprawidłowy format pliku users.json!")

def refresh_books_list():
    # Czyszczenie listy
    for item in books_tree.get_children():
        books_tree.delete(item)
    
    # Wczytywanie książek z biblioteki
    for ksiazka in biblioteka.ksiazki:
        status = "Dostępna" if ksiazka.status == "dostepna" else "Wypożyczona"
        books_tree.insert('', 'end', values=(
            ksiazka.tytul,
            ksiazka.autor,
            ksiazka.isbn,
            status
        ))

def dodaj_ksiazke():
    add_window = tkinter.Toplevel(root)
    add_window.title("Dodaj książkę")
    add_window.geometry("300x200")
    
    ttk.Label(add_window, text="Tytuł:").pack(pady=5)
    tytul_entry = ttk.Entry(add_window)
    tytul_entry.pack(pady=5)
    
    ttk.Label(add_window, text="Autor:").pack(pady=5)
    autor_entry = ttk.Entry(add_window)
    autor_entry.pack(pady=5)
    
    ttk.Label(add_window, text="ISBN:").pack(pady=5)
    isbn_entry = ttk.Entry(add_window)
    isbn_entry.pack(pady=5)
    
    def zapisz_ksiazke():
        tytul = tytul_entry.get()
        autor = autor_entry.get()
        isbn = isbn_entry.get()
        
        if current_user and isinstance(current_user, Bibliotekarz):
            if current_user.dodaj_ksiazke(biblioteka, tytul, autor, isbn):
                messagebox.showinfo("Sukces", "Książka została dodana!")
                refresh_books_list()
                add_window.destroy()
            else:
                messagebox.showerror("Błąd", "Książka o podanym ISBN już istnieje!")
        else:
            messagebox.showerror("Błąd", "Brak uprawnień do dodawania książek!")
    
    ttk.Button(add_window, text="Dodaj", command=zapisz_ksiazke).pack(pady=10)
    ttk.Button(add_window, text="Anuluj", command=add_window.destroy).pack(pady=5)

def usun_ksiazke():
    selected_item = books_tree.selection()
    if not selected_item:
        messagebox.showerror("Błąd", "Wybierz książkę do usunięcia!")
        return
    
    isbn = books_tree.item(selected_item[0])['values'][2]
    
    if current_user and isinstance(current_user, Bibliotekarz):
        if current_user.usun_ksiazke(biblioteka, isbn):
            messagebox.showinfo("Sukces", "Książka została usunięta!")
            refresh_books_list()
        else:
            messagebox.showerror("Błąd", "Nie można usunąć wypożyczonej książki!")
    else:
        messagebox.showerror("Błąd", "Brak uprawnień do usuwania książek!")

def wypozycz_ksiazke():
    selected_item = books_tree.selection()
    if not selected_item:
        messagebox.showerror("Błąd", "Wybierz książkę do wypożyczenia!")
        return
    
    isbn = books_tree.item(selected_item[0])['values'][2]
    
    if current_user and (isinstance(current_user, Czytelnik) or isinstance(current_user, Bibliotekarz)):
        if current_user.wypozycz_ksiazke(biblioteka, isbn):
            messagebox.showinfo("Sukces", "Książka została wypożyczona!")
            refresh_books_list()
        else:
            messagebox.showerror("Błąd", "Książka jest już wypożyczona!")
    else:
        messagebox.showerror("Błąd", "Brak uprawnień do wypożyczania książek!")

def zwroc_ksiazke():
    if not current_user or not (isinstance(current_user, Czytelnik) or isinstance(current_user, Bibliotekarz)):
        messagebox.showerror("Błąd", "Brak uprawnień do zwracania książek!")
        return

    # Znajdź książki wypożyczone przez aktualnego użytkownika
    borrowed_books = [ksiazka for ksiazka in biblioteka.ksiazki 
                     if ksiazka.status == "wypozyczona" and ksiazka.wypozyczajacy == current_user.login]
    
    if not borrowed_books:
        messagebox.showinfo("Informacja", "Nie masz wypożyczonych książek!")
        return
    
    # Utwórz okno z listą książek
    return_window = tkinter.Toplevel(root)
    return_window.title("Zwróć książkę")
    return_window.geometry("600x400")
    
    ttk.Label(return_window, text="Wybierz książkę do zwrotu:").pack(pady=10)
    
    # Lista książek
    books_list = ttk.Treeview(return_window, columns=('Tytuł', 'Autor', 'ISBN'), show='headings')
    books_list.heading('Tytuł', text='Tytuł')
    books_list.heading('Autor', text='Autor')
    books_list.heading('ISBN', text='ISBN')
    
    for ksiazka in borrowed_books:
        books_list.insert('', 'end', values=(
            ksiazka.tytul,
            ksiazka.autor,
            ksiazka.isbn
        ))
    
    books_list.pack(pady=10, fill='both', expand=True)
    
    def wykonaj_zwrot():
        selected_item = books_list.selection()
        if not selected_item:
            messagebox.showerror("Błąd", "Wybierz książkę do zwrotu!")
            return
        
        isbn = books_list.item(selected_item[0])['values'][2]
        
        if current_user.zwroc_ksiazke(biblioteka, isbn):
            messagebox.showinfo("Sukces", "Książka została zwrócona!")
            refresh_books_list()
            return_window.destroy()
        else:
            messagebox.showerror("Błąd", "Nie możesz zwrócić tej książki!")
    
    # Przyciski
    button_frame = ttk.Frame(return_window)
    button_frame.pack(pady=10)
    
    ttk.Button(button_frame, text="Zwróć", command=wykonaj_zwrot).pack(side='left', padx=5)
    ttk.Button(button_frame, text="Anuluj", command=return_window.destroy).pack(side='left', padx=5)

def wyszukaj_ksiazke():
    search_window = tkinter.Toplevel(root)
    search_window.title("Wyszukaj książkę")
    search_window.geometry("300x150")
    
    ttk.Label(search_window, text="Wyszukaj po:").pack(pady=5)
    search_var = tkinter.StringVar()
    search_combo = ttk.Combobox(search_window, textvariable=search_var)
    search_combo['values'] = ('Tytuł', 'Autor', 'ISBN')
    search_combo.pack(pady=5)
    
    ttk.Label(search_window, text="Szukana fraza:").pack(pady=5)
    search_entry = ttk.Entry(search_window)
    search_entry.pack(pady=5)
    
    def wykonaj_wyszukiwanie():
        search_type = search_var.get()
        search_phrase = search_entry.get().lower()
        
        if not search_type or not search_phrase:
            messagebox.showerror("Błąd", "Wypełnij wszystkie pola!")
            return
        
        found_books = []
        for ksiazka in biblioteka.ksiazki:
            if search_type == "Tytuł" and search_phrase in ksiazka.tytul.lower():
                found_books.append(ksiazka)
            elif search_type == "Autor" and search_phrase in ksiazka.autor.lower():
                found_books.append(ksiazka)
            elif search_type == "ISBN" and search_phrase in ksiazka.isbn.lower():
                found_books.append(ksiazka)
        
        if found_books:
            result_window = tkinter.Toplevel(root)
            result_window.title("Wyniki wyszukiwania")
            result_window.geometry("600x400")
            
            result_tree = ttk.Treeview(result_window, columns=('Tytuł', 'Autor', 'ISBN', 'Status'), show='headings')
            result_tree.heading('Tytuł', text='Tytuł')
            result_tree.heading('Autor', text='Autor')
            result_tree.heading('ISBN', text='ISBN')
            result_tree.heading('Status', text='Status')
            
            for ksiazka in found_books:
                status = "Dostępna" if ksiazka.status == "dostepna" else "Wypożyczona"
                result_tree.insert('', 'end', values=(
                    ksiazka.tytul,
                    ksiazka.autor,
                    ksiazka.isbn,
                    status
                ))
            
            result_tree.pack(fill='both', expand=True)
            ttk.Button(result_window, text="Zamknij", command=result_window.destroy).pack(pady=10)
        else:
            messagebox.showinfo("Informacja", "Nie znaleziono książek spełniających kryteria wyszukiwania.")
        
        search_window.destroy()
    
    ttk.Button(search_window, text="Szukaj", command=wykonaj_wyszukiwanie).pack(pady=10)
    ttk.Button(search_window, text="Anuluj", command=search_window.destroy).pack(pady=5)

def rezerwuj_ksiazke():
    selected_item = books_tree.selection()
    if not selected_item:
        messagebox.showerror("Błąd", "Wybierz książkę do rezerwacji!")
        return
    
    isbn = books_tree.item(selected_item[0])['values'][2]
    
    if current_user and (isinstance(current_user, Czytelnik) or isinstance(current_user, Bibliotekarz)):
        if current_user.rezerwuj_ksiazke(biblioteka, isbn):
            messagebox.showinfo("Sukces", "Książka została zarezerwowana!")
            refresh_books_list()
        else:
            messagebox.showerror("Błąd", "Nie można zarezerwować tej książki!")
    else:
        messagebox.showerror("Błąd", "Brak uprawnień do rezerwowania książek!")

def sprawdz_kare():
    if not current_user or not (isinstance(current_user, Czytelnik) or isinstance(current_user, Bibliotekarz)):
        messagebox.showerror("Błąd", "Brak uprawnień do sprawdzania kar!")
        return

    # Znajdź książki wypożyczone przez aktualnego użytkownika
    borrowed_books = [ksiazka for ksiazka in biblioteka.ksiazki 
                     if ksiazka.status == "wypozyczona" and ksiazka.wypozyczajacy == current_user.login]
    
    if not borrowed_books:
        messagebox.showinfo("Informacja", "Nie masz wypożyczonych książek!")
        return
    
    # Utwórz okno z listą książek i kar
    kara_window = tkinter.Toplevel(root)
    kara_window.title("Sprawdź kary")
    kara_window.geometry("600x400")
    
    ttk.Label(kara_window, text="Twoje wypożyczone książki i kary:").pack(pady=10)
    
    # Lista książek
    books_list = ttk.Treeview(kara_window, columns=('Tytuł', 'Autor', 'ISBN', 'Termin zwrotu', 'Kara'), show='headings')
    books_list.heading('Tytuł', text='Tytuł')
    books_list.heading('Autor', text='Autor')
    books_list.heading('ISBN', text='ISBN')
    books_list.heading('Termin zwrotu', text='Termin zwrotu')
    books_list.heading('Kara', text='Kara (zł)')
    
    for ksiazka in borrowed_books:
        kara = biblioteka.oblicz_kare(ksiazka.isbn)
        books_list.insert('', 'end', values=(
            ksiazka.tytul,
            ksiazka.autor,
            ksiazka.isbn,
            ksiazka.termin_zwrotu,
            f"{kara:.2f}"
        ))
    
    books_list.pack(pady=10, fill='both', expand=True)
    
    ttk.Button(kara_window, text="Zamknij", command=kara_window.destroy).pack(pady=10)

inter_font = font.Font(family="Inter", size=24)

ekran1 = ttk.Frame(root)
ttk.Label(ekran1, text="Biblioteka szkolna", font=inter_font).pack(pady=20)

login_frame = ttk.Frame(ekran1)
login_frame.pack(pady=20)

ttk.Label(login_frame, text="Login:").grid(row=0, column=0, padx=5, pady=5)
login_entry = ttk.Entry(login_frame)
login_entry.grid(row=0, column=1, padx=5, pady=5)
login_entry.bind('<Return>', lambda e: checkLogin())

ttk.Label(login_frame, text="Hasło:").grid(row=1, column=0, padx=5, pady=5)
password_entry = ttk.Entry(login_frame, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)
password_entry.bind('<Return>', lambda e: checkLogin())

ttk.Button(ekran1, text="Zaloguj się", command=checkLogin).pack(pady=20)

ekran2 = ttk.Frame(root)
ttk.Label(ekran2, text="Biblioteka szkolna", font=inter_font).pack(pady=10)
role_label = ttk.Label(ekran2, text="Nie zalogowano")
role_label.pack(pady=5)

# Przyciski dla bibliotekarza
add_book_button = ttk.Button(ekran2, text="Dodaj książkę", command=dodaj_ksiazke)
add_book_button.pack_forget()
remove_book_button = ttk.Button(ekran2, text="Usuń książkę", command=usun_ksiazke)
remove_book_button.pack_forget()

# Przyciski dla czytelnika
borrow_book_button = ttk.Button(ekran2, text="Wypożycz książkę", command=wypozycz_ksiazke)
borrow_book_button.pack_forget()
return_book_button = ttk.Button(ekran2, text="Zwróć książkę", command=zwroc_ksiazke)
return_book_button.pack_forget()

# Przycisk wyszukiwania dla wszystkich
search_button = ttk.Button(ekran2, text="Wyszukaj książkę", command=wyszukaj_ksiazke)
search_button.pack(pady=5)

# Lista książek
books_frame = ttk.Frame(ekran2)
books_frame.pack(pady=10, fill='both', expand=True)

books_tree = ttk.Treeview(books_frame, columns=('Tytuł', 'Autor', 'ISBN', 'Status'), show='headings')
books_tree.heading('Tytuł', text='Tytuł')
books_tree.heading('Autor', text='Autor')
books_tree.heading('ISBN', text='ISBN')
books_tree.heading('Status', text='Status')
books_tree.pack(fill='both', expand=True)

# Dodaj nowe przyciski do ekranu głównego
reserve_book_button = ttk.Button(ekran2, text="Zarezerwuj książkę", command=rezerwuj_ksiazke)
reserve_book_button.pack_forget()
check_penalty_button = ttk.Button(ekran2, text="Sprawdź kary", command=sprawdz_kare)
check_penalty_button.pack_forget()

ttk.Button(ekran2, text="Wyloguj", command=lambda: selectScreen(ekran2, ekran1)).pack(pady=10)

ekran1.pack()


root.mainloop()