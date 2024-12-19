from flask import Flask, request, session
import logging
from flask_babel import Babel, _
from app.blueprints.pagina_inicial import pagina_inicial
from app.blueprints.pagina_final import pagina_final
from app.blueprints.sugestao import sugestao
from app.blueprints.gestor import gestor, configura_senha
from app.blueprints.configuracoes import  configuracoes, configuracoes_usuario, configuracoes_gestor, configuracoes_salvar_alteracoes, configuracoes_reset_senha
from app.blueprints.configuracoes import configuracoes_pesquisa_gestor
from app.blueprints.dashboard import dashboard, dashboard_categoria, dashboard_sugestoes, dashboard_area, dashboard_categoria_area, dashboard_lideres
from app.blueprints.responder import responder
from app.utils.db import close_db

def get_locale():
    supported_languages = ['pt', 'es']  # Lista de idiomas suportados
    lang = request.args.get('lang')

    if lang and lang in supported_languages:
        session['lang'] = lang
    else:
        lang = session.get('lang', request.accept_languages.best_match(supported_languages))
        if not lang:
            lang = 'pt'
        session['lang'] = lang 

    app.logger.debug(f'Selected language: {session["lang"]}')
    return session['lang']

def create_app():
    app = Flask(__name__,  static_url_path='/static')
    
    # Configuração de Babel
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    babel = Babel(app, locale_selector=get_locale)

    # Configuração de chave secreta
    app.secret_key = 'your_secret_key'
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # Registro de Blueprints
    app.register_blueprint(pagina_inicial)
    app.register_blueprint(sugestao)
    app.register_blueprint(gestor)
    app.register_blueprint(responder)
    app.register_blueprint(pagina_final)
    app.register_blueprint(dashboard)
    app.register_blueprint(dashboard_categoria)
    app.register_blueprint(dashboard_sugestoes)
    app.register_blueprint(dashboard_area)
    app.register_blueprint(dashboard_categoria_area)
    app.register_blueprint(dashboard_lideres)
    app.register_blueprint(configuracoes)
    app.register_blueprint(configuracoes_usuario)
    app.register_blueprint(configuracoes_gestor)
    app.register_blueprint(configuracoes_salvar_alteracoes)
    app.register_blueprint(configura_senha)
    app.register_blueprint(configuracoes_reset_senha)
    app.register_blueprint(configuracoes_pesquisa_gestor)
    # Finaliza a conexão com o banco de dados
    app.teardown_appcontext(close_db)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)
