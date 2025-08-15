from flask import Blueprint, render_template, request
# Импортируйте вашу функцию взаимодействия с LLM
# from .llm import get_llm_response

bp = Blueprint('main', __name__)

@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    prompt = ''
    response = None
    if request.method == 'POST':
        prompt = request.form.get('prompt', '')
        # Здесь вызовите вашу функцию для получения ответа от LLM
        # response = get_llm_response(prompt)
        response = f"Тестова відповідь на: {prompt}"  # Замените на реальный вызов
    return render_template('dashboard.html', prompt=prompt, response=response)