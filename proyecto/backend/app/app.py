from flask import Flask, render_template

#render_template sirve para poder devolver archivos HTML
app = Flask(__name__)

#Ruta raiz
@app.route("/")

def index():
    return "Sistema de Reservas - API Backend"
if (__name__ == '__main__' ) : 
    #con el debug @ true activamos el modo depurador para poder ver los cambios en vivo
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

