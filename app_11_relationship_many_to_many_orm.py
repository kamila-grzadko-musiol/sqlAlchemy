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


class Doctor(Base):
    __tablename__ = 'doctors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    visits: Mapped[list["Visit"]] = relationship(
        "Visit",
        back_populates="doctor",
        lazy="select")


class Patient(Base):
    __tablename__ = 'patients'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    visits: Mapped[list["Visit"]] = relationship(
        "Visit",
        back_populates="patient",
        lazy="select")


class Visit(Base):
    __tablename__ = 'visits'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey('doctors.id'), primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey('patients.id'), primary_key=True)
    details: Mapped[str] = mapped_column(String(50), nullable=False)
    doctor: Mapped[Doctor] = relationship(
        "Doctor",
        back_populates="visits",
        cascade="all"
    )
    patient: Mapped[Patient] = relationship(
        "Patient",
        back_populates="visits",
        cascade="all"
    )


def main() -> None:
    metadata = Base.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)

    with Session(engine) as session:
        d1 = Doctor(name="D1")
        d2 = Doctor(name="D2")
        p1 = Patient(name="P1")
        p2 = Patient(name="P2")
        v1 = Visit(doctor=d1, patient=p1, details="V1")
        v2 = Visit(doctor=d1, patient=p2, details="V2")
        v3 = Visit(doctor=d2, patient=p1, details="V3")
        v4 = Visit(doctor=d2, patient=p2, details="V4")

        session.add_all([v1, v2, v3, v4])
        session.commit()

        print('----[1]----')
        doctors = session.query(Doctor).all()
        for doctor in doctors:
            print(f'Doctor: {doctor.id} = {doctor.name}')

        print('----[2]----')
        patients = session.query(Patient).all()
        for patient in patients:
            print(f'Patient: {patient.id} = {patient.name}')

        print('----[3]----')
        visits = session.query(Visit).all()
        for visit in visits:
            print(f'Doctor: {visit.doctor.name} | {visit.patient.name} = Details: {visit.details}')


if __name__ == '__main__':
    main()