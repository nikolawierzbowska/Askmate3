from flask import Flask, render_template, request, redirect, url_for
import data_manager, util

app = Flask(__name__)


@app.route('/')
def main_page():
    order_by = request.args.get('order_by')
    order = request.args.get('order_direction')
    if order is not None and order_by is not None:
        questions = data_manager.get_sorted_questions(order_by, order)
    else:
        questions = data_manager.get_sorted_questions("submission_time", "DESC")
    latest_questions = questions[:5]
    return render_template('main.html', questions=latest_questions)


@app.route('/list')
def list_questions():
    order_by = request.args.get('order_by')
    order = request.args.get('order_direction')
    if order is not None and order_by is not None:
        questions = data_manager.get_sorted_questions(order_by, order)
        return render_template("list.html", questions=questions)
    else:
        questions = data_manager.get_sorted_questions("submission_time", "DESC")
        return render_template("list.html", questions=questions)


@app.route('/question/<question_id>')
def print_question(question_id):
    data_manager.view_question(question_id)
    question = data_manager.get_question_data_by_id(question_id)
    comments = data_manager.get_comments_by_question_id(question_id)
    answers = data_manager.get_answers_by_question_id(question_id)
    comments_to_answers = data_manager.get_comments_of_answers(question_id)
    tags = data_manager.get_tags_by_question_id(question_id)
    return render_template('question.html', question=question, answers=answers, comments_to_answers=comments_to_answers,
                           comments=comments, tags=tags)


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        image_file = request.files['image']
        image_path = util.save_image(image_file) if image_file.filename != '' else None
        new_question_id = data_manager.add_question(title, message, image_path)
        return redirect(f'/question/{new_question_id}')
    else:
        return render_template('add_question.html')


@app.route('/question/<question_id>/new_answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if request.method == 'POST':
        message = request.form['message']
        image_file = request.files['image']
        image_path = util.save_image(image_file) if image_file.filename != '' else None
        data_manager.add_answer(message, question_id, image_path)
        return redirect(f'/question/{question_id}')
    elif request.method == 'GET':
        return render_template('add_answer.html', question_id=question_id)


@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    image_paths = data_manager.delete_question(question_id)
    util.delete_image_files(image_paths)
    return redirect('/list')


@app.route('/answer/<answer_id>/delete')
def delete_answer(answer_id):
    question_id, image_path = data_manager.delete_answer_by_id(answer_id)
    util.delete_image_files([image_path])
    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def update_question(question_id):
    question = data_manager.get_question_data_by_id(question_id)
    if request.method == 'GET':
        return render_template('edit_question.html', question=question)
    elif request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        new_image_file = request.files['image']
        remove_image_checkbox = request.form.get('remove_image')
        if 'image' in request.files and new_image_file.filename != '':
            new_image_path = util.save_image(new_image_file)
            data_manager.update_question(title, message, question_id, remove_image_checkbox,
                                         new_image_path)
        else:
            data_manager.update_question(title, message, question_id, remove_image_checkbox)
        return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/vote_up')
def vote_up_questions(question_id):
    source = request.args.get('source')
    if source == 'question':
        data_manager.vote_on_question(question_id, 'up')
        return redirect(f'/question/{question_id}')
    elif source == 'search':
        search_phrase = request.args.get('q')
        data_manager.vote_on_question(question_id, 'up')
        return redirect(url_for('search', q=search_phrase))
    else:
        data_manager.vote_on_question(question_id, 'up')
        return redirect('/list')


@app.route('/question/<question_id>/vote_down')
def vote_down_questions(question_id):
    source = request.args.get('source')
    if source == 'question':
        data_manager.vote_on_question(question_id, 'down')
        return redirect(f'/question/{question_id}')
    elif source == 'search':
        search_phrase = request.args.get('q')
        data_manager.vote_on_question(question_id, 'down')
        return redirect(url_for('search', q=search_phrase))
    else:
        data_manager.vote_on_question(question_id, 'down')
        return redirect('/list')


@app.route('/answer/<answer_id>/vote_up')
def vote_up_answers(answer_id):
    question_id = data_manager.vote_on_answer(answer_id, "up")
    return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/vote_down')
def vote_down_answers(answer_id):
    question_id = data_manager.vote_on_answer(answer_id, "down")
    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/new_comment', methods=['GET', 'POST'])
def add_comment_to_question(question_id):
    if request.method == 'POST':
        new_comment = request.form['message']
        data_manager.add_comment_question(question_id, new_comment)
        return redirect(f'/question/{question_id}')
    elif request.method == 'GET':
        return render_template('add_comment_to_question.html', question_id=question_id)


@app.route('/answer/<answer_id>/new_comment', methods=['GET', 'POST'])
def add_comment_to_answer(answer_id):
    if request.method == 'POST':
        message = request.form['message']
        question_id = data_manager.add_comment_to_answer(answer_id, message)
        return redirect(f'/question/{question_id}')
    elif request.method == 'GET':
        question_id = data_manager.get_question_id_by_answer_id(answer_id)
        return render_template('add_comment_to_answer.html', answer_id=answer_id, question_id=question_id)


@app.route('/question/<question_id>/new_tag', methods=['GET', 'POST'])
def add_tag(question_id):
    if request.method == 'POST':
        tags = request.form.getlist('tags')
        new_tag = request.form.get('new_tag_check_box')
        if new_tag:
            new_tag_name = request.form.get('new_tag_name')
            tags.append(new_tag_name)
        data_manager.add_tags(question_id, tags)
        return redirect(f'/question/{question_id}')
    elif request.method == 'GET':
        tags = data_manager.get_tags()
        return render_template('add_tag.html', tags=tags, question_id=question_id)


@app.route('/search')
def search():
    search_phrase = request.args.get('q')
    questions = data_manager.get_questions_by_search_phrase(search_phrase)
    for question in questions:
        question['title'] = highlight_search_phrase(question['title'], search_phrase)
        question['message'] = highlight_search_phrase(question['message'], search_phrase)
        question['answers'] = [highlight_search_phrase(answer, search_phrase) for answer in question['answers']]
    questions = [question for question in questions if
                 search_phrase.lower() in question['title'].lower() or search_phrase.lower()
                 in question['message'].lower() or any(
                     search_phrase.lower() in answer.lower() for answer in question['answers'])]
    return render_template('search.html', questions=questions, search_phrase=search_phrase)


@app.route('/comments/<comment_id>/delete')
def delete_comments(comment_id):
    question_id = data_manager.get_question_id_by_comment_question_or_answer(comment_id)
    data_manager.delete_comment(comment_id)
    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/delete_image')
def delete_image_to_question(question_id):
    image_path = data_manager.delete_image_from_question(question_id)
    util.delete_image_files([image_path])
    return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/delete_image')
def delete_image_to_answer(answer_id):
    question_id, image_path = data_manager.delete_image_from_answer(answer_id)
    return redirect(f'/question/{question_id}')


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
def update_comment(comment_id):
    if request.method == 'POST':
        message = request.form['message']
        data_manager.update_comment(comment_id, message)
        question_id = data_manager.get_question_id_by_comment_question_or_answer(comment_id)
        return redirect(f'/question/{question_id}')
    elif request.method == 'GET':
        comment = data_manager.get_comment_by_id(comment_id)
        question_id = data_manager.get_question_id_by_comment_question_or_answer(comment_id)
        return render_template('edit_comments.html', comment=comment, question_id=question_id)


@app.template_filter('highlight_search_phrase')
def highlight_search_phrase(value, search_phrase):
    if search_phrase.lower() not in value.lower():
        return value

    start_index = value.lower().index(search_phrase.lower())
    stop_index = start_index + len(search_phrase)
    original_substring = value[start_index:stop_index]
    highlighted = f'<span style="background-color:lightgreen;">{original_substring}</span>'
    highlighted_value = f'{value[0:start_index]}{highlighted}{value[stop_index:]}'

    return highlighted_value


if __name__ == '__main__':
    app.run(debug=True)
