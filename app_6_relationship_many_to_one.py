from sqlalchemy import ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import (DeclarativeBase, relationship, Session, Mapped, mapped_column, joinedload, selectinload,
                            subqueryload)


USERNAME = 'user'
PASSWORD = 'user1234'
DATABASE = 'db_1'
PORT = 3307
URL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{DATABASE}'

engine = create_engine(URL, echo=True)


class Base(DeclarativeBase):
    pass



class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relacja z Player
    players: Mapped[list["Player"]] = relationship(
        back_populates='team',
        lazy='select',
        # lazy='joined'

        # Automotycznie zapisuje zmiany w powiązanych obiektach, gdy rodzic jest zapisywany
        # cascade='save-update'

        # Podczas uzywania metody merge (np scalanie stanów obiektów z roznych sesji) opracja jest propagowana do
        # powiązanych obiektów
        # cascade='merge'

        # Usunięcie obiektu rodzica powoduje usunięcie powiązanych obiektów z bazy danych
        # cascade='save-update, delete',

        # Usuniecie relacji miedzy rodzicem a dzieckiem powoduje automatycznie usuniecie dziecka
        # cascade='delete-orphan, save-update',

        # Usunięcie rodzica z sesji powoduje usunięcie powiązanych obiektów z sesji.
        cascade='expunge, save-update',

        # Włącza wszystkie kaskady: save-update, merge, delete, delete-orphan, expunge.
        # cascade='all'

        # Brak kaskadowania – żadne operacje nie są propagowane do obiektów podrzędnych.
        # cascade='none'
    )

class Player(Base):
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relacja Team
    # Konfigurujemy klucz obcy, który bedzie w bazie danych
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'), nullable=False)

    #Konfigurujemy obiekt, ktory pozwoli nam na prace z relacja na poziomie ORM
    team: Mapped[Team] = relationship(back_populates='players')


def main() -> None:
    metadata = Base.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)

    # ------------------------------------------------------------
    # cascade='save-update'
    # ------------------------------------------------------------
    # with Session(engine) as session:
    #     try:
    #        team = Team(name='Team A', players=[
    #            Player(name='Player 1'),
    #            Player(name='Player 2')
    #        ])
    #        session.add(team)
    #        session.commit()
    #
    #        # Aktualizujemy nazwę gracza
    #        team.players[0].name = 'Upadated Player 1'
    #        session.commit() # Zmiana nazwy gracza jest automatycznie zapisywania w bazie danych

    # ------------------------------------------------------------
    # cascade='merge'
    # ------------------------------------------------------------

    # with Session(engine) as session:
    #     try:
    #         team = Team(name='Team A', players=[Player(name='Player 1')])
    #         session.add(team)
    #         session.commit()
    #
    #     except Exception as e:
    #         print(e)
    #         session.rollback()
    #     finally:
    #         print('Sesja została zakończona')
    #
    # with Session(engine) as session:
    #     try:
    #         detached_team = Team(id=1, name='Updated Team A', players=[Player(id=1, name="Updated Player 1")])
    #         session.merge(detached_team)
    #         session.commit()
    #     except Exception as e:
    #         print(e)
    #         session.rollback()
    #     finally:
    #         print('Sesja została zakończona')

    # --------------------------------------------------------------------------
    # cascade = 'delete'
    # --------------------------------------------------------------------------
    # with Session(engine) as session:
    #     # team = Team(name='Team A', players=[
    #     #     Player(name='Player 1'),
    #     #     Player(name='Player 2')
    #     # ])
    #     # session.add(team)
    #     # session.commit()
    #
    #     team_db = session.get(Team, 1)
    #     session.delete(team_db)
    #     session.commit()

    # --------------------------------------------------------------------------
    # cascade = 'delete-orphan'
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # cascade = 'delete-orphan'
    # --------------------------------------------------------------------------
    # with Session(engine) as session:
    #     # team = Team(name='Team A', players=[Player(name="Player 1")])
    #     # session.add(team)
    #     # session.commit()
    #
    #     team = session.get(Team, 1)
    #     team.players.pop(0)
    #     session.commit()

    # --------------------------------------------------------------------------
    # cascade = 'expunge'
    # --------------------------------------------------------------------------
    with Session(engine) as session:
        # team = Team(name='Team A', players=[Player(name="Player 1")])
        # session.add(team)
        # session.commit()

        team = session.get(Team, 1)
        team.players[0].name = 'UPDATED'
        session.expunge(team)
        session.commit()

if __name__ == '__main__':
    main()