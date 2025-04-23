# System Biblioteki Szkolnej

## Opis Systemu
System zarządzania biblioteką szkolną umożliwiający katalogowanie książek oraz obsługę wypożyczeń.

## Struktura Klas

### Osoba (Klasa Bazowa)
- Podstawowa klasa zawierająca dane osobowe
- Atrybuty: imię, nazwisko, ID
- Poziom uprawnień: 1 (podstawowy dostęp)

### Bibliotekarz (Dziedziczy po Osoba)
- Zarządza księgozbiorem
- Może dodawać i usuwać książki
- Może modyfikować dane książek
- Poziom uprawnień: 4-5 (pełny dostęp administracyjny)

### Czytelnik (Dziedziczy po Osoba)
- Może przeglądać dostępne książki
- Może wypożyczać i zwracać książki
- Może sprawdzać historię swoich wypożyczeń
- Poziom uprawnień: 2-3 (dostęp użytkownika)

### Książka
Atrybuty:
- Tytuł
- Autor
- ISBN
- Status dostępności
- Data dodania
- Historia wypożyczeń

### Biblioteka
Funkcjonalności:
- Zarządzanie użytkownikami
- Zarządzanie książkami
- System wypożyczeń
- Generowanie raportów

## System Uprawnień
1. Poziom 1: Podstawowy dostęp (przeglądanie katalogu)
2. Poziom 2: Czytelnik (wypożyczanie, zwroty)
3. Poziom 3: Czytelnik+ (wypożyczanie, zwroty, rezerwacje)
4. Poziom 4: Bibliotekarz (zarządzanie książkami)
5. Poziom 5: Administrator (pełne uprawnienia) 