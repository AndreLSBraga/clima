from flask import Blueprint, render_template

pagina_final = Blueprint('pagina_final', __name__)

@pagina_final.route('/Sugerir')
def pagina_final_view():
    
    return render_template('pagina_final.html')