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
    # # Base.metadata przechowuje informacje o wszystkich tabelach
    # metadata = Base.metadata
    # metadata.create_all(engine) #Realizujemy tworzenia tabel w bazie danych
    #
    # # odwołujemy się do wszystkich tabel w bazie danych
    # for table in metadata.sorted_tables:
    #     print('-----')
    #     print(table.info)
    #     print('-----')
    #     print(table.columns)
    #     print('-----')
    #     print(table.name)
    #     print('-----')
    #     print(table.metadata)
    #
    # # wyciąganie informacji o pojedynczej tabeli
    # people_table = metadata.tables['people']
    # print(people_table.columns)
    # c = people_table.columns
    # print(people_table.c.age)
    # print(people_table.c.age.type)
    # print(people_table.c.age.nullable)
    # print(people_table.c.age.primary_key)
    #
    # #informacje na temat kluczy glownych i obcych
    # print('--PK---')
    # for pk in people_table.primary_key:
    #     print(pk)
    # print('---FK--')
    # for fk in people_table.foreign_keys:
    #     print(fk)
    #
    # #usuwanie tabel
    # # metadata.drop_all(bind=engine)
    # # metadata.drop_all(bind=engine, tables=[cast(Table,Person.__table__]))
    #
    # print(Person.__table__)
    # print(Person.__mapper__)
    # print(Person.__annotations__)
# """
#    Klasa, która dziedziczy po DeclarativeBase w SQLAlchemy, pełni rolę bazy dla wszystkich modeli ORM. Dziedzicząc
#    po niej, otrzymujesz wbudowane atrybuty i funkcjonalności, które SQLAlchemy zapewnia do zarządzania mapowaniem
#    obiektów na tabele bazy danych.
#
#    __tablename__
#    Wymagane dla klasy, aby SQLAlchemy wiedziało, jak nazywać tabelę w bazie danych.
#    Jeżeli nie ustawisz __tablename__, SQLAlchemy spróbuje wygenerować domyślną nazwę tabeli na podstawie nazwy klasy.
#
#    __table__
#    Automatycznie tworzony obiekt Table, który odpowiada za mapowanie klasy na tabelę w bazie danych.
#
#    metadata
#    Atrybut metadata dziedziczony po klasie bazowej (DeclarativeBase).
#    Przechowuje informacje o wszystkich tabelach zdefiniowanych w danym ORM.
#    Dzięki niemu można tworzyć, usuwać lub zarządzać tabelami.
#
#    __mapper__
#    Obiekt Mapper, który odpowiada za mapowanie klasy na tabelę.
#    Jest automatycznie tworzony przez SQLAlchemy.
#
#    __table_args__
#    Opcjonalny słownik lub krotka, który umożliwia podanie dodatkowych parametrów dla tabeli (np. klucze obce, indeksy).
#    __table_args__ = (
#        {'mysql_engine': 'InnoDB'},  # Specyficzny silnik dla MySQL
#    )
#
#    __annotations__
#    Słownik przechowujący typy pól, zdefiniowane za pomocą Mapped oraz typowania Pythona.
#    Automatycznie generowany przy korzystaniu z typowania.
#
#
#    W SQLAlchemy, kiedy używamy ORM do mapowania klas na tabele w bazie danych, istnieje zestaw obiektów, które
#    współpracują ze sobą w tle, aby utworzyć reprezentację tabeli i umożliwić mapowanie klas Pythona na encje
#    w bazie danych.
#
#    Główne komponenty i ich relacje
#    DeclarativeBase (klasa bazowa)
#    Table (obiekt reprezentujący strukturę tabeli)
#    Mapper (obiekt mapujący klasę na tabelę)
#    metadata (kontener dla wszystkich obiektów Table)
#
#    Jak to działa krok po kroku?
#
#    1.  Klasa bazowa: DeclarativeBase
#        DeclarativeBase to klasa nadrzędna, z której dziedziczy nasz model ORM. Jest to punkt wyjściowy dla
#        mapowania ORM. Zawiera atrybut metadata, który jest kontenerem dla wszystkich obiektów Table utworzonych
#        przez SQLAlchemy.
#
#        class Base(DeclarativeBase):
#            pass
#
#    2.  Definiowanie modelu ORM
#        Gdy tworzymy klasę ORM, SQLAlchemy analizuje tę klasę i tworzy mapowanie między klasą a tabelą w bazie
#        danych.
#
#        class Person(Base):
#            __tablename__ = "people"  # Nazwa tabeli w bazie danych
#
#            id = mapped_column(Integer, primary_key=True)
#            name = mapped_column(String(50), unique=True, nullable=False)
#            ...
#
#        W tym momencie SQLAlchemy tworzy następujące obiekty:
#
#        Obiekt Table:
#        Reprezentuje strukturę tabeli people w bazie danych.
#        Jest tworzony automatycznie na podstawie pól klasy Person i zapisany w Base.metadata.
#
#        Obiekt Mapper:
#        Jest odpowiedzialny za mapowanie klasy Person na obiekt Table.
#        Mapper informuje ORM, jak operować na danych: jak tworzyć, odczytywać i aktualizować rekordy w tabeli people
#        za pomocą klasy Person.
#
#    3.  Obiekt Table i metadata
#        Obiekt Table jest tworzony automatycznie podczas analizy klasy ORM. Zawiera informacje o:
#        Kolumnach tabeli,
#        Kluczach głównych i obcych,
#        Nazwie tabeli,
#        Indeksach.
#        Obiekt Table jest rejestrowany w metadata klasy bazowej Base.
#
#    4.  Obiekt Mapper
#        Mapper łączy klasę Pythona (np. Person) z odpowiadającym jej obiektem Table.
#        __mapper__ to atrybut klasy ORM, który pozwala uzyskać dostęp do obiektu Mapper.
#        Zadania obiektu Mapper:
#        Mapowanie atrybutów klasy (np. id, name) na kolumny w tabeli Table.
#        Zarządzanie cyklem życia encji (INSERT, SELECT, UPDATE, DELETE).
#        Obsługa relacji między tabelami, jeśli występują.
#
#    PODSUMOWANIE
#    Kiedy aplikacja uruchamia się, a SQLAlchemy przetwarza klasę ORM:
#    -> Klasa ORM jest analizowana.
#    -> Tworzony jest obiekt Table i rejestrowany w Base.metadata.
#    -> Tworzony jest obiekt Mapper, który mapuje klasę na obiekt Table.
#    -> Przy operacjach na bazie danych SQLAlchemy używa Mapper i Table, aby wygenerować odpowiednie zapytania SQL.
# """
    # ---------------------------------------------------------------------------------------------
    # Zarządzanie danymi w tabeli
    # --------------------------------------------------------------------------------------------
    with Session(engine) as session:
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
        print('--------------2-----------')
        print(person_kama)



if __name__ == '__main__':
    main()