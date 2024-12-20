from flask import Blueprint, render_template, current_app as app, request, session, flash
from app.utils.db_consultas import consulta_categorias, consulta_fk_categoria_pela_desc_categoria
from app.utils.db_dml import insert_resposta
from flask_babel import _, gettext

pagina_final = Blueprint('pagina_final', __name__)

@pagina_final.route('/Sugerir', methods=['GET', 'POST'])
def pagina_final_view():

    lang = session.get('lang', 'pt')
    if lang:
        if lang == 'pt':
            fk_pais = 3
        if lang =='es':
            fk_pais = 1
    grupo_categorias = consulta_categorias(fk_pais)
    categorias = []

    for categoria in grupo_categorias:
        categorias.append(categoria[0])

    if request.method == 'POST':
        check_box_auto_identificacao = request.form.get('auto_identificacao')
        if check_box_auto_identificacao:
            auto_identificacao = 1
        else:
            auto_identificacao = 0

        resposta = {
            'sugestao':request.form.get('sugestao'),
            'auto_identificacao_sugestao': auto_identificacao,
            'fk_categoria': consulta_fk_categoria_pela_desc_categoria(request.form.get('categoria'))
        }

        dados_usuario = session['dados']
        insert_resposta(dados_usuario,resposta, 'sugestao')
        flash("Sugestão enviada com sucesso!","success")
    return render_template('pagina_final.html', categorias=categorias, lang=lang)