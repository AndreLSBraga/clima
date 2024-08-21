from flask import Blueprint, render_template

sugestao = Blueprint('sugestao', __name__)

@sugestao.route('/')
def sugestao_view():
    return render_template('sugestao.html')