from flask import Blueprint, render_template

login_gestor = Blueprint('login_gestor', __name__)

@login_gestor.route('/')
def login_gestor_view():
    
    return render_template('login_gestor.html')