import connection
import util
import uuid
import os


@connection.connection_handler
def list_questions_(cursor):
    query = """
     SELECT *
     FROM question"""
    cursor.execute(query)
    return cursor.fetchall()

@connection.connection_handler
def get_question_data_by_id_dm(cursor,question_id):
    query = """
     SELECT *
     FROM question
     WHERE id= %(question_id)s;"""
    cursor.execute(query,{"question_id":question_id})
    return cursor.fetchone()


@connection.connection_handler
def get_answers_by_question_id_dm(cursor,question_id):
    query = """
     SELECT *
     FROM answer
     WHERE question_id= %(question_id)s;
     ORDER BY submission_time"""
    cursor.execute(query,{"question_id":question_id})
    return cursor.fetchall()



# def add_question_dm(cursor, title, message, image_path):
#     question_id = str(util.generated_id(cursor, "question"))
#     time = util.get_time()
#     query = """
#         INSERT INTO question
#         VALUES (%s, %s, 0, 0, %s, %s, %s);"""
#     cursor.execute(query, (question_id, time, title, message, image_path))
#     return question_id

@connection.connection_handler
def add_question_dm(cursor, data_q):
    cursor.execute("""
                    INSERT INTO question(submission_time, view_number, vote_number, title, message, image)
                    VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s);
                    """,
                   {'submission_time': util.get_time(),
                    'view_number': 0,
                    'vote_number': 0,
                    'title': data_q['title'],
                    'message': data_q['message'],
                    'image': data_q['image']})
    # new_question_id = cursor.fetchone()['id']
    # return new_question_id


@connection.connection_handler
def get_newest_question_dm(cursor):
    query = """
        SELECT MAX(id) AS max_id
        FROM question
        """
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        return result['max_id']
    return None

# @connection.connection_handler
# def add_answer_dm(cursor, message, question_id, image_path=None):
#     answer_id = str(util.generated_id(cursor, 'public.answers'))
#     time = util.get_time()
#     query = """
#         INSERT INTO question
#         VALUES (%s, %s, 0, 0, %s, %s, %s);"""
#     cursor.execute(query, (question_id, time, title, message, image_path))
#     return question_id


# def add_answer_dm(message, question_id, image_path=None):
#     answers = connection.read_dict_from_file(answers_csv)
#     new_answer_id = str(util.generated_id(answers_csv))
#     new_answer = {
#         'id': new_answer_id,
#         "submission_time": util.get_time(),
#         "vote_number": 0,
#         "question_id": question_id,
#         'message': message,
#         "image": image_path
#     }
#     answers.append(new_answer)
#     connection.write_dict_to_file_str(answers_csv, answers, HEADERS_A)

# @connection.connection_handler
# def sorted_questions_(cursor):
#     query = """
#      SELECT submission_time, view_number, vote_number, title, mesage
#      FROM question
#      ORDER BY submission_time, view_number, vote_number, title, mesage ASC|DESC"""
#     cursor.execute(query)
#     return cursor.fetchall()


# def get_sorted_questions(order_by, order_direction):
#     questions = get_question_data_by_id_dm(cursor,question_id)
#     answers = get_answers_by_question_id_dm(cursor,question_id)


    # for question in questions:
    #     question["submission_time"] = util.convert_timestamp_to_date(int(question["submission_time"]))
    #     question['answers'] = 0
    #     for answer in answers:
    #         if question['id'] == answer['question_id']:
    #             question['answers'] += 1
    # if order_by == 'title':
    #     questions.sort(key=lambda q: q['title'].lower(), reverse=(order_direction == 'desc'))
    # elif order_by == 'submission_time':
    #     questions.sort(key=lambda q: q['submission_time'], reverse=(order_direction == 'desc'))
    # elif order_by == 'message':
    #     questions.sort(key=lambda q: q['message'].lower(), reverse=(order_direction == 'desc'))
    # elif order_by == 'view_number':
    #     questions.sort(key=lambda q: int(q['view_number']), reverse=(order_direction == 'desc'))
    # elif order_by == 'vote_number':
    #     questions.sort(key=lambda q: int(q['vote_number']), reverse=(order_direction == 'desc'))
    # elif order_by == 'answers':
    #     questions.sort(key=lambda q: int(q['answers']), reverse=(order_direction == 'desc'))
    # return questions

#
# def delete_answer_by_id(answer_id):
#     delete_answer_dm(answer_id, 'id')
#
#
# def delete_answer_by_question_id(question_id):
#     delete_answer_dm(question_id, 'question_id')
#
#
# def delete_answer_dm(data_id, header):
#     answers = connection.read_dict_from_file(answers_csv)
#     for answer in answers:
#         file_path = answer['image']
#         if answer.get(header) == data_id:
#             util.delete_image_file(file_path)
#             answers.remove(answer)
#     connection.write_dict_to_file_str(answers_csv, answers, HEADERS_A)

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


# def get_question_id(answer_id):
#     answers = connection.read_dict_from_file(answers_csv)
#     for answer in answers:
#         if answer['id'] == answer_id:
#             return answer['question_id']


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

#
# def save_image_dm(image_file):
#     unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
#     image_path = 'static/uploads/' + unique_filename
#     image_file.save(image_path)
#     return image_path

# @connection.connection_handler
# def view_question_dm(cursor, question_id):
#     query = """
#         UPDATE question
#         SET view_number = view_number + 1
#         WHERE id = %s;"""
#     cursor.execute(query, question_id)
#     return question_id

def save_image_dm(image_file):
    unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
    image_path = 'static/uploads/' + unique_filename
    image_file.save(image_path)
    return image_path