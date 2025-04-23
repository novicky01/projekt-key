import datetime
import json

class Osoba:
    def __init__(self, imie, nazwisko):
        self.imie = imie
        self.nazwisko = nazwisko

class Bibliotekarz(Osoba):
    def __init__(self, imie, nazwisko, login):
        super().__init__(imie, nazwisko)
        self.role = "Bibliotekarz"
        self.login = login
        self.wypozyczone_ksiazki = []

    def dodaj_ksiazke(self, biblioteka, tytul, autor, isbn):
        return biblioteka.dodaj_ksiazke(tytul, autor, isbn)

    def usun_ksiazke(self, biblioteka, isbn):
        return biblioteka.usun_ksiazke(isbn)

    def wypozycz_ksiazke(self, biblioteka, isbn):
        return biblioteka.wypozycz_ksiazke(isbn, self.login)

    def zwroc_ksiazke(self, biblioteka, isbn):
        return biblioteka.zwroc_ksiazke(isbn, self.login)

    def rezerwuj_ksiazke(self, biblioteka, isbn):
        return biblioteka.rezerwuj_ksiazke(isbn, self.login)

class Czytelnik(Osoba):
    def __init__(self, imie, nazwisko, login):
        super().__init__(imie, nazwisko)
        self.role = "Czytelnik"
        self.login = login
        self.wypozyczone_ksiazki = []

    def wypozycz_ksiazke(self, biblioteka, isbn):
        return biblioteka.wypozycz_ksiazke(isbn, self.login)

    def zwroc_ksiazke(self, biblioteka, isbn):
        return biblioteka.zwroc_ksiazke(isbn, self.login)

    def rezerwuj_ksiazke(self, biblioteka, isbn):
        return biblioteka.rezerwuj_ksiazke(isbn, self.login)

class Ksiazka:
    def __init__(self, tytul, autor, isbn):
        self.tytul = tytul
        self.autor = autor
        self.isbn = isbn
        self.status = "dostepna"  # dostepna, wypozyczona, zarezerwowana
        self.wypozyczajacy = None
        self.data_wypozyczenia = None
        self.rezerwujacy = None
        self.data_rezerwacji = None
        self.termin_zwrotu = None

class Biblioteka:
    def __init__(self):
        self.ksiazki = []
        self.uzytkownicy = []
        self.kara_za_dzien = 1.0  # kara w złotych za dzień przetrzymania

    def zapisz_ksiazki_do_json(self):
        try:
            data = {"ksiazki": []}
            for ksiazka in self.ksiazki:
                book_data = {
                    "tytul": ksiazka.tytul,
                    "autor": ksiazka.autor,
                    "isbn": ksiazka.isbn,
                    "status": ksiazka.status
                }
                if ksiazka.wypozyczajacy:
                    book_data["wypozyczajacy"] = ksiazka.wypozyczajacy
                if ksiazka.data_wypozyczenia:
                    book_data["data_wypozyczenia"] = ksiazka.data_wypozyczenia
                if ksiazka.rezerwujacy:
                    book_data["rezerwujacy"] = ksiazka.rezerwujacy
                if ksiazka.data_rezerwacji:
                    book_data["data_rezerwacji"] = ksiazka.data_rezerwacji
                if ksiazka.termin_zwrotu:
                    book_data["termin_zwrotu"] = ksiazka.termin_zwrotu
                data["ksiazki"].append(book_data)
            
            with open('books.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Błąd podczas zapisywania pliku: {str(e)}")
            return False

    def dodaj_ksiazke(self, tytul, autor, isbn):
        for ksiazka in self.ksiazki:
            if ksiazka.isbn == isbn:
                return False
        nowa_ksiazka = Ksiazka(tytul, autor, isbn)
        self.ksiazki.append(nowa_ksiazka)
        self.zapisz_ksiazki_do_json()
        return True

    def usun_ksiazke(self, isbn):
        for ksiazka in self.ksiazki:
            if ksiazka.isbn == isbn:
                if ksiazka.status == "dostepna":
                    self.ksiazki.remove(ksiazka)
                    self.zapisz_ksiazki_do_json()
                    return True
        return False

    def wypozycz_ksiazke(self, isbn, czytelnik_login):
        for ksiazka in self.ksiazki:
            if ksiazka.isbn == isbn:
                if ksiazka.status == "dostepna":
                    ksiazka.status = "wypozyczona"
                    ksiazka.wypozyczajacy = czytelnik_login
                    ksiazka.data_wypozyczenia = datetime.datetime.now().strftime("%Y-%m-%d")
                    # Ustaw termin zwrotu na 14 dni od wypożyczenia
                    ksiazka.termin_zwrotu = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
                    self.zapisz_ksiazki_do_json()
                    return True
                elif ksiazka.status == "zarezerwowana" and ksiazka.rezerwujacy == czytelnik_login:
                    ksiazka.status = "wypozyczona"
                    ksiazka.wypozyczajacy = czytelnik_login
                    ksiazka.data_wypozyczenia = datetime.datetime.now().strftime("%Y-%m-%d")
                    ksiazka.termin_zwrotu = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
                    ksiazka.rezerwujacy = None
                    ksiazka.data_rezerwacji = None
                    self.zapisz_ksiazki_do_json()
                    return True
        return False

    def zwroc_ksiazke(self, isbn, czytelnik_login):
        for ksiazka in self.ksiazki:
            if ksiazka.isbn == isbn and ksiazka.status == "wypozyczona" and ksiazka.wypozyczajacy == czytelnik_login:
                ksiazka.status = "dostepna"
                ksiazka.wypozyczajacy = None
                ksiazka.data_wypozyczenia = None
                ksiazka.termin_zwrotu = None
                self.zapisz_ksiazki_do_json()
                return True
        return False

    def rezerwuj_ksiazke(self, isbn, czytelnik_login):
        for ksiazka in self.ksiazki:
            if ksiazka.isbn == isbn:
                if ksiazka.status == "wypozyczona":
                    ksiazka.status = "zarezerwowana"
                    ksiazka.rezerwujacy = czytelnik_login
                    ksiazka.data_rezerwacji = datetime.datetime.now().strftime("%Y-%m-%d")
                    self.zapisz_ksiazki_do_json()
                    return True
        return False

    def oblicz_kare(self, isbn):
        for ksiazka in self.ksiazki:
            if ksiazka.isbn == isbn and ksiazka.status == "wypozyczona":
                if ksiazka.termin_zwrotu:
                    termin = datetime.datetime.strptime(ksiazka.termin_zwrotu, "%Y-%m-%d")
                    dzisiaj = datetime.datetime.now()
                    if dzisiaj > termin:
                        roznica = dzisiaj - termin
                        return roznica.days * self.kara_za_dzien
        return 0.0

    def znajdz_ksiazke(self, isbn):
        for ksiazka in self.ksiazki:
            if ksiazka.isbn == isbn:
                return ksiazka
        return None

    def lista_dostepnych_ksiazek(self):
        return [ksiazka for ksiazka in self.ksiazki if ksiazka.status == "dostepna"]

    def lista_wypozyczonych_ksiazek(self):
        return [ksiazka for ksiazka in self.ksiazki if ksiazka.status == "wypozyczona"]

    def lista_zarezerwowanych_ksiazek(self):
        return [ksiazka for ksiazka in self.ksiazki if ksiazka.status == "zarezerwowana"] 