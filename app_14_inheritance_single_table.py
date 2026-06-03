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

# Dziedziczenie z jedna tabela (Single Table Inheritance)
# Wszystkie klasy dziedziczące są mapowane na jedną wspólną tabelę w bazie danych.
# Wszystkie pola dla wszystkich klas są przechowywane w tej samej tabeli, a kolumna
# dyskryminatora identyfikuje typ rekordu.

class Person(Base):
    __tablename__ = 'people'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    # Kolumna type przechowuje typ obiektu (np. person, engineer, manager)
    type: Mapped[str] = mapped_column(String(50))

    # Parametry mapowania ORM dla dziedziczenia
    __mapper_args__ = {
        # Wartosc domyslna w kolumnie type dla klasy bazowej
        'polymorphic_identity': 'person',
        # Kolumna uzywana do roznicowania typow obiektow
        'polymorphic_on': type
    }

class Engineer(Person):
    primary_language: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __mapper_args__ = {
        # Dla klasy Enigineer type ma wartosc 'engineer'
        'polymorphic_identity': 'engineer',
    }

class Manager(Person):
    department: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'manager',
    }


def main() -> None:
    metadata = Base.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)

    with Session(engine) as session:
        person = Person(name='P')
        engineer = Engineer(name='E', primary_language='EN')
        manager = Manager(name='M', department='D')
        session.add_all([person, engineer, manager])
        session.commit()

        print('----1----')
        people = session.query(Person).all()
        for person in people:
            print(person.name)

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