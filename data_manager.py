import os
import uuid

import connection
import util

questions_csv = "data/question.csv"
answers_csv = "data/answer.csv"

HEADERS_Q = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
HEADERS_A = ["id", "submission_time", "vote_number", "question_id", "message", "image"]


def get_question_data_by_id_dm(question_id):
    data_questions = connection.read_dict_from_file(questions_csv)
    return next(data for data in data_questions if data['id'] == question_id)


def get_answers_by_question_id_dm(question_id):
    data_answers = connection.read_dict_from_file(answers_csv)
    for answer in data_answers:
        answer["submission_time"] = util.convert_timestamp_to_date(int(answer["submission_time"]))
    sorted_answers = sorted(data_answers, key=lambda x: x["submission_time"], reverse=True)
    return [line for line in sorted_answers if line['question_id'] == question_id]


def add_question_dm(title, message, image_path=None, question_id=None):
    questions = connection.read_dict_from_file(questions_csv)
    question_id = str(util.generated_id(questions_csv)) if question_id is None else question_id
    new_question = {
        'id': question_id,
        "submission_time": util.get_time(),
        "view_number": 0,
        "vote_number": 0,
        'title': title,
        'message': message,
        "image": image_path

    }
    questions.append(new_question)
    connection.write_dict_to_file_str(questions_csv, questions, HEADERS_Q)
    return question_id


def add_answer_dm(message, question_id, image_path=None):
    answers = connection.read_dict_from_file(answers_csv)
    new_answer_id = str(util.generated_id(answers_csv))
    new_answer = {
        'id': new_answer_id,
        "submission_time": util.get_time(),
        "vote_number": 0,
        "question_id": question_id,
        'message': message,
        "image": image_path
    }
    answers.append(new_answer)
    connection.write_dict_to_file_str(answers_csv, answers, HEADERS_A)


# TODO solution with filter + len (i have no idea..?)
def get_sorted_questions(order_by, order_direction):
    questions = connection.read_dict_from_file(questions_csv)
    answers = connection.read_dict_from_file(answers_csv)
    for question in questions:
        question["submission_time"] = util.convert_timestamp_to_date(int(question["submission_time"]))
        question['answers'] = 0
        for answer in answers:
            if question['id'] == answer['question_id']:
                question['answers'] += 1
    if order_by == 'title':
        questions.sort(key=lambda q: q['title'].lower(), reverse=(order_direction == 'desc'))
    elif order_by == 'submission_time':
        questions.sort(key=lambda q: q['submission_time'], reverse=(order_direction == 'desc'))
    elif order_by == 'message':
        questions.sort(key=lambda q: q['message'].lower(), reverse=(order_direction == 'desc'))
    elif order_by == 'view_number':
        questions.sort(key=lambda q: int(q['view_number']), reverse=(order_direction == 'desc'))
    elif order_by == 'vote_number':
        questions.sort(key=lambda q: int(q['vote_number']), reverse=(order_direction == 'desc'))
    elif order_by == 'answers':
        questions.sort(key=lambda q: int(q['answers']), reverse=(order_direction == 'desc'))
    return questions


def delete_answer_by_id(answer_id):
    delete_answer_dm(answer_id, 'id')


def delete_answer_by_question_id(question_id):
    delete_answer_dm(question_id, 'question_id')


def delete_answer_dm(data_id, header):
    answers = connection.read_dict_from_file(answers_csv)
    for answer in answers:
        file_path = answer['image']
        if answer.get(header) == data_id:
            util.delete_image_file(file_path)
            answers.remove(answer)
    connection.write_dict_to_file_str(answers_csv, answers, HEADERS_A)


def delete_image(question_id):
    questions = connection.read_dict_from_file(questions_csv)
    for question in questions:
        if question.get('id') == question_id:
            file_path = question['image']
            saved_data = question
            saved_data['image'] = None
            util.delete_image_file(file_path)
            questions.remove(question)
            questions.append(saved_data)
            break
    connection.write_dict_to_file_str(questions_csv, questions, HEADERS_Q)


def delete_question_dm(question_id, delete_image_file=None):
    questions = connection.read_dict_from_file(questions_csv)
    for question in questions:
        if question.get('id') == question_id:
            file_path = question['image']
            if delete_image_file:
                util.delete_image_file(file_path)
            questions.remove(question)
    connection.write_dict_to_file_str(questions_csv, questions, HEADERS_Q)


def get_question_id(answer_id):
    answers = connection.read_dict_from_file(answers_csv)
    for answer in answers:
        if answer['id'] == answer_id:
            return answer['question_id']


# TODO solution in connection, without changing time. additionally: add date of edition
def update_question_dm(title, message, image_path, question_id, delete_image_file):
    delete_question_dm(question_id, delete_image_file)
    add_question_dm(title, message, image_path, question_id)


def vote_on_question_dm(question_id, vote):
    vote_on_dm(question_id, questions_csv, vote, HEADERS_Q)


def vote_on_answer_dm(answer_id, vote):
    vote_on_dm(answer_id, answers_csv, vote, HEADERS_A)


def vote_on_dm(data_id, file_csv, vote, headers):
    data_list = connection.read_dict_from_file(file_csv)
    for data in data_list:
        if data['id'] == data_id:
            number_of_votes = int(data["vote_number"])
            if vote == "up":
                number_of_votes += 1
            elif vote == "down":
                number_of_votes -= 1
            data["vote_number"] = number_of_votes
    connection.write_dict_to_file_str(file_csv, data_list, headers)


def view_question_dm(question_id):
    questions = connection.read_dict_from_file(questions_csv)
    for question in questions:
        if question['id'] == question_id:
            number_of_views = int(question["view_number"])
            number_of_views += 1
            question["view_number"] = number_of_views

    connection.write_dict_to_file_str(questions_csv, questions, HEADERS_Q)


def save_image_dm(image_file):
    unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
    image_path = 'static/uploads/' + unique_filename
    image_file.save(image_path)
    return image_path
