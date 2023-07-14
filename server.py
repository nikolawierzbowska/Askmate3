import bcrypt as bcrypt
from flask import Flask, render_template, request, redirect, url_for, session

import data_manager
import util
import config

app = Flask(__name__)
app.secret_key = "96449384-97ca-4e24-bdec-58a7dc8f59fc"


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        return render_template("registration.html")
    else:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeat_password']

        errors = []

        if not password == repeat_password:
            errors.append("Passwords not match")

        if len(password) not in config.PASSWORD_LENGTH:
            errors.append(f"Password should have from {config.PASSWORD_LENGTH_MIN} to {config.PASSWORD_LENGTH_MAX} "
                          f"characters.")
        if len(username) not in config.USERNAME_LENGTH:
            errors.append(f"Username should have from {config.USERNAME_LENGTH_MIN} to {config.USERNAME_LENGTH_MAX} "
                          f"characters.")
        if data_manager.get_user_by_name(username, email):
            errors.append("User with this name or email already exists.")
        if len(errors):
            return render_template("registration.html", errors=errors)

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user_id = data_manager.add_user(username, email, hashed_password.decode("utf-8"))

        if user_id:
            return render_template("registration_confirm.html")
        else:
            return render_template("registration.html", errors='Unknown error, please try later.')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        username_email = request.form['username_email']
        password = request.form['password']
        errors = []
        user = data_manager.get_user_by_name(username_email, username_email)
        if not user:
            errors.append(f'{username_email} not exist')
            return render_template("login.html", errors=errors)

        is_password_correct = bcrypt.checkpw(password.encode("utf-8"), user['password'].encode("utf-8"))

        if is_password_correct:
            session['username_email'] = username_email
            session['is_logged'] = True
            session['user_id'] = user['id']
            return redirect(f"/user/{user['id']}")
        else:
            return render_template("login.html", errors=['Password incorrect!'])


def is_logged():
    return "is_logged" in session and session["is_logged"]


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect("/")


@app.route('/users')
@util.is_logged_in
def list_users():
    users = data_manager.get_users_list()
    return render_template('list_users.html', users=users, LIST_USERS_HEADERS=config.LIST_USERS_HEADERS)


@app.route('/tags')
def list_tags():
    tags = data_manager.get_tags()
    return render_template('list_tags.html', tags=tags)


@app.route('/answers/<answer_id>/mark_unmark_accepted', methods=['POST'])
@util.is_logged_in
def mark_unmark_answer_as_accepted(answer_id):
    user_id = session['user_id']
    answer = data_manager.get_answer_by_id(answer_id)
    question_id = answer['question_id']
    question = data_manager.get_question_data_by_id(question_id)

    if question['user_id'] == user_id:
        accepted = not answer['is_accepted']
        if accepted and not answer['reputation_status']:
            data_manager.mark_unmark_answer_as_accepted(answer_id, accepted)
            author_id = answer['user_id']
            data_manager.change_reputation(config.GAIN_REPUTATION_ACCEPTED, author_id)
            data_manager.update_reputation_gained(answer_id, True)
        elif not accepted and answer['reputation_status']:
            data_manager.mark_unmark_answer_as_accepted(answer_id, accepted)
            author_id = answer['user_id']
            data_manager.change_reputation(config.LOSE_REPUTATION_ACCEPTED, author_id)
            data_manager.update_reputation_gained(answer_id, False)

    return redirect(f'/question/{question_id}')


@app.route('/user/<user_id>')
@util.is_logged_in
def user_detail_page(user_id):
    users = data_manager.get_users_list()
    user = next(user for user in users if user['id'] == int(user_id))
    questions = data_manager.get_questions_by_user_id(user_id)
    answers = data_manager.get_answers_by_user_id(user_id)
    comments = data_manager.get_comments_by_user_id(user_id)
    return render_template('user_details_page.html', user=user, questions=questions, answers=answers, comments=comments)


@app.route('/')
def main_page():
    questions = data_manager.get_sorted_questions("submission_time", "DESC")
    latest_questions = questions[:5]
    return render_template('main.html', questions=latest_questions, is_logged=is_logged())


@app.route('/list')
def list_questions():
    order_by = request.args.get('order_by')
    order = request.args.get('order_direction')
    columns = [
        {'label': 'Submission Time', 'order_by': 'submission_time'},
        {'label': 'Number of Views', 'order_by': 'view_number'},
        {'label': 'Votes', 'order_by': 'vote_number'},
        {'label': 'Answers', 'order_by': 'number_of_answers'},
        {'label': 'Title', 'order_by': 'title'},
        {'label': 'Message', 'order_by': 'message'}
    ]

    questions = data_manager.get_sorted_questions(order_by, order) if order and order_by else \
        data_manager.get_sorted_questions("submission_time", "DESC")

    return render_template("list.html", questions=questions, columns=columns, is_logged=is_logged())


@app.route('/question/<question_id>')
def print_question(question_id):
    data_manager.view_question(question_id)
    question = data_manager.get_question_data_by_id(question_id)
    comments = data_manager.get_comments_by_question_id(question_id)
    answers = data_manager.get_answers_by_question_id(question_id)
    comments_to_answers = data_manager.get_comments_of_answers(question_id)
    tags = data_manager.get_tags_by_question_id(question_id)
    return render_template('question.html', question=question, answers=answers, comments_to_answers=comments_to_answers,
                           comments=comments, tags=tags, is_logged=is_logged())


@app.route('/add_question', methods=['GET', 'POST'])
@util.is_logged_in
def add_question():
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        image_file = request.files['image']
        image_path = util.save_image(image_file) if image_file.filename != '' else None
        user_id = session['user_id']
        new_question_id = data_manager.add_question(title, message, image_path, user_id)
        return redirect(f'/question/{new_question_id}')
    else:
        return render_template('add_question.html', is_logged=is_logged())

      
@app.route('/question/<question_id>/new_answer', methods=['GET', 'POST'])
@util.is_logged_in
def add_answer(question_id):
    if request.method == 'POST':
        message = request.form['message']
        image_file = request.files['image']
        image_path = util.save_image(image_file) if image_file.filename != '' else None
        user_id = session['user_id']
        data_manager.add_answer(message, question_id, image_path, user_id)
        return redirect(f'/question/{question_id}')
    elif request.method == 'GET':
        return render_template('add_answer.html', question_id=question_id, is_logged=is_logged())


@app.route('/question/<question_id>/delete')
@util.is_logged_in
def delete_question(question_id):
    user_id = session['user_id']
    if user_id  == data_manager.get_user_id_by_question_id(question_id):
        image_paths = data_manager.delete_question(question_id)
        util.delete_image_files(image_paths)
        return redirect('/list')
    else:
        return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/delete')
@util.is_logged_in
def delete_answer(answer_id):
    user_id = session['user_id']
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    if user_id == data_manager.get_user_id_by_answer_id(answer_id):
        question_id, image_path = data_manager.delete_answer_by_id(answer_id)
        util.delete_image_files([image_path])
        return redirect(f'/question/{question_id}')
    else:
        return redirect(f'/question/{question_id}')



@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
@util.is_logged_in
def update_question(question_id):
    user_id = session['user_id']
    question = data_manager.get_question_data_by_id(question_id)
    if request.method == 'GET' and user_id == data_manager.get_user_id_by_question_id(question_id):
        return render_template('edit_question.html', question=question)
    elif request.method == 'POST' and user_id == data_manager.get_user_id_by_question_id(question_id):

        title = request.form['title']
        message = request.form['message']
        new_image_file = request.files['image']
        remove_image_checkbox = request.form.get('remove_image')
        if 'image' in request.files and new_image_file.filename != '':
            new_image_path = util.save_image(new_image_file)
            data_manager.update_question(title, message, question_id, remove_image_checkbox,
                                         new_image_path)
            util.delete_image_files([question['image']])
        else:
            if remove_image_checkbox:
                util.delete_image_files([question['image']])
            data_manager.update_question(title, message, question_id, remove_image_checkbox)
        return redirect(f'/question/{question_id}')
    else:
        return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/vote_up')
@util.is_logged_in
def vote_up_questions(question_id):
    source = request.args.get('source')
    question = data_manager.get_question_data_by_id(question_id)
    data_manager.vote_on_question(question_id, 'up')
    data_manager.change_reputation(config.GAIN_REPUTATION_QUESTION, question['user_id'])
    if source == 'question':
        return redirect(f'/question/{question_id}')
    elif source == 'search':
        search_phrase = request.args.get('q')
        return redirect(url_for('search', q=search_phrase))
    else:
        return redirect('/list')


@app.route('/question/<question_id>/vote_down')
@util.is_logged_in
def vote_down_questions(question_id):
    source = request.args.get('source')
    question = data_manager.get_question_data_by_id(question_id)
    data_manager.vote_on_question(question_id, 'down')
    data_manager.change_reputation(config.LOSE_REPUTATION, question['user_id'])
    if source == 'question':
        return redirect(f'/question/{question_id}')
    elif source == 'search':
        search_phrase = request.args.get('q')
        return redirect(url_for('search', q=search_phrase))
    else:
        return redirect('/list')


@app.route('/answer/<answer_id>/vote_up')
@util.is_logged_in
def vote_up_answers(answer_id):
    data_manager.vote_on_answer(answer_id, "up")
    answer = data_manager.get_answer_by_id(answer_id)
    data_manager.change_reputation(config.GAIN_REPUTATION_ANSWER, answer['user_id'])
    return redirect(f"/question/{answer['question_id']}")


@app.route('/answer/<answer_id>/vote_down')
@util.is_logged_in
def vote_down_answers(answer_id):
    data_manager.vote_on_answer(answer_id, "down")
    answer = data_manager.get_answer_by_id(answer_id)
    data_manager.change_reputation(config.LOSE_REPUTATION, answer['user_id'])
    return redirect(f"/question/{answer['question_id']}")


@app.route('/question/<question_id>/new_comment', methods=['GET', 'POST'])
@util.is_logged_in
def add_comment_to_question(question_id):
    if request.method == 'POST':
        new_comment = request.form['message']
        user_id = session['user_id']
        data_manager.add_comment_question(question_id, new_comment, user_id)
        return redirect(f'/question/{question_id}')
    elif request.method == 'GET':
        return render_template('add_comment_to_question.html', question_id=question_id, is_logged=is_logged())


@app.route('/answer/<answer_id>/new_comment', methods=['GET', 'POST'])
@util.is_logged_in
def add_comment_to_answer(answer_id):
    if request.method == 'POST':
        message = request.form['message']
        user_id = session['user_id']
        question_id = data_manager.add_comment_to_answer(answer_id, message, user_id)
        return redirect(f'/question/{question_id}')
    elif request.method == 'GET':
        question_id = data_manager.get_question_id_by_answer_id(answer_id)
        return render_template('add_comment_to_answer.html', answer_id=answer_id, question_id=question_id,
                               is_logged=is_logged())


@app.route('/question/<question_id>/new_tag', methods=['GET', 'POST'])
@util.is_logged_in
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
    order_by = request.args.get('order_by')
    order_direction = request.args.get('order_direction')
    if search_phrase:
        questions = data_manager.get_questions_by_search_phrase(search_phrase)
        for question in questions:
            question['title'] = highlight_search_phrase(question['title'], search_phrase)
            question['message'] = highlight_search_phrase(question['message'], search_phrase)
            question['answers'] = [highlight_search_phrase(answer, search_phrase) for answer in question['answers']]
        questions = [question for question in questions if
                     search_phrase.lower() in question['title'].lower() or search_phrase.lower()
                     in question['message'].lower() or any(
                         search_phrase.lower() in answer.lower() for answer in question['answers'])]
        if order_by is not None and order_direction is not None:
            questions = data_manager.get_sorted_questions(order_by, order_direction, questions)
        columns = [
            {'label': 'Submission Time', 'order_by': 'submission_time'},
            {'label': 'Number of Views', 'order_by': 'view_number'},
            {'label': 'Votes', 'order_by': 'vote_number'},
            {'label': 'Title', 'order_by': 'title'},
            {'label': 'Message', 'order_by': 'message'}
        ]

        return render_template('search.html', questions=questions, search_phrase=search_phrase,
                               order_by=order_by, order_direction=order_direction, columns=columns,
                               is_logged=is_logged())
    else:
        return redirect('/')


@app.route('/comments/<comment_id>/delete')
@util.is_logged_in
def delete_comments(comment_id):
    question_id= data_manager.get_question_id_by_comment_question_or_answer(comment_id)
    user_id = session['user_id']
    if user_id == data_manager.get_user_id_by_comment_id(comment_id):
        data_manager.delete_comment(comment_id)
    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/delete_image')
@util.is_logged_in
def delete_image_to_question(question_id):
    user_id = session['user_id']
    if user_id == data_manager.get_user_id_by_question_id(question_id):
        image_path = data_manager.delete_image_from_question(question_id)
        util.delete_image_files([image_path])
    return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/delete_image')
@util.is_logged_in
def delete_image_to_answer(answer_id):
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    user_id = session['user_id']
    if user_id == data_manager.get_user_id_by_answer_id(answer_id):
        question_id, image_path = data_manager.delete_image_from_answer(answer_id)
        util.delete_image_files(image_path)
    return redirect(f'/question/{question_id}')


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
@util.is_logged_in
def update_comment(comment_id):
    user_id = session['user_id']
    question_id = data_manager.get_question_id_by_comment_question_or_answer(comment_id)
    if request.method == 'POST':
        message = request.form['message']
        data_manager.update_comment(comment_id, message)

        return redirect(f'/question/{question_id}')
    elif request.method == 'GET' and user_id == data_manager.get_user_id_by_comment_id(comment_id):
        comment = data_manager.get_comment_by_id(comment_id)

        return render_template('edit_comments.html', comment=comment, question_id=question_id)
    else:
        return redirect(f'/question/{question_id}')



@app.template_filter('highlight_search_phrase')
def highlight_search_phrase(value, search_phrase):
    if search_phrase.lower() not in value.lower():
        return value

    highlighted_value = value
    start_index = 0
    while True:
        start_index = highlighted_value.lower().find(search_phrase.lower(), start_index)
        if start_index == -1:
            break

        stop_index = start_index + len(search_phrase)
        original_substring = highlighted_value[start_index:stop_index]
        highlighted = f'<span style="background-color:#1e65ff;">{original_substring}</span>'
        highlighted_value = f'{highlighted_value[:start_index]}{highlighted}{highlighted_value[stop_index:]}'
        start_index += len(highlighted)

    return highlighted_value


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
@util.is_logged_in
def update_answers(answer_id):
    answer = data_manager.get_answer_by_id(answer_id)
    if request.method == 'GET':
        return render_template('edit_answer.html', answer=answer)
    elif request.method == "POST":
        image_file = request.files['image']
        if 'image' in request.files and image_file.filename != '':
            util.delete_image_files([answer['image']])
        message = request.form['message']
        data_manager.update_answer(message, answer_id)
        data_manager.update_image(answer_id, image_file)
        return redirect(f"/question/{answer['question_id']}")


@app.route('/question/<question_id>/tag/<tag_id>/delete')
@util.is_logged_in
def delete_tag(question_id, tag_id):
    data_manager.delete_tag(question_id, tag_id)
    return redirect(f'/question/{question_id}')


if __name__ == '__main__':
    app.run(port=5001)
