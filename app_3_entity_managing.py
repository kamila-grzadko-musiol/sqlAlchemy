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
    # metadata.drop_all(engine) #Usuwamy tabele w bazie danych
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

            person_kama.age = 100
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
            # session.add(person_sylwia)
            # session.commit()
        except Exception as e:
            print(e)
            #Wycofanie wszystkich niezapisanych w sesji zmian w przypadku błędu
            session.rollback()
        finally:
            print('Sesja została zakończona')


if __name__ == '__main__':
    main()