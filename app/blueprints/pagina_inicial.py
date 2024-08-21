from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from app.utils.auth import valida_id
pagina_inicial = Blueprint('pagina_inicial', __name__)

@pagina_inicial.route('/', methods=['GET', 'POST'])
def pagina_inicial_view():

    if request.method == 'POST':
        user_id = request.form['user_id']
        data_nascimento = request.form['data_nascimento'] 
        if not user_id or not data_nascimento:
            flash("Preencha todos os campos", "warning")
        elif valida_id(user_id,data_nascimento):
            return redirect(url_for('responder.responder_view'))
        else:
            return render_template('pagina_inicial.html')

    return render_template('pagina_inicial.html')
