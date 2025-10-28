from flask import Flask,render_template

app = Flask(__name__)

#Ruta raiz
@app.route("/")

def index():
    return "hola mundo"
if (__name__ == '__main__' ) : {
    #con el debug @ true activamos el modo depurador para poder ver los cambios en vivo
    app.run(debug=True, port=5000)
}   
