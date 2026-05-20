from sqlalchemy import ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import (DeclarativeBase, relationship, Session, Mapped, mapped_column, joinedload, selectinload,
                            subqueryload, contains_eager)


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

        # --------------------------------------------------------------------------------------------------------------
        # Lazy loading (lazy='select') - filtrowanie listy Python
        # W tym podejsciu filtrowanie odbywa sie na liscie Python, trzeba dociagnac dane na temat players
        # dla konkretnego team + mamy problem select n + 1
        # teams = session.query(Team).filter(Team.name.like('Team%')).all()
        # for team in teams:
        #     filtred_players = [player for player in team.players if player.name == "Player 1"]
        #     print(filtred_players)

        # --------------------------------------------------------------------------------------------------------------
        # Lazy loading (lazy='select') - filtrowanie po stronie SQL
        # teams = session.query(Team).filter(Team.name.like('Team%')).all()
        # for team in teams:
        #     # Dalej masz select n +1 problem ale filtrowanie players odbywa się na poziomie sql
        #     filtred_players = session.query(Player).filter(
        #         Player.team_id == team.id,
        #         Player.name.like('Player%')
        #     ).all()
        #     print(filtred_players)

        # --------------------------------------------------------------------------------------------------------------
        # Eager Loading (joinedload)
        # W przypadku tego kodu dostajesz warning:
        # : SAWarning: SELECT statement has a cartesian product between FROM element(s) "players" and FROM element
        # "players_1".
        # Ten warning wskazuje, że zapytanie SQL generowane przez SQLAlchemy tworzy iloczyn kartezjański między
        # tabelami players i players_1. Jest to nieefektywne i nieprawidłowe, ponieważ brak określenia warunków
        # dołączenia (ON) między tymi tabelami prowadzi do połączenia każdego rekordu z każdym.
        # Iloczyn kartezjański to sytuacja, w której każda para wierszy z tabel jest łączona. W Twoim
        # przypadku był spowodowany przez brak warunku połączenia między tabelami Team i Player oraz
        # konflikt między joinedload a dodatkowymi filtrami w zapytaniu.

        # joinedload(Team.players): Automatycznie generuje LEFT OUTER JOIN między Team i Player, aby załadować
        # całą relację players.
        # Player.name.like('Player%'): SQLAlchemy dodaje kolejną instancję tabeli players do sekcji FROM (jako players_1),
        # ale nie określa, w jaki sposób ta dodatkowa tabela jest powiązana z innymi tabelami.

        # teams = session.query(Team).options(joinedload(Team.players)).filter(
        #     Team.name.like('Team%'),
        #     Player.name.like('Player%')
        # ).all()
        # print(teams)
        # print(teams[0].players)

        # ILOCZYN KARTEZJANSKI

        # Tabela A:
        # ID	Name
        #  1	Alice
        #  2	Bob

        # Tabela B:
        # ID	Value
        #  1	100
        #  2	200
        #  3	300

        # Kiedy doprowadzisz do iloczynu kartezjanskiego otrzymasz:
        # A.ID	A.Name	B.ID	B.Value
        #  1	Alice	1	    100
        #  1	Alice	2	    200
        #  1	Alice	3	    300
        #  2	Bob	    1	    100
        #  2	Bob	    2	    200
        #  2	Bob	    3	    300

        # WNIOSEK: options(joinedload)  jest nieefektywny, kiedy zaczynasz jednoczesnie
        # filtrowac po players - UNIKAC w tej wersji

        # --------------------------------------------------------------------------------------------------------------
        # --> Eager Loading (join zamiast joinedload)
        # teams = session.query(Team).join(Team.players).filter(
        #     Team.name.like('Team%'),
        #     Player.name.like('Player%')
        # ).all()
        # print(teams)
        #
        # # SQLAlchemy nie wie, że dane z JOIN są częścią relacji players.
        # # Gdy odwołasz się do team.players, SQLAlchemy może wykonać dodatkowy SELECT dla relacji.
        # for team in teams:
        #     print(f"Team: {team.name}, Players: {[player.name for player in team.players]}")

        # WNIOSEK: join pomaga w jdnym select zrobic filtrowanie po Team oraz players ale
        # potem kiedy chcesz odwolac sie do players moze generowac dodatkowy sql

        # --------------------------------------------------------------------------------------------------------------
        # --> Eager Loading (join zamiast joinedload + contains_eager)
        # Kiedy nie chcesz dodatkowego select-a mozesz zastosowac contains_eager
        # Co robi contains_eager?
        # Informuje ORM, że wyniki JOIN dotyczą relacji Team.players.
        # Zapobiega ponownemu ładowaniu relacji players, co może prowadzić do nadmiarowych zapytań.

        # teams = session.query(Team).join(Team.players).filter(
        #     Team.name.like('Team%'),
        #     Player.name.like('Player%')
        # ).options(contains_eager(Team.players)).all()
        # print(teams)
        #
        # for team in teams:
        #     print(f"Team: {team.name}, Players: {[player.name for player in team.players]}")

        # WNIOSEK: zeby join "zrozumial" ze moze to co w pierwszym sql zaciagnac i juz potem nie
        # robic kolejnych sql dla team.players uzyj contains_eager

        # A co jesli nie ma fitrowania po stronie players - joinedload? = jeden select

        # teams = session.query(Team).options(joinedload(Team.players)).all()
        # print(teams)
        # for team in teams:
        #     print(f"Team: {team.name}, Players: {[player.name for player in team.players]}")

        # A co jesli nie ma fitrowania po stronie players - join?
        print('*********************')
        teams = session.query(Team).join(Team.players).all()
        print(teams)
        for team in teams:
            print(f"Team: {team.name}, Players: {[player.name for player in team.players]}")


if __name__ == '__main__':
    main()