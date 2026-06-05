from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship, DeclarativeBase, Session, Mapped, mapped_column, validates


USERNAME = 'user'
PASSWORD = 'user1234'
DATABASE = 'db_1'
PORT = 3307
URL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{DATABASE}'

engine = create_engine(URL, echo=True)


class Base(DeclarativeBase):
    pass


# Dziedziczenie z oddzielnymi tabelami( Concrete Table Inheritance) w SQLAlchemy ORM.
# W strategii Concrete Table Inheritance każda klasa w hierarchii dziedziczenia jest mapowana
# na oddzielną tabelę, która zawiera wszystkie atrybuty – zarówno dziedziczone z klasy bazowej,
# jak i specyficzne dla danej klasy. W tej strategii nie ma tabeli bazowej reprezentującej
# wspólne dane, a każda tabela jest w pełni niezależna.

class Person(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))


class Engineer(Person):
    __tablename__ = 'engineers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    primary_language: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'engineer',
    }


class Manager(Person):
    __tablename__ = 'managers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'manager',
    }


def main() -> None:
    metadata = Base.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)

    with Session(engine) as session:

        engineer = Engineer(name='E', primary_language='EN')
        manager = Manager(name='M', department='D')
        session.add_all([engineer, manager])
        session.commit()


        print('----2----')
        managers = session.query(Manager).all()
        for manager in managers:
            print(manager.name)

        print('----3----')
        engineers = session.query(Engineer).all()
        for engineer in engineers:
            print(engineer.name)


if __name__ == '__main__':
    main()

# Dokumentacja SQLAlchemy dla dziedziczenia:
# https://docs.sqlalchemy.org/en/20/orm/inheritance.html

# Która strategia dziedziczenia jest najlepsza?

"""
----------------------------------------------------------------------------------------------------------------------
                                    Single Table Inheritance	            

Struktura tabel                     Jedna tabela dla całej hierarchii dziedziczenia.

Normalizacja danych                 Brak – wszystkie dane są przechowywane razem.

Kolumna dyskryminatora              Wymagana (np. type).

Złożoność zapytań                   Proste – brak potrzeby użycia JOIN.

Wydajność zapytań                   Szybkie zapytania dla małych tabel, może być wolne przy dużych.

Redundancja danych                  Puste kolumny dla pól specyficznych dla podklas.

Elastyczność                        Mniej elastyczna dla zmian strukturalnych.

Przypadki użycia                    Gdy dane są spójne i podklasy mają niewiele specyficznych pól.


----------------------------------------------------------------------------------------------------------------------
                                    Joined Table Inheritance	

Struktura tabel                     Jedna tabela bazowa i osobne tabele dla każdej podklasy.

Normalizacja danych                 Wysoka – wspólne dane w tabeli bazowej, specyficzne w tabelach potomnych.

Kolumna dyskryminatora              Wymagana (np. type).

Złożoność zapytań                   Średnia – wymaga JOIN tabel bazowej i potomnych.

Wydajność zapytań                   Wolniejsze – wymaga JOIN, szczególnie dla skomplikowanych zapytań.

Redundancja danych                  Brak redundancji – dane są znormalizowane.

Elastyczność                        Elastyczna – łatwo dodawać nowe klasy potomne.

Przypadki użycia                    Gdy dane muszą być znormalizowane, a zapytania obejmują wiele relacji.                                     


----------------------------------------------------------------------------------------------------------------------
                                    Concrete Table Inheritance

Struktura tabel                     Osobne, niezależne tabele dla każdej klasy.

Normalizacja danych                 Brak – dane są zdublowane w tabelach.

Kolumna dyskryminatora              Nie wymagana.

Złożoność zapytań                   Proste – brak potrzeby użycia JOIN.

Wydajność zapytań                   Szybkie zapytania – każda tabela działa niezależnie.

Redundancja danych                  Redundancja – wspólne dane są powielane w tabelach.

Elastyczność                        Elastyczna – każda tabela jest niezależna.

Przypadki użycia                    Gdy podklasy mają bardzo różne zestawy danych i wymagania.             

Kiedy wybrać którą strategię?

1. Single Table Inheritance
    Zalety:
    Prosta implementacja – wszystkie dane są w jednej tabeli.
    Brak potrzeby użycia JOIN, co przyspiesza zapytania.

    Wady:
    Puste kolumny dla podklas, które nie używają wszystkich pól.
    Potencjalnie duże rozmiary tabeli przy skomplikowanej hierarchii dziedziczenia.

Przypadki użycia:
    Gdy klasy mają wiele wspólnych danych i niewiele pól specyficznych.
    Gdy wydajność zapytań jest ważniejsza niż normalizacja danych.
    Gdy masz prostą hierarchię dziedziczenia z niewielką liczbą podklas.

Przykład:
    Prosta aplikacja CRM, w której Customer i Employee różnią się minimalnie.    

2. Joined Table Inheritance
    Zalety:
    Dane są znormalizowane, co zmniejsza redundancję.
    Łatwo dodawać nowe podklasy i rozszerzać hierarchię.

    Wady:
    Wymaga użycia JOIN, co może być wolniejsze w przypadku dużych tabel i złożonych zapytań.
    Nieco bardziej skomplikowana implementacja w porównaniu do Single Table.

    Przypadki użycia:
    Gdy dane muszą być znormalizowane (np. w systemach ERP lub finansowych).
    Gdy podklasy mają dużo specyficznych pól i zapytania będą dotyczyć wielu relacji.
    Gdy potrzebujesz łatwo rozbudowywalnej struktury danych.

    Przykład:
    System HR, gdzie Employee, Manager i Contractor mają różne dane specyficzne.


3. Concrete Table Inheritance
    Zalety:
    Brak JOIN – zapytania są szybkie.
    Każda klasa działa niezależnie, co upraszcza zarządzanie tabelami.

    Wady:
    Powielanie wspólnych danych w tabelach.
    Trudność w pracy z danymi na poziomie klasy bazowej (np. brak wspólnej tabeli dla Person).

    Przypadki użycia:
    Gdy podklasy mają bardzo różne zestawy danych.
    Gdy zależy Ci na prostocie struktury tabel i wydajności zapytań.
    Gdy nie potrzebujesz wspólnego zarządzania wszystkimi podklasami na poziomie klasy bazowej.

Przykład:
    System raportowy, gdzie SalesReport i InventoryReport przechowują dane w zupełnie różnych formatach.
"""