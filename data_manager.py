import connection
import util


@connection.connection_handler  #nie jest to dokładna wersja z zajęć, jak próbowałam to przerobić z f stringa to cos sie posypało, i zrobiłam na siłe, nie wiem czy tak może być???
def get_sorted_questions(cursor, order_by, order_direction):
    query = """
        SELECT *,
        (SELECT COUNT(id) FROM answer a WHERE q.id = a.question_id) AS number_of_answers
        FROM question q
        ORDER BY {} {};
    """.format(order_by, order_direction)
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_question_data_by_id_dm(cursor, question_id):
    cursor.execute("""
        SELECT *
        FROM question
        WHERE id = %s;""",
             (question_id))
    return cursor.fetchone()


@connection.connection_handler
def get_answers_by_question_id_dm(cursor, question_id):
    cursor.execute("""
        SELECT *
        FROM answer
        WHERE question_id = %s
        ORDER BY submission_time DESC;""",
                   (question_id))
    return cursor.fetchall()


@connection.connection_handler
def add_question_dm(cursor, submission_time, title, message, image_path):
    cursor.execute("""
        INSERT INTO question(submission_time, view_number, vote_number, title, message, image)
        VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s)
        RETURNING id;""",
                   {'submission_time': submission_time,
                    'vote_number': 0,
                    'view_number': 0,
                    'title' : title,
                    'message': message,
                    'image': image_path})
    new_question_id = cursor.fetchone()['id']
    return new_question_id


@connection.connection_handler
def add_answer_dm(cursor, submission_time, message, question_id, image_path):
    cursor.execute("""
        INSERT INTO answer(submission_time, vote_number, message, question_id, image)
        VALUES (%(submission_time)s, %(vote_number)s, %(message)s, %(question_id)s %(image)s);
        """,
       {'submission_time': submission_time,
        'vote_number': 0,
        'message': message,
        'question_id': question_id,
        'image': image_path})


# @connection.connection_handler
# def delete_question(cursor, question_id):
#     # usuwa obrazek do Q
#     delete_question_image_file(question_id)
#     # pobiera A do Q i usuwa zdjęcia
#     answers = get_answers_by_question_id_dm(question_id)
#     for
#     cursor.execute(f"""
#             DELETE FROM question
#             WHERE question_id = {question_id};""")


def delete_question_image_file(cursor, question_id):
    cursor.execute(f"""
        SELECT image
        FROM question
        WHERE id = {question_id};""")
    result = cursor.fetchone()
    if result is not None:
        image_path = result['image']
        util.delete_image_file(image_path)


@connection.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute(f"""
        SELECT image 
        FROM answer
        WHERE id = {answer_id};""")
    image_paths = cursor.fetchall()
    for image_path in image_paths:
        util.delete_image_file(image_path)


@connection.connection_handler
def delete_answer_from_data_base(cursor, answer_id):
    cursor.execute(f"""
        DELETE FROM answer
        WHERE id = {answer_id};""")


@connection.connection_handler
def delete_answer_by_question_id(cursor, question_id):
    cursor.execute(f"""
        DELETE FROM answer
        WHERE question_id = {question_id};""")


# def delete_answer_dm(data_id, header):
#     answers = connection.read_dict_from_file(answers_csv)
#     for answer in answers:
#         file_path = answer['image']
#         if answer.get(header) == data_id:
#             util.delete_image_file(file_path)
#             answers.remove(answer)
#     connection.write_dict_to_file_str(answers_csv, answers, HEADERS_A)
#
#
# def delete_image(question_id):
#     questions = connection.read_dict_from_file(questions_csv)
#     for question in questions:
#         if question.get('id') == question_id:
#             file_path = question['image']
#             saved_data = question
#             saved_data['image'] = None
#             util.delete_image_file(file_path)
#             questions.remove(question)
#             questions.append(saved_data)
#             break
#     connection.write_dict_to_file_str(questions_csv, questions, HEADERS_Q)
#
#
# def delete_question_dm(question_id, delete_image_file=None):
#     questions = connection.read_dict_from_file(questions_csv)
#     for question in questions:
#         if question.get('id') == question_id:
#             file_path = question['image']
#             if delete_image_file:
#                 util.delete_image_file(file_path)
#             questions.remove(question)
#     connection.write_dict_to_file_str(questions_csv, questions, HEADERS_Q)

@connection.connection_handler
def get_question_id_by_answer(answer_id):
    cursor.execute("""
        SELECT question_id 
        FROM answer
        WHERE id = %(answer_id)s;""",
                   (answer_id))
    return cursor.fetchone()["question_id"]


# # TODO solution in connection, without changing time. additionally: add date of edition
# def update_question_dm(title, message, image_path, question_id, delete_image_file):
#     delete_question_dm(question_id, delete_image_file)
#     add_question_dm(title, message, image_path, question_id)
#
#
# def vote_on_question_dm(question_id, vote):
#     vote_on_dm(question_id, questions_csv, vote, HEADERS_Q)
#
#
# def vote_on_answer_dm(answer_id, vote):
#     vote_on_dm(answer_id, answers_csv, vote, HEADERS_A)
#
#
# def vote_on_dm(data_id, file_csv, vote, headers):
#     data_list = connection.read_dict_from_file(file_csv)
#     for data in data_list:
#         if data['id'] == data_id:
#             number_of_votes = int(data["vote_number"])
#             if vote == "up":
#                 number_of_votes += 1
#             elif vote == "down":
#                 number_of_votes -= 1
#             data["vote_number"] = number_of_votes
#     connection.write_dict_to_file_str(file_csv, data_list, headers)

@connection.connection_handler
def view_question_dm(cursor, question_id):
    cursor.execute("""
        UPDATE question 
        SET view_number = view_number + 1
        WHERE id = %(question_id)s;""",
                   (question_id))

