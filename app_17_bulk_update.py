from sqlalchemy import create_engine, String, Identity, Integer
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column


USERNAME = 'user'
PASSWORD = 'user1234'
DATABASE = 'db_1'
PORT = 3307
URL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{DATABASE}'

engine = create_engine(URL, echo=True)

"""
----------------------------------------------------------------------------------------------------------------------
BULK INSERT
----------------------------------------------------------------------------------------------------------------------

Bulk insert (wstawianie masowe) to technika dodawania dużej liczby rekordów do bazy danych w sposób efektywny, 
zmniejszając liczbę pojedynczych zapytań SQL. Zamiast wykonywać jedno zapytanie dla każdego wiersza, grupuje dane 
i przesyła je do bazy w jednym większym zapytaniu lub w partiach.

Dlaczego stosujemy bulk insert?

Wydajność:
Redukuje liczbę zapytań SQL.
Minimalizuje czas komunikacji między aplikacją a bazą danych.

Skalowalność:
Umożliwia efektywną pracę z dużymi zestawami danych.

Prostota implementacji:
W SQLAlchemy można go zrealizować za pomocą wbudowanych mechanizmów, takich jak bulk_insert_mappings czy 
bulk_save_objects.

Użycie bulk_insert_mappings
Akceptuje listę słowników, gdzie każdy słownik reprezentuje rekord.
Obejście warstwy ORM — rekordy są wstawiane bezpośrednio.

Użycie bulk_save_objects
Akceptuje listę obiektów ORM, które są następnie wstawiane do bazy.
Jest bardziej „ORM-friendly” niż bulk_insert_mappings.

customers = [
    Customer(name=f"customer name {i}", description=f"customer description {i}")
    for i in range(1, 10001)
]
session.bulk_save_objects(customers)


----------------------------------------------------------------------------------------------------------------------
BULK UPDATE
----------------------------------------------------------------------------------------------------------------------
W aplikacjach, które operują na dużych zbiorach danych, konieczne może być zaktualizowanie tysięcy lub nawet milionów 
rekordów w bazie danych. Tradycyjne podejście w ORM (przez ładowanie rekordów do pamięci, ich modyfikację i zapisanie) 
jest nieefektywne:
-> Wymaga dużej ilości pamięci.
-> Generuje wiele pojedynczych zapytań SQL UPDATE, co powoduje duże opóźnienia.

bulk_update_mappings:
-> Aktualizuje rekordy bez ładowania ich jako obiektów ORM.
-> Tworzy jedną masową instrukcję SQL UPDATE, co znacząco zwiększa wydajność.
-> Eliminuje konieczność śledzenia zmian w obiektach przez mechanizm ORM.

Jak działa bulk_update_mappings?

Mechanizm:
-> Otrzymuje listę słowników, gdzie każdy słownik zawiera:
    Identyfikator rekordu (id) potrzebny do jego zlokalizowania.
    Kolumny, które mają zostać zaktualizowane, z nowymi wartościami.

-> Proces w tle:
    SQLAlchemy generuje efektywne zapytania SQL UPDATE, które aktualizują rekordy na podstawie podanych danych.
    Zapytania te są wykonywane bezpośrednio na bazie danych, omijając warstwę ORM.

Zalety masowej aktualizacji

Wydajność:
Operuje bezpośrednio na bazie danych, co eliminuje koszt ładowania obiektów ORM.
Minimalizuje liczbę zapytań SQL (jedno zapytanie dla wielu rekordów).

Skalowalność:
Możliwość obsługi dużych zbiorów danych bez ryzyka wyczerpania pamięci.

Łatwość implementacji:
Prosta składnia, która pozwala na aktualizację rekordów w jednym przebiegu.    
"""


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = 'customers'
    # https://docs.sqlalchemy.org/en/20/core/defaults.html#identity-ddl
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)

def main() -> None:
    metadata = Base.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)

    with Session(engine) as session:
        pass



if __name__ == '__main__':
    main()

