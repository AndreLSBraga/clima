from flask import Flask
import logging
from app.blueprints.pagina_inicial import pagina_inicial
from app.blueprints.pagina_final import pagina_final
from app.blueprints.sugestao import sugestao
from app.blueprints.gestor import gestor, configura_senha
from app.blueprints.configuracoes import  configuracoes, configuracoes_usuario, configuracoes_gestor, configuracoes_salvar_alteracoes
from app.blueprints.dashboard import dashboard
from app.blueprints.responder import responder
from app.utils.db import close_db

def create_app():
    app = Flask(__name__,  static_url_path='/static')
    
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
    app.register_blueprint(configuracoes)
    app.register_blueprint(configuracoes_usuario)
    app.register_blueprint(configuracoes_gestor)
    app.register_blueprint(configuracoes_salvar_alteracoes)
    app.register_blueprint(configura_senha)
    # Finaliza a conexão com o banco de dados
    app.teardown_appcontext(close_db)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)
