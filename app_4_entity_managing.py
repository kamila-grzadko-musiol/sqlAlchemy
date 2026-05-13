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
    Table, # Typ reprezentujący tabele
    func,
    desc,
    and_,
    or_,
    not_
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
                age=22,
                birthdate=date(2005,3,10),
                last_login_datetime=datetime.now(),
                gender=Gender.FEMALE,
                salary=Decimal('2000.04'),
                is_active=True)

            person_andrzej = Person(
                name='Andrzej',
                age=25,
                birthdate=date(2004,2,11),
                last_login_datetime=datetime.now(),
                gender=Gender.MALE,
                salary=Decimal('6000.34'),
                is_active=False)

            person_sylwia = Person(
                name='Sylwia',
                age=27,
                birthdate=date(2004,12,16),
                last_login_datetime=datetime.now(),
                gender=Gender.FEMALE,
                salary=Decimal('1000.34'),
                is_active=False)



            person_pawel = Person(
                name='Pawel',
                age=30,
                birthdate=date(2001, 2, 23),
                last_login_datetime=datetime.now(),
                gender=Gender.MALE,
                salary=Decimal('4000.23'),
                is_active=False)

            session.add_all([person_kama, person_andrzej, person_sylwia, person_pawel])
            session.commit()

            # person_from_db = session.get(Person,1)
            # print(person_from_db.salary)
            # print(type(person_from_db.salary))

            print('------------------------POBIERANIE WSZYSTKICH REKORDÓW----------------------------------')
            for person in session.query(Person).all():
                print(person)

            print('------------------------POBIERANIE POSZCZEGOLNYCH KOLUMN--------------------------------')
            for name, age in session.query(Person.name, Person.age).all():
                print(f'{name}, {age}')

            print('------------------------POBIERANIE Z SORTOWANIEM I LIMITOWANIEM-------------------------')
            # Za pomocą indeksowanie omineliśmy pierwszy element, zrobiliśmy limit 2
            for person in session.query(Person).order_by(desc(Person.age))[1:3]:
                print(person)

            print('------------------------FILTROWANIE ZAKRESU---------------------------------------------')
            for person in session.query(Person).filter(and_(Person.age >= 20, Person.age <= 30)):
                print(person)

            print('------------------------FILTROWANIE Z WARUNKIEM OR_ ------------------------------------')
            for person in session.query(Person).filter(or_(Person.age < 20, Person.salary > 3000)):
                print(person)

            print('------------------------WILDCARDS (like) i ZLICZANIE------------------------------------')
            counter = session.query(Person).filter(Person.name.like('%A%')).count()
            print(counter)

            print('------------------------AGREGACJA I GRUPOWANIE------------------------------------------')
            # one() daje nam tuple, której pierwszy element jest wynik funkcji agregujacej
            # total_count = session.query(func.count(Person.id)).one()
            # Funkcja skalar wyciągnie z tuple pierwszy tuple
            total_count = session.query(func.count(Person.id)).scalar()
            avg_salary = session.query(func.avg(Person.salary)).scalar()
            print(total_count)
            print(avg_salary)

            print('------------------------GRUPOWANIE PO PLCI----------------------------------------------')
            for gender, avg_salary in session.query(Person.gender, func.avg(Person.salary)).group_by(Person.gender):
                print(f'{gender}, {avg_salary}')

            print('------------------------NAJMŁODSZA OSOBA AKTYWNA----------------------------------------')
            youngest_active = session.query(Person).filter(Person.is_active == True).order_by(Person.age).first()
            print(youngest_active)

            print('------------------------UZYCIE NOT_----------------------------------------')
            for person in session.query(Person).filter(not_(and_(Person.is_active, Person.age >= 10))):
                print(person)

        except Exception as e:
            print(e)
            #Wycofanie wszystkich niezapisanych w sesji zmian w przypadku błędu
            session.rollback()
        finally:
            print('Sesja została zakończona')


if __name__ == '__main__':
    main()