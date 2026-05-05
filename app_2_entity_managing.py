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

    # Base.metadata przechowuje informacje o wszystkich tabelach
    metadata = Base.metadata

    metadata.create_all(engine) #Realizujemy tworzenia tabel w bazie danych


if __name__ == '__main__':
    main()