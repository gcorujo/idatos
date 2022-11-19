import json
import csv
import difflib

from flask import Flask, request
from flask_restful import Resource, Api

from rotten_tomatoes_scraper.rt_scraper import MovieScraper
from rotten_tomatoes_scraper.rt_scraper import DirectorScraper

app = Flask(__name__)
api = Api(app)

class Pelicula(Resource):
    #Se agregan los metodos aca
    def get(self):
        query = request.args.get('buscar')
        
        moviesTitleIMDB = []
        indice = 0
        with open('imdb_top_1000.csv','rt') as dataset:
            data = csv.reader(dataset)
            for movie in data:
                moviesTitleIMDB.append(movie[1])
        dataset.close() 

        titlesMap = {}
        for i,nombre in enumerate(moviesTitleIMDB):
            titlesMap[nombre] = i 
        
        #Se busca los nombres de las peliculas que matchean mejor con la query
        titlesMatchesIMDB = difflib.get_close_matches(query,titlesMap.keys())
        titleIMDB = titlesMatchesIMDB[0]
        indicePeliculaElegida = titlesMap[titleIMDB]
        print(indicePeliculaElegida)

        with open('imdb_top_1000.csv','rt') as dataset:
            data = csv.reader(dataset)
            for i, row in enumerate(data):
                if i == indicePeliculaElegida:
                    infoPelicula = row 
                    break
        dataset.close()
        
        #Info pelicula del dataset de IMDB
        yearIMDB = infoPelicula[2]
        genresIMDB = infoPelicula[5]
        scoreIMDB = infoPelicula[6]
        directorIMDB = infoPelicula[9]

        #Se busca en el web scrapper de RT todas las peliculas que hizo el director
        director_scraper = DirectorScraper(director_name=directorIMDB)
        director_scraper.extract_metadata()
        moviesTitleRT = list(director_scraper.metadata.keys())
        moviesInfoRT = director_scraper.metadata
        
        #Se matchea la lista de peliculas del director con el nombre de la pelicula del dataset de IMDB
        titlesMatchesRT = difflib.get_close_matches(titleIMDB, moviesTitleRT)
        #titleMovieRT = titlesMatchesRT[0] 
       
        movieTitleRT = ''
        for titleMovieRT in titlesMatchesRT:
            #Se obtiene la informacion de la pelicula en RT
            yearRT = moviesInfoRT[titleMovieRT]['Year']
            scoreRT = moviesInfoRT[titleMovieRT]['Score_Rotten'] 
        
            if yearRT == yearIMDB:
                movieTitleRT = titleMovieRT
                break
        
        movie_scraper = MovieScraper(movie_title=movieTitleRT)
        movie_scraper.extract_metadata()     
       
        scoreRT = movie_scraper.metadata['Score_Rotten']
        scoreAudienceRT = movie_scraper.metadata['Score_Audience']
        genresRT = movie_scraper.metadata['Genre']
       
        #Integracion de Generos 
        for genre in genresRT:
            if (genre == 'Mystery&thriller'):
                print('Encontro el genero')


        return {'data': {'IMDB': { 'titleIMDB': titleIMDB, 'scoreIMDB': scoreIMDB, 'directorIMDB': directorIMDB, 'yearIMDB': yearIMDB, 'genresIMDB': genresIMDB}, 'RottenTomates': {'titleRT': titleMovieRT, 'scoreRT': scoreRT, 'scoreAudienceRT': scoreAudienceRT, 'genresRT': genresRT} } }, 200 

api.add_resource(Pelicula,'/pelicula')

if __name__ == '__main__':
    app.run()

