from sqlalchemy import ForeignKey, Integer, String, create_engine, select, or_, and_
from sqlalchemy.orm import (DeclarativeBase, relationship, Session, Mapped, mapped_column, joinedload, selectinload,
                            subqueryload, contains_eager, with_parent)
from sqlalchemy.sql import exists


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

    )

    # Możesz dodać specjalne filtry w relationship()
    # za pomocą primaryjoin

    active_players: Mapped[list["Player"]] = relationship(
        'Player',
        primaryjoin='and_(Player.team_id == Team.id, Player.name.like("%1%"))',
        lazy='select'
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
    # metadata = Base.metadata
    # metadata.drop_all(engine)
    # metadata.create_all(engine)

    # with Session(engine) as session:
    #     team = Team(name='Team A', players=[
    #         Player(name='Player 1'),
    #         Player(name='Player 2')
    #     ])
    #     session.add(team)
    #     session.commit()

    # Filtrowanie danych

    with Session(engine) as session:

        # ------------------------------------------------------------------------------------------
        # EXISTS - sprawdzenie, czy istnieje gracz, ktory spełnia warunki

        has_exists = session.query(exists().where(Player.name == 'Player 1')).scalar()
        print(f'===1====: {has_exists}')

        # ------------------------------------------------------------------------------------------
        # has - sprawdzenie warunku na relacji jednokierunkowej
        # Jesli pracujesz z relacja w druga strone (np. od Player do Team), mozesz uzyc has()
        # do sprawdzenia, czy powiazany obiekt Team spelnia warunek.

        players = session.query(Player).filter(Player.team.has(Team.name.like('Team%'))).all()
        print(f'===2====: {players}')

        # ------------------------------------------------------------------------------------------
        # contains - sprawdzanie, czy kolekcja zwiera dany obiekt

        player = session.query(Player).filter(Player.name == 'Player 1').first()
        teams = session.query(Team).filter(Team.players.contains(player)).all()
        print(f'===3====: {teams}')

        # ------------------------------------------------------------------------------------------
        # with_parent - pobieranie powiazanych elementow
        # Funkcja with_parent pozwala na filtracje powiazanych elementow w kolekcji players
        # bezposrednio w kontekscie rodzica

        team = session.query(Team).filter(Team.name == "Team A").first()
        players = session.query(Player).filter(with_parent(team, Team.players)).all() # pobierze graczy powiązanych z Team
        print(f'===4====: {players}')

        # ------------------------------------------------------------------------------------------
        # distinct - eliminowanie duplikatow
        # in_ - dopasowanie do wielu wartosci

        teams = session.query(Team).filter(Team.players.any(Player.name.in_(['Player 1', 'Player 2']))).distinct().all()
        print(f'===5====: {teams}')

        # ------------------------------------------------------------------------------------------
        # isnot - sprawdzanie braku powiazan
        # Jesli chcesz sprawdzic, czy kolekcja jest pusta np. druzyna bez graczy

        teams_without_players = session.query(Team).filter(or_(
            ~Team.players.any(),  # Druzyny bez zadnych graczy
            Team.players == None  # Czy mamy cokolwiek przypisane do kolekcji
        )).all()
        print(f'===6====: {teams_without_players}')

        teams = session.query(Team).filter(Team.players.any(and_(Player.name.like('Player%'), Player.id > 1))).all()
        print(f'===7====: {teams}')

        team = session.query(Team).filter(Team.name == 'Team A').first()
        print(f'===8====: {team.active_players}')


if __name__ == '__main__':
    main()