from flask import Blueprint, render_template

configuracoes = Blueprint('configuracoes', __name__)

@configuracoes.route('/configuracoes')
def configuracoes_view():
    
    return render_template('configuracoes.html')