from sqlalchemy import ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, Session, Mapped, mapped_column


USERNAME = 'user'
PASSWORD = 'user1234'
DATABASE = 'db_1'
PORT = 3307
URL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{DATABASE}'

engine = create_engine(URL, echo=True)


class Base(DeclarativeBase):
    pass


"""
Omówienie kluczowych elementow ponizszej relacji

1. Parent i Child
-> Team jest stroną pasywną, ponieważ nie przechowuje bezpośrednio klucza obcego oraz rodzicem.
-> Player jest stroną aktywną, ponieważ przechowuje klucz obcy team_id oraz dzieckiem.

2. Relacja:
-> relationship w modelu Team tworzy dynamiczną listę graczy (players) powiązanych z zespołem.
-> relationship w modelu Player tworzy połączenie z modelem Team.

3. Ładowanie danych (lazy vs eager):
Domyślnie SQLAlchemy stosuje lazy loading – dane są ładowane, gdy są potrzebne, przez dodatkowe zapytanie.
Możemy zmienić sposób ładowania:
Lazy loading (lazy="select") – dane są ładowane na żądanie.
Eager loading (lazy="joined") – dane są ładowane natychmiast za pomocą jednego zapytania SQL.

"""

class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relacja z Player
    players: Mapped[list["Player"]] = relationship(back_populates='team', lazy='select')

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

    with Session(engine) as session:
        try:
            # Wstawianie danych wersja 1
            # team1 = Team(name='Team A')
            # team2 = Team(name='Team B')
            #
            # player1 = Player(name='Kama', team=team1)
            # player2 = Player(name='Andrzej', team=team1)
            # player3 = Player(name='Magda', team=team2)

            # Wstawianie wszystko osobno
            # session.add_all([team1, team2, player1, player2, player3])

            #Wstawianie tylko players, teams beda i tak wstaione bo orm je wykryje
            # session.add_all([player1,player2,player3])

            # Mozesz od razu kiedy tworzysz player tworzyc tez team
            # player1 = Player(name="Alice", team=Team(name='Team A'))
            # player2 = Player(name="Bob", team=player1.team)
            # player3 = Player(name="Charlie", team=Team(name='Team B'))
            # session.add_all([player1, player2, player3])

            # Możesz utowrzyć team z lista players i wstawiać od stony team

            team1 = Team(name='Team A', players=[
                Player(name='Kama'),
                Player(name='Andrzej')
            ])
            team2 = Team(name='Team B', players=[
                Player(name='Magda'),
                Player(name='Pawel')
            ])
            session.add_all([team1, team2])
            session.commit()

        except Exception as e:
            print(e)
            session.rollback()
        finally:
            print('Sesja została zakończona')


if __name__ == '__main__':
    main()