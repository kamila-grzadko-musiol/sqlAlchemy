from sqlalchemy import (
    create_engine,  # Tworzenie połączenia z bazą danych
    String,  # Typ danych VARCHAR
    Integer,  # Typ danych INTEGER
    Date,  # Typ danych DATE
    DateTime,  # Typ danych DATETIME
    Enum,  # Typ danych ENUM
    Numeric,  # Typ danych NUMERIC (precyzyjne liczby)
    Boolean,  # Typ danych BOOLEAN
    text,  # Surowe zapytania SQL,
    Table # Typ reprezentujący tabele
)
from sqlalchemy.orm import (
    DeclarativeBase,  # Bazowa klasa do mapowania ORM
    Mapped,  # Mapowanie typów danych
    mapped_column,  # Kolumny z mapowaniem
    Session  # Sesja do komunikacji z bazą
)
from dataclasses import dataclass
from datetime import date, datetime
from typing import cast
from decimal import Decimal
import enum

# Konfiguracja polaczenia z baza danych
USERNAME = 'user'
PASSWORD = 'user1234'
DATABASE = 'db_1'
PORT = 3307
# URL do polaczenia z baza danych MySQL - dane lepiej przechowywac zmiennych środokowiskowych w .env
URL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{DATABASE}'

# Tworzenie silnika bazy danych
# echo ustawione na True pozwoli nam obserwowac zapytania SQL generowane przez ORM pod spodem
engine = create_engine(URL, echo=True)


# Specjalna klasa - deklaratywna baza czyli klasa bazowa dla wszystkich modeli ORM
class Base(DeclarativeBase):
    pass


class Gender(enum.Enum):
    FEMALE = 0
    MALE = 1

# Model ORM, ktory reprezentuje tabele people w bazie danych
# Klasa Person jest encja.
# Encja to obiekt reprezentujący rzeczywisty byt w bazie danych. W kontekście SQLAlchemy encja to klasa,
# która jest mapowana na tabelę w bazie danych przy użyciu ORM (Object Relational Mapping).
@dataclass
class Person(Base):
    __tablename__ = 'people'  # Tak bedzie nazywac sie powiazana tabela w bazie danych

    # Definicja kolumn z wykorzystaniem nowoczesnego podejscia - Mapped (kiedys robiono Column)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # Klucz glowny
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)  # Unikalna nazwa usera do 50 znakow
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Wiek (opcjonalny)
    birthdate: Mapped[date | None] = mapped_column(Date, nullable=True)  # Data urodzenia (opcjonalna)
    last_login_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender), nullable=True)
    salary: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Inne typy znajdziesz w dokumentacji:
    # https://docs.sqlalchemy.org/en/20/core/types.html
    # server_default - ustawianie wartosci domyslnej po stronie serwera

    # __table_args__ = (
    #     {'mysql_engine': 'InnoDB'},  # Specyficzny silnik dla MySQL
    # )

    @property
    def is_adult(self):
        return self.age is not None and self.age >= 18

    def __repr__(self) -> str:
        return f'Person [id={self.id}, name={self.name}, age={self.age}, birthdate={self.birthdate}, last_login_datetime={self.last_login_datetime}, gender={self.gender}, salary={self.salary}, is_active={self.is_active}]'


def main() -> None:
    # ---------------------------------------------------------------------------------------------
    # Zarządzanie i pozyskiwanie informacji o strukturze tabel
    # --------------------------------------------------------------------------------------------
    # Base.metadata przechowuje informacje o wszystkich tabelach
    metadata = Base.metadata
    metadata.drop_all(engine) #Usuwamy tabele w bazie danych
    metadata.create_all(engine) #Realizujemy tworzenia tabel w bazie danych


    # ---------------------------------------------------------------------------------------------
    # Zarządzanie danymi w tabeli
    # --------------------------------------------------------------------------------------------
    with Session(engine) as session:
        try:
            print('-----Dodawanie nowych rekordow do tabeli w bazie')
            person_kama = Person(
                name='Kama',
                age=34,
                birthdate=date(1992,3,10),
                last_login_datetime=datetime.now(),
                gender=Gender.FEMALE,
                salary=Decimal('2000.04'),
                is_active=True)

            person_andrzej = Person(
                name='Andrzej',
                age=38,
                birthdate=date(1993,2,11),
                last_login_datetime=datetime.now(),
                gender=Gender.MALE,
                salary=Decimal('6000.34'),
                is_active=False)

            person_sylwia = Person(
                name='Sylwia',
                age=32,
                birthdate=date(1991,12,16),
                last_login_datetime=datetime.now(),
                gender=Gender.FEMALE,
                salary=Decimal('1000.34'),
                is_active=False)

            print('--------------1-----------')
            print(person_kama)
            # Dodawanie obiektow do SESJI - stan pending
            # SQLAlchemy ORM posiada tzw. "stany" encji (obiektów ORM), które opisują, w jakim stanie znajduje się obiekt
            # w kontekście sesji SQLAlchemy. Stany te wskazują na interakcję obiektu z bazą danych i sesją. Dzięki temu
            # SQLAlchemy może zarządzać cyklem życia encji.

            # Podstawowe stany encji:

            # 1. Transient (Przejściowy)
            # Oznacza, że obiekt został utworzony, ale nie jest związany z sesją i nie istnieje w bazie danych.
            # Obiekt jest "luźnym obiektem" i SQLAlchemy nie śledzi jego zmian.
            # person_anna = Person(name="Anna", age=22)
            #  W tym momencie person_anna jest transient, bo nie została dodana do sesji

            # 2. Pending (Oczekujący)
            # Oznacza, że obiekt został dodany do sesji, ale nie został jeszcze zapisany w bazie danych (nie wykonano commit()).
            # Obiekt nie ma przypisanego jeszcze klucza głównego (ID), chyba że został ustawiony ręcznie.
            # SQLAlchemy przygotowuje obiekt do operacji INSERT w bazie danych.
            # session.add(person_anna)
            # W tym momencie person_anna jest w stanie 'pending'

            # 3. Persistent (Trwały)
            # Oznacza, że obiekt jest powiązany z sesją i istnieje w bazie danych.
            # SQLAlchemy śledzi zmiany tego obiektu. Każda zmiana zostanie zsynchronizowana z bazą danych przy commit()
            # lub flush().

            # 4. Detached (Odłączony)
            # Oznacza, że obiekt istnieje w bazie danych, ale nie jest już powiązany z sesją.
            # Zwykle występuje po zamknięciu sesji lub po jej usunięciu.
            # SQLAlchemy nie będzie śledziło jego zmian.

            # 5. Deleted (Usunięty)
            # Oznacza, że obiekt został oznaczony do usunięcia z bazy danych, ale operacja jeszcze nie została wykonana
            # (commit() nie zostało wywołane).
            # SQLAlchemy przygotowuje obiekt do operacji DELETE.

            #Możesz dodawać obikety pojedynczo
            session.add(person_kama)

            #Dodawanie obiektów kilku na raz
            session.add_all([person_andrzej, person_sylwia])

            session.commit()
            print('-------------------------')
            print(person_kama)
            print('-------------------------')
            print(person_andrzej)
            print('-------------------------')
            print(person_sylwia)

            # person_kama.age = 100
            session.commit()
            print('-------------------------')
            print(person_kama)

            # wstawianie błędnych danych
            # person_sylwia = Person(
            #     name='Sylwia',
            #     age=22,
            #     birthdate=date(1992, 10, 11),
            #     last_login_datetime=datetime.now(),
            #     gender=Gender.FEMALE,
            #     salary=Decimal('13000.34'),
            #     is_active=False)
            #
            session.add(person_sylwia)
            session.commit()

            # Pobieranie wszystkich rekordów z tabeli people

            people = session.query(Person).all()
            print('-----------------------------------------------------------------------------------------------')
            for person in people:
                print(person)
            print('-----------------------------------------------------------------------------------------------')
            # Pobieranie po konkretnym ID

            # Metoda one
            # Jeśli zapytanie zwróci więcej niż jeden wynik, zostanie rzucony
            # wyjątek MultipleResultsFound.
            # Jeśli zapytanie nie zwróci żadnego wyniku, zostanie rzucony
            # wyjątek NoResultFound.
            person = session.query(Person).filter_by(id=1).one()
            print(person)


            print('-----------------------------------------------------------------------------------------------')
            # Metoda one_or_none
            # Zwraca dokładnie jeden wynik, jeśli istnieje, lub None, jeśli brak wyników.
            # Jeśli zapytanie zwróci więcej niż jeden wynik, zostanie rzucony wyjątek
            # MultipleResultsFound.
            person = session.query(Person).filter_by(id=1).one_or_none()
            print(person)

            print('-----------------------------------------------------------------------------------------------')
            # Metoda first
            # Zwraca pierwszy wynik pasujący do zapytania lub None, jeśli brak wyników.
            # Nie rzuca wyjątków, nawet jeśli istnieje więcej wyników — zwraca po prostu
            # pierwszy.
            # Może być mniej wydajne w przypadku dużych zbiorów danych, jeśli nie użyto
            # dodatkowych ograniczeń jak LIMIT.
            person = session.query(Person).filter_by(id=1).first()
            print(person)

            print('-----------------------------------------------------------------------------------------------')
            # Metoda get - tylko dla kluczy
            # Pobiera rekord na podstawie klucza głównego.
            # Jeśli rekord istnieje, zwraca obiekt ORM.
            # Jeśli nie istnieje, zwraca None.
            # W przypadku braku wyniku nie rzuca żadnego wyjątku.
            person = session.get(Person, 1)
            print(person)
            # Metoda get w pierwszej kolejnosci sprawdza, czy jest instancja
            # powiazana z wymaganym id w pamieci sesji i jesli tak nie wykonuje
            # dodatkowego sql.

            """
            --------------------------------------------------------------------------------
             CACHE SESJI - jak dziala
            --------------------------------------------------------------------------------
            Identity Map to mechanizm SQLAlchemy ORM, który mapuje obiekty Python na rekordy bazy 
            danych i zapewnia ich jednoznaczność w ramach jednej sesji. Dzięki temu każdy rekord 
            w bazie danych jest reprezentowany przez dokładnie jeden obiekt Python w obrębie tej 
            samej sesji. Działa to na zasadzie cache, który eliminuje potrzebę wielokrotnego pobierania 
            tego samego rekordu z bazy danych.

            Przypisanie obiektu do cache przy pierwszym pobraniu
            Gdy pobierasz obiekt z bazy danych (np. za pomocą session.get() lub session.query()), 
            SQLAlchemy rejestruje go w sesji.
            Rejestracja odbywa się przy użyciu klucza głównego (Primary Key) jako unikalnego identyfikatora.
            Jeśli obiekt o konkretnym id jest pobrany po raz pierwszy, SQLAlchemy doda go do Identity Map.
            Przy kolejnym pobraniu tego samego obiektu za pomocą session.get(), SQLAlchemy sprawdza, czy 
            obiekt istnieje w cache. Jeśli obiekt jest w cache, SQLAlchemy nie wykonuje zapytania 
            SELECT – zwraca obiekt z pamięci.

            Cache działa tylko w ramach jednej sesji
            Cache (Identity Map) działa tylko dla aktywnej sesji SQLAlchemy.
            Po zamknięciu sesji (session.close()), Identity Map jest usuwane, a obiekty stają się odłączone 
            (detached).

            Zmiany na obiektach są śledzone w cache
            SQLAlchemy monitoruje zmiany na obiektach znajdujących się w Identity Map.
            Zmiany są automatycznie synchronizowane z bazą danych przy wywołaniu session.commit() 
            lub session.flush().

            Usuwanie obiektów z cache
            Obiekty mogą być usunięte z Identity Map za pomocą session.expunge() lub session.close().
            Po usunięciu obiektu z cache staje się on odłączony (detached).            

            flush(): Jeśli chcesz wysłać zmiany do bazy przed commit() (np. aby uzyskać ID wygenerowane 
            przez bazę).

            commit(): Gdy chcesz trwale zapisać zmiany w bazie.

            expunge(): Jeśli chcesz odłączyć konkretny obiekt od sesji.

            close(): Gdy zakończysz pracę z sesją i chcesz zwolnić zasoby.

            """

            person_pawel = Person(
                name='Pawel',
                age=30,
                birthdate=date(1995, 2, 23),
                last_login_datetime=datetime.now(),
                gender=Gender.MALE,
                salary=Decimal('4000.23'),
                is_active=False)

            session.add(person_pawel)
            # Wysyłanie zmian do bazy danych, ale bez zatwierdzania
            # Flush wysyła zapytania do bazy:
            # -> SQLAlchemy generuje i wykonuje zapytania SQL.
            # -> Jeśli w bazie jest mechanizm autogenerowania kluczy głównych (AUTO_INCREMENT),
            #    to klucz główny zostanie już przypisany do obiektu.
            # Zmiany są widoczne tylko w ramach transakcji:
            # -> W bazie dane są widoczne tylko w tej samej transakcji.
            # -> Jeśli wykonasz rollback(), wszystkie zmiany wykonane przez flush() zostaną
            #    cofnięte.
            # Bez zatwierdzenia (commit):
            # -> Dopóki nie wykonasz commit(), zmiany nie są trwale zapisane w bazie danych.
            # -> Inne transakcje (używające innych sesji) nie widzą tych zmian.
            session.flush()

            # Usuniecie obiektu z sesji
            session.expunge(person_pawel)
            print(person_pawel in session) # Obiekt nie jest już śledzony
            person_pawel.age = 200

            # Usuwanie rekordu z bazy danych z poziomu reprezentujacej go instancji modelu ORM
            # Wersja 1
            person_to_delete = session.get(Person, 1)
            if person_to_delete:
                #Oznaczenie obiektu do usuniecia, usuniecie nastapi kied bedzie commit
                session.delete(person_to_delete)

            # Wersja 2
            # Mozesz rowniez usunac wiele obiektow przy uzyciu session.query().filter() w polaczeniu
            # z petla
            people_to_delete = session.query(Person).filter(Person.age > 10).all()
            for person_to_delete in people_to_delete:
                session.delete(person_to_delete)

            # Wersja 3
            # Usuwanie bez pobierania obiektow, jesli nie potrzebujesz ladowac obiektow do pamieci
            session.query(Person).filter(Person.age > 10).delete(synchronize_session=False)

            session.commit()
            # Opcja synchronize_session:
            # False: Najwydajniejsza opcja. Nie aktualizuje sesji, zakładając, że usunięcie
            # jest prawidłowe.
            # 'fetch': Synchronizuje sesję, pobierając klucze główne usuniętych obiektów.
            # 'evaluate': Aktualizuje sesję na podstawie warunków użytych w zapytaniu.


        except Exception as e:
            print(e)
            #Wycofanie wszystkich niezapisanych w sesji zmian w przypadku błędu
            session.rollback()
        finally:
            print('Sesja została zakończona')


if __name__ == '__main__':
    main()