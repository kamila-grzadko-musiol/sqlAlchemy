from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase, Session, Mapped, mapped_column


USERNAME = 'user'
PASSWORD = 'user1234'
DATABASE = 'db_1'
PORT = 3307
URL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{DATABASE}'

engine = create_engine(URL, echo=True)

# Kiedy potrzebujesz tabele posrednia tylko po to, zeby "spiac" dwie inne tabele
# relacje, nie zamierzasz nia zarzadzac, umieszczac w niej dodatkowych kolumn
# poza kluczami obcymi, nie ma potrzeby robic dla niej osobnej klasu modelu ORM.

metadata = MetaData()


# Association table
actor_movie_association = Table(
    'actors_movies',
    metadata,
    Column('actor_id', ForeignKey('actors.id'), primary_key=True),
    Column('movie_id', ForeignKey('movies.id'), primary_key=True),
)


class Base(DeclarativeBase):
    metadata = metadata


class Actor(Base):
    __tablename__ = 'actors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    movies: Mapped[list["Movie"]] = relationship(
        "Movie",
        secondary=actor_movie_association,
        back_populates="actors",
        lazy='select'
    )


class Movie(Base):
    __tablename__ = 'movies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)

    actors: Mapped[list[Actor]] = relationship(
        "Actor",
        secondary=actor_movie_association,
        back_populates="movies",
        lazy='select'
    )


def main() -> None:
    # metadata.drop_all(engine)
    # metadata.create_all(engine)
    #
    # with Session(engine) as session:
    #     actor1 = Actor(name='Actor 1')
    #     actor2 = Actor(name='Actor 2')
    #     movie1 = Movie(title='Movie 1')
    #     movie2 = Movie(title='Movie 2')
    #
    #     actor1.movies.extend([movie1, movie2])
    #     actor2.movies.append(movie1)
    #     session.add_all([actor1, actor2, movie1, movie2])
    #     session.commit()

    with Session(engine) as session:
        print('Actors and their movies')
        actors = session.query(Actor).all()
        for actor in actors:
            print(f'Actor: {actor.name}, Movies: {[movie.title for movie in actor.movies]}')

        print('Movie and their actors')
        movies = session.query(Movie).all()
        for movie in movies:
            print(f'Movie: {movie.title}, Actors: {[actor.name for actor in movie.actors]}')


if __name__ == '__main__':
    main()