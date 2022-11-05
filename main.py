import json

from flask import Flask, request
from flask_restful import Resource, Api

from PyMovieDb import IMDB
from rotten_tomatoes_scraper.rt_scraper import MovieScraper

app = Flask(__name__)
api = Api(app)

imdb = IMDB()

class Pelicula(Resource):
    #Se agregan los metodos aca
    def get(self):
        query = request.args.get('buscar')
        
        #Se obtiene la informacion de la pelicula desde IMDB
        infoPeliculasIMDB = imdb.search(query)
        #peliculaIMDB = imdb.get_by_id("tt2283362")
        #Se convierte el string json para poder manejarlo como un diccionario
        infoPeliculasIMDB  = json.loads(infoPeliculasIMDB)
        
        #if (infoPeliculasIMDB['result_count'] > 0):
        listaPeliculasIMDB = infoPeliculasIMDB['results']

        #pelicula = listaPeliculasIMDB[1]
        #print("test" + str(pelicula), flush=True) 
            

        #Se obtiene la informacion de la pelicula desde Rotten Tomatoes
        movie_scraper = MovieScraper(movie_title=query)
        movie_scraper.extract_metadata()
        peliculaRT = movie_scraper.metadata
        
        return {'data': {'peliculaIMDB': listaPeliculasIMDB, 'peliculaRT': peliculaRT}}, 200 

api.add_resource(Pelicula,'/pelicula')

if __name__ == '__main__':
    app.run()

