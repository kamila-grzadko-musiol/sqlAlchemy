from sqlalchemy import (
    create_engine,  # Tworzenie połączenia z bazą danych
    String,  # Typ danych VARCHAR
    Integer,  # Typ danych INTEGER
    Date,  # Typ danych DATE
    DateTime,  # Typ danych DATETIME
    Enum,  # Typ danych ENUM
    Numeric,  # Typ danych NUMERIC (precyzyjne liczby)
    Boolean,  # Typ danych BOOLEAN
    text  # Surowe zapytania SQL
)
from sqlalchemy.orm import (
    DeclarativeBase,  # Bazowa klasa do mapowania ORM
    Mapped,  # Mapowanie typów danych
    mapped_column,  # Kolumny z mapowaniem
    Session  # Sesja do komunikacji z bazą
)
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import enum

# Konfiguracja polaczenia z baza danych
USERNAME = 'user'
PASSWORD = 'user1234'
DATABASE = 'db_1'
PORT = 3307
#URL do połączenia z baza danych MySQL - dane lepiej przechowywac zmiennych środokowiskowych w .env
URL = f'mysql://{USERNAME}:{PASSWORD}@localhost:{PORT}/{DATABASE}'

#Tworzenie silnika bazy danych
#echo ustawione na True pozwoli nam obserowac zapytania SQL generowane przez orm pod spodem

engine = create_engine(URL, echo=True)
#Specjalna klasa - deklaratywna baza czyli klasa bazowa dla wszysrkich modeli ORM
class Base(DeclarativeBase):
    pass

class Gender(Enum):
    FEMALE = 0,
    MALE = 1

#Model ORM, który reprezentuje tabele people w bazie danych
#Klasa Person jest encją
# Encja to obiekt reprezentujący rzeczywisty byt w bazie danych. W kontekście SQLAlchemy encja to klasa,
# która jest mapowana na tabelę w bazie danych przy użyciu ORM (Object Relational Mapping).
@dataclass
class Person(Base):
    __tablename__ = 'people' # Tak będzie nazywać sie powiązana tabela w bazie danych

    #Definicja kolumn z wykorzystaniem podejścia - Mapped
    id: Mapped[int] = mapped_column(Integer, primary_key=True) #Klucz główny
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) #Unikalna nazwa usera do 50 znakow nie może być null
    age: Mapped[int | None] = mapped_column(Integer, nullable=True) #Wiek opcjonalny
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True) #Data urodzenia opcjonalna
    last_login_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=True)
    salary: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Inne typy znajdziesz w dokumentacji:
    # https://docs.sqlalchemy.org/en/20/core/types.html