from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship, DeclarativeBase, Session, Mapped, mapped_column, validates


USERNAME = 'user'
PASSWORD = 'user1234'
DATABASE = 'db_1'
PORT = 3307
URL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{DATABASE}'

engine = create_engine(URL, echo=True)

metadata = MetaData()

class Base(DeclarativeBase):
    metadata = metadata

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    preferences: Mapped[dict[str, str] | list[str]] = mapped_column(JSON, nullable=False )

    @validates('preferences')
    def validate_preferences(self, key, value):
        if not isinstance(value, (dict, list)):
            raise TypeError('preferences must be dict or list')
        return value

    def __repr__(self):
        return f'<Customer(id={self.id}, name={self.name}, preferences={self.preferences})>'


users_tables = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50), nullable=False),
    Column('preferences', JSON)
)

def main() -> None:

    metadata.drop_all(engine)
    metadata.create_all(engine)

    with engine.connect() as conn:
        conn.execute(users_tables.insert(),[
            {'name': 'Adam', 'preferences': {'param1': '10', 'param2': '20'}},
            {'name': 'Ewa', 'preferences': ['A', 'B', 'C']}
        ])
        conn.commit()

        res = conn.execute(users_tables.select())
        for row in res:
            print(row)

    with Session(engine) as session:
        c1 = Customer(name='Adam', preferences={'param1': '10', 'param2': '20'})
        c2 = Customer(name='Ewa', preferences=['A', 'B', 'C'])

        session.add_all([c1, c2])
        session.commit()
        customers = session.query(Customer).all()
        for customer in customers:
            print(customer)



if __name__ == '__main__':
    main()