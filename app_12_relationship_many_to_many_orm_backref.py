from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase, Session, Mapped, mapped_column


USERNAME = 'user'
PASSWORD = 'user1234'
DATABASE = 'db_1'
PORT = 3307
URL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{DATABASE}'

engine = create_engine(URL, echo=True)


class Base(DeclarativeBase):
    pass

#
# class Doctor(Base):
#     __tablename__ = 'doctors'
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#
#     name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
#     visits: Mapped[list["Visit"]] = relationship(
#         "Visit",
#         back_populates="doctor",
#         lazy="select")
#
#
#
# class Visit(Base):
#     __tablename__ = 'visits'
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     details: Mapped[str] = mapped_column(String(50), nullable=False)
#
#     doctor_id: Mapped[int] = mapped_column(ForeignKey('doctors.id'), primary_key=True)
#     doctor: Mapped[Doctor] = relationship(
#         "Doctor",
#         back_populates="visits",
#         cascade="save-update"
#     )

class Doctor(Base):
    __tablename__ = 'doctors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    visits: Mapped[list["Visit"]] = relationship(
        "Visit",
        backref="doctor",
        lazy="select")



class Visit(Base):
    __tablename__ = 'visits'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    details: Mapped[str] = mapped_column(String(50), nullable=False)

    doctor_id: Mapped[int] = mapped_column(ForeignKey('doctors.id'), primary_key=True)


def main() -> None:
    metadata = Base.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)

    with Session(engine) as session:
        d1 = Doctor(name="D1")
        d2 = Doctor(name="D2")
        v1 = Visit(doctor=d1, details="V1")
        v2 = Visit(doctor=d2, details="V2")

        session.add_all([v1, v2])
        session.commit()

        print('----[1]----')
        doctors = session.query(Doctor).all()
        for doctor in doctors:
            print(f'Doctor: {doctor.id} = {doctor.name}')
            print(f'Visit: {[visit.details for visit in doctor.visits]}')


        print('----[3]----')
        visits = session.query(Visit).all()
        for visit in visits:
            print(f'Doctor: {visit.doctor.name} = Details: {visit.details}')


"""
    Zarówno back_populates, jak i backref w SQLAlchemy są używane do definiowania relacji dwukierunkowych między 
    tabelami. Jednak różnią się w sposobie konfiguracji, elastyczności i czytelności. 

    -> back_populates

    Wymaga jawnego zdefiniowania relacji w obu klasach, co daje większą kontrolę nad konfiguracją każdej 
    strony relacji.
    Możesz przypisać różne ustawienia (np. cascade, lazy) dla każdej strony relacji.
    Wyraźnie widać, jak relacja jest skonfigurowana z obu stron.
    Wymaga więcej kodu, ponieważ musisz ręcznie definiować obie strony.

    -> backref

    Tworzy automatyczną relację dwukierunkową. Definiujesz backref w jednej klasie, a SQLAlchemy automatycznie 
    generuje odpowiadającą relację w drugiej klasie.
    Krótszy i bardziej zwięzły kod, szczególnie dla prostych relacji. Nie trzeba definiować obu stron.

    Obie strony relacji dziedziczą te same ustawienia (np. cascade, lazy).
    Mniej elastyczna konfiguracja, jeśli wymagane są różne ustawienia po obu stronach.
"""

if __name__ == '__main__':
    main()