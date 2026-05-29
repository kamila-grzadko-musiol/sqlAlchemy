from sqlalchemy import ForeignKey, Integer, String, create_engine, select, UniqueConstraint
from sqlalchemy.orm import (DeclarativeBase, relationship, Session, Mapped, mapped_column, joinedload, selectinload,
                            subqueryload, contains_eager, with_parent)

USERNAME = 'user'
PASSWORD = 'user1234'
DATABASE = 'db_1'
PORT = 3307
URL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{DATABASE}'

engine = create_engine(URL, echo=True)


class Base(DeclarativeBase):
    pass


class Driver(Base):
    __tablename__ = 'drivers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    license: Mapped["License"] = relationship(
        back_populates="driver",
        uselist=False,
        lazy='select'
    )

    def __repr__(self) -> str:
        return f'Driver: id= {self.id}, name= {self.name}'


class License(Base):
    __tablename__ = 'licenses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    driver_id: Mapped[int] = mapped_column(ForeignKey('drivers.id'), nullable=False, unique=True)
    driver: Mapped[Driver] = relationship(back_populates='license')


def main() -> None:
    # metadata = Base.metadata
    # metadata.drop_all(engine)
    # metadata.create_all(engine)

    with Session(engine) as session:

        # driver1 = Driver(name='Alice', license=License(name='A12345'))
        # driver2 = Driver(name='Bob', license=License(name='B67890'))
        # session.add_all([driver1, driver2])
        # session.commit()

        # Pobieranie danych
        print('----[1]---- Lazy loading - select N + 1 Problem')

        drivers = session.query(Driver).all()
        for driver in drivers:
            print(f'Driver: {driver.name}, License: {driver.license.name}')

        print('----[2]---- Eager loading - joinedload')

        drivers = session.query(Driver).options(joinedload(Driver.license)).all()
        for driver in drivers:
            print(f'Driver: {driver.name}, License: {driver.license.name}')

        print('----[3]---- Eager loading - selectedload')

        drivers = session.query(Driver).options(selectinload(Driver.license)).all()
        for driver in drivers:
            print(f'Driver: {driver.name}, License: {driver.license.name}')

        print('----[4]---- Explicit load ')

        stmpt = select(Driver.name, License.name).join(Driver.license)
        res = session.execute(stmpt).all()
        drivers = session.query(Driver).options(joinedload(Driver.license)).all()
        for driver in drivers:
            print(f'Driver: {driver.name}, License: {driver.license.name}')

        print('----[5]---- Subquery load')

        drivers = session.query(Driver).options(subqueryload(Driver.license)).all()
        for driver in drivers:
            print(f'Driver: {driver.name}, License: {driver.license.name}')


if __name__ == '__main__':
    main()