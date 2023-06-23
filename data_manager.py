import connection
import util


@connection.connection_handler
def get_sorted_questions(cursor, order_by, order_direction):
    order = 'ASC' if order_direction.upper() == 'ASC' else 'DESC'
    order_columns = ['submission_time', 'view_number', 'vote_number', 'number_of_answers', 'title', 'message']
    if order_by not in order_columns:
        raise Exception('SQL injection not possible:)')
    cursor.execute(f"""
                    SELECT *, (SELECT count(id) FROM answer a WHERE q.id = a.question_id)
                    AS number_of_answers
                    FROM question q
                    ORDER BY {order_by} {order};
                     """)
    return cursor.fetchall()


@connection.connection_handler
def get_question_data_by_id_dm(cursor, question_id):
    cursor.execute("""
                    SELECT *
                    FROM question
                    WHERE id = %(question_id)s;
                    """, {'question_id': question_id})
    return cursor.fetchone()


@connection.connection_handler
def view_question_dm(cursor, question_id):
    cursor.execute("""
                    UPDATE question 
                    SET view_number = view_number + 1
                    WHERE id = {};""".format(question_id))


@connection.connection_handler
def get_answers_by_question_id_dm(cursor, question_id):
    cursor.execute("""
                    SELECT *
                    FROM answer
                    WHERE question_id = %(question_id)s
                    ORDER BY submission_time DESC;
                    """, {'question_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def add_question_dm(cursor, title, message, image_file):
    submission_time = util.get_time()
    image_path = None
    if image_file.filename != '':
        image_path = util.save_image(image_file)
    cursor.execute("""
        INSERT INTO question(submission_time, view_number, vote_number, title, message, image)
        VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s)
        RETURNING id;""",
                   {'submission_time': submission_time,
                    'vote_number': 0,
                    'view_number': 0,
                    'title': title,
                    'message': message,
                    'image': image_path})
    new_question_id = cursor.fetchone()['id']
    return new_question_id


@connection.connection_handler
def add_answer_dm(cursor, message, question_id, image_file):
    submission_time = util.get_time()
    image_path = None
    if image_file.filename != '':
        image_path = util.save_image(image_file)
    cursor.execute("""
                    INSERT INTO answer(submission_time, vote_number, message, question_id, image)
                    VALUES (%(submission_time)s, %(vote_number)s, %(message)s, %(question_id)s, %(image)s);
                    """,
                   {'submission_time': submission_time,
                    'vote_number': 0,
                    'message': message,
                    'question_id': question_id,
                    'image': image_path})


@connection.connection_handler
def delete_question_dm(cursor, question_id):
    image_paths = get_image_paths(question_id)
    cursor.execute("""
                    DELETE FROM comment
                    WHERE answer_id IN
                    (SELECT answer_id
                    FROM answer
                    WHERE question_id = %(question_id)s);

                    DELETE FROM answer
                    WHERE question_id = %(question_id)s;

                    DELETE FROM comment
                    WHERE question_id = %(question_id)s;

                    DELETE FROM question_tag
                    WHERE question_id = %(question_id)s;

                    DELETE FROM question
                    WHERE id = %(question_id)s;
                    """,
                   {'question_id': question_id})
    util.delete_image_files(image_paths)


@connection.connection_handler
def get_image_paths(cursor, question_id):
    cursor.execute("""
                    SELECT image
                    FROM question
                    WHERE id = %(question_id)s
                    UNION ALL
                    SELECT image
                    FROM answer
                    WHERE question_id = %(question_id)s
                    """,
                   {'question_id': question_id})
    images = cursor.fetchall()
    image_paths = [image['image'] for image in images]
    return image_paths


@connection.connection_handler
def delete_answer_by_id(cursor, answer_id):
    cursor.execute("""
                    DELETE FROM comment
                    WHERE answer_id = %(answer_id)s;
            
                    DELETE FROM answer
                    WHERE id = %(answer_id)s
                    RETURNING image, question_id;
                    """,
                   {'answer_id': answer_id})
    data = cursor.fetchone()
    image_path = data['image']
    question_id = data['question_id']
    util.delete_image_files([image_path])
    return question_id


# TODO solution in connection, without changing time. additionally: add date of edition
@connection.connection_handler
def update_question_dm(cursor, title, message, old_image_path, new_image_file, question_id, remove_image):
    new_image_path = None
    if remove_image:
        util.delete_image_files([old_image_path])
    if new_image_file.filename != '':
        new_image_path = util.save_image(new_image_file)
    if remove_image and new_image_file.filename == '':
        new_image_path = old_image_path
    cursor.execute("""
                    UPDATE question 
                    SET 
                        title = %(title)s, 
                        message = %(message)s, 
                        image = %(image)s
                    WHERE id = %(question_id)s;
                    """,
                   {'title': title,
                    'message': message,
                    'image': new_image_path,
                    'question_id': question_id})


@connection.connection_handler
def vote_on_question_dm(cursor, question_id, vote_direction):
    cursor.execute("""
                    UPDATE question 
                    SET vote_number = CASE
                        WHEN %(vote_direction)s = 'up' THEN vote_number + 1
                        WHEN %(vote_direction)s = 'down' THEN vote_number - 1
                        ELSE vote_number
                    END
                    WHERE id = %(question_id)s;
                    """,
                   {'question_id': question_id,
                    'vote_direction': vote_direction})


@connection.connection_handler
def vote_on_answer_dm(cursor, answer_id, vote_direction):
    cursor.execute("""
                    UPDATE answer 
                    SET vote_number = CASE
                        WHEN %(vote_direction)s = 'up' THEN vote_number + 1
                        WHEN %(vote_direction)s = 'down' THEN vote_number - 1
                        ELSE vote_number
                    END
                    WHERE id = %(answer_id)s
                    RETURNING question_id;
                    """,
                   {'answer_id': answer_id, 'vote_direction': vote_direction})
    question_id = cursor.fetchone()['question_id']
    return question_id


@connection.connection_handler
def get_questions_by_search_phrase(cursor, search_phrase):
    search_pattern = f"%{search_phrase}%"
    cursor.execute("""
                    SELECT DISTINCT ON (q.id) q.id, q.submission_time, q.view_number, q.vote_number, q.title,
                    q.message, a.message AS answer_message, q.image
                    FROM question AS q
                    LEFT JOIN answer AS a ON q.id = a.question_id
                    WHERE q.title ILIKE %(search_pattern)s
                      OR q.message ILIKE %(search_pattern)s
                      OR a.message ILIKE %(search_pattern)s
                    ORDER BY q.id DESC, q.submission_time DESC;
                    """, {'search_pattern': search_pattern})
    rows = cursor.fetchall()
    questions = []
    for row in rows:
        question_id = row['id']
        if not any(q['id'] == question_id for q in questions):
            questions.append({
                'id': question_id,
                'submission_time': row['submission_time'],
                'view_number': row['view_number'],
                'vote_number': row['vote_number'],
                'title': row['title'],
                'message': row['message'],
                'answers': [],
                'image': row['image']
            })
        if row['answer_message']:
            questions[-1]['answers'].append(row['answer_message'])
    return questions


