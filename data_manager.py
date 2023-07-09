import connection
import util


@connection.connection_handler
def add_user(cursor, username, email, hashed_password):
    registration_date = util.get_time()
    cursor.execute("""
                    INSERT INTO users(username, email, password, registration_date) 
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;""",
                   (username, email, hashed_password, registration_date))
    return cursor.fetchone()["id"]


@connection.connection_handler
def get_user_by_name(cursor, username, email):
    cursor.execute("""
                SELECT * 
                FROM users
                WHERE username = %s  OR email = %s    
                """, (username, email))
    return cursor.fetchone()


@connection.connection_handler
def get_users_list(cursor):
    cursor.execute("""
                    SELECT username, registration_date, reputation,
                    (SELECT COUNT(id) FROM question q WHERE u.id = q.user_id) AS questions_number,
                    (SELECT COUNT(id) FROM answer a WHERE u.id =a.user_id) AS answers_number,
                    (SELECT COUNT(id) FROM comment c WHERE u.id = c.user_id) AS comments_number
                    FROM users u;
                    """)
    return cursor.fetchall()


@connection.connection_handler
def get_user_id(cursor, username, email):
    cursor.execute("""
                   SELECT id
                   FROM users
                   WHERE username = %s  OR email = %s 
                   """, (username, email))
    return cursor.fetchone()


@connection.connection_handler
def get_sorted_questions(cursor, order_by, order_direction, questions=None):
    if questions is None:
        order = 'ASC' if order_direction.upper() == 'ASC' else 'DESC'
        order_columns = ['submission_time', 'view_number', 'vote_number', 'number_of_answers', 'title', 'message']
        if order_by not in order_columns:
            raise Exception('Wrong order by query.')
        cursor.execute(f"""
                        SELECT *,
                        (SELECT COUNT(id) FROM answer a WHERE q.id = a.question_id) AS number_of_answers
                        FROM question q
                        ORDER BY {order_by} {order};
                        """)
        return cursor.fetchall()
    else:
        order_by_column = {
            'submission_time': 'submission_time',
            'view_number': 'view_number',
            'vote_number': 'vote_number',
            'title': 'title',
            'message': 'message'
        }
        order_by = order_by_column.get(order_by)
        if order_by is None:
            raise Exception('Wrong order by query.')
        questions.sort(key=lambda q: q[order_by], reverse=(order_direction.upper() == 'DESC'))
        return questions


@connection.connection_handler
def get_question_data_by_id(cursor, question_id):
    cursor.execute("""
                    SELECT *
                    FROM question
                    WHERE id = %(question_id)s;
                    """, {'question_id': question_id})
    return cursor.fetchone()


@connection.connection_handler
def view_question(cursor, question_id):
    cursor.execute("""
                    UPDATE question 
                    SET view_number = view_number + 1
                    WHERE id = %(question_id)s;
                    """, {'question_id': question_id})


@connection.connection_handler
def get_answers_by_question_id(cursor, question_id):
    cursor.execute("""
                    SELECT *
                    FROM answer
                    WHERE question_id = %(question_id)s
                    ORDER BY submission_time DESC;
                    """, {'question_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def add_question(cursor, title, message, image_path, user_id):
    submission_time = util.get_time()
    cursor.execute("""
                    INSERT INTO question(submission_time, view_number, vote_number, title, message, user_id)
                    VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(user_id)s)
                    RETURNING id;""",
                   {'submission_time': submission_time,
                    'vote_number': 0,
                    'view_number': 0,
                    'title': title,
                    'message': message,
                    'user_id': user_id})
    new_question_id = cursor.fetchone()['id']
    update_image_in_question(new_question_id, image_path)
    return new_question_id


@connection.connection_handler
def add_answer(cursor, message, question_id, image_path, user_id):
    submission_time = util.get_time()
    cursor.execute("""
                    INSERT INTO answer(submission_time, vote_number, message, question_id, image, user_id)
                    VALUES (%(submission_time)s, %(vote_number)s, %(message)s, %(question_id)s, %(image)s, %(user_id)s);
                    """,
                   {'submission_time': submission_time,
                    'vote_number': 0,
                    'message': message,
                    'question_id': question_id,
                    'image': image_path,
                    'user_id': user_id})


@connection.connection_handler
def delete_question(cursor, question_id):
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
                    """, {'question_id': question_id})
    return image_paths


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
                    """, {'question_id': question_id})
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
    return question_id, image_path


@connection.connection_handler
def update_question(cursor, title, message, question_id, remove_image, new_image_path=None):
    if remove_image or new_image_path is not None:
        delete_image_from_question(question_id)
    if new_image_path is not None:
        update_image_in_question(question_id, new_image_path)
    cursor.execute("""
                    UPDATE question 
                    SET 
                        title = %(title)s, 
                        message = %(message)s
                    WHERE id = %(question_id)s;""",
                   {'title': title,
                    'message': message,
                    'question_id': question_id})


@connection.connection_handler
def update_image_in_question(cursor, question_id, image_path):
    cursor.execute("""
                    UPDATE question 
                    SET image = %(image)s
                    WHERE id = %(question_id)s;""",
                   {'image': image_path,
                    'question_id': question_id})


@connection.connection_handler
def vote_on_question(cursor, question_id, vote_direction):
    cursor.execute("""
                    UPDATE question 
                    SET vote_number = CASE
                        WHEN %(vote_direction)s = 'up' THEN vote_number + 1
                        WHEN %(vote_direction)s = 'down' THEN vote_number - 1
                        ELSE vote_number
                    END
                    WHERE id = %(question_id)s;""",
                   {'question_id': question_id,
                    'vote_direction': vote_direction})


@connection.connection_handler
def vote_on_answer(cursor, answer_id, vote_direction):
    cursor.execute("""
                    UPDATE answer 
                    SET vote_number = CASE
                        WHEN %(vote_direction)s = 'up' THEN vote_number + 1
                        WHEN %(vote_direction)s = 'down' THEN vote_number - 1
                        ELSE vote_number
                    END
                    WHERE id = %(answer_id)s;
                    """, {'answer_id': answer_id,
                          'vote_direction': vote_direction})


@connection.connection_handler
def change_reputation(cursor, number, user_id):
    cursor.execute("""
            UPDATE users
            SET reputation = reputation + %(number)s
            WHERE id = %(user_id)s
            """, {'number': number, 'user_id': user_id})


@connection.connection_handler
def get_comments_by_question_id(cursor, question_id):
    cursor.execute("""
                    SELECT *
                    FROM comment
                    WHERE question_id = %(question_id)s
                    ORDER BY submission_time DESC;
                    """, {'question_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def add_comment_question(cursor, question_id, message, user_id):
    submission_time = util.get_time()
    cursor.execute("""
                    INSERT INTO comment(question_id, message,submission_time, user_id)
                    VALUES (%(question_id)s, %(message)s, %(submission_time)s, %(user_id)s);
                    """, {'question_id': question_id,
                          'message': message,
                          'submission_time': submission_time,
                          'user_id': user_id})


@connection.connection_handler
def get_comments_of_answers(cursor, question_id):
    cursor.execute("""
                    SELECT c.id, c.answer_id, c.message, c.submission_time, edited_count
                    FROM comment c
                    JOIN answer a on c.answer_id = a.id
                    WHERE a.question_id = %(question_id)s
                    ORDER BY submission_time DESC
                    """, {'question_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def add_comment_to_answer(cursor, answer_id, message, user_id):
    submission_time = util.get_time()
    cursor.execute("""
                    INSERT INTO comment(answer_id, message, submission_time, user_id)
                    VALUES (%(answer_id)s, %(message)s, %(submission_time)s, %(user_id)s);
                    
                    SELECT question_id
                    FROM answer
                    WHERE id = %(answer_id)s;
                    """, {'answer_id': answer_id,
                          'message': message,
                          'submission_time': submission_time,
                          'user_id': user_id})
    question_id = cursor.fetchone()['question_id']
    return question_id


@connection.connection_handler
def delete_comment(cursor, comment_id):
    cursor.execute("""
                    DELETE FROM comment
                    WHERE id = %(comment_id)s
                    RETURNING question_id;                                    
                    """, {'comment_id': comment_id})
    question_id = cursor.fetchone()["question_id"]
    return question_id


@connection.connection_handler
def get_tags(cursor):
    cursor.execute("""
                    SELECT t.name, COUNT(q.question_id) AS number_of_questions
                    FROM tag t
                    LEFT JOIN question_tag q on t.id = q.tag_id
                    GROUP BY t.id, t.name;
                    """)
    tags = cursor.fetchall()
    return tags


@connection.connection_handler
def get_tags_by_question_id(cursor, question_id):
    cursor.execute("""
                    SELECT t.id, t.name
                    FROM tag t
                    JOIN question_tag q on q.tag_id = t.id
                    WHERE q.question_id = %(question_id)s;
                    """,
                   {'question_id': question_id})
    tags = cursor.fetchall()
    return tags


@connection.connection_handler
def get_question_id_by_answer_id(cursor, answer_id):
    cursor.execute("""
                    SELECT question_id
                    FROM answer
                    WHERE id = %(answer_id)s;
                    """,
                   {'answer_id': answer_id})
    question_id = cursor.fetchone()['question_id']
    return question_id


@connection.connection_handler
def add_tags(cursor, question_id, tags):
    for tag in tags:
        cursor.execute("""
                        INSERT INTO tag (name)
                        SELECT %(tag)s
                        WHERE NOT EXISTS
                            (SELECT 1
                             FROM tag
                             WHERE name = %(tag)s);

                        INSERT INTO question_tag (question_id, tag_id)
                        SELECT %(question_id)s, t.id
                        FROM tag t
                        WHERE t.name = %(tag)s
                        AND NOT EXISTS
                            (SELECT 1
                             FROM question_tag
                             WHERE question_id = %(question_id)s AND tag_id = t.id);
                        """,
                       {'question_id': question_id, 'tag': tag})


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
                    """,
                   {'search_pattern': search_pattern})
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


@connection.connection_handler
def delete_image_from_answer(cursor, answer_id):
    cursor.execute("""
                    SELECT image
                    FROM answer
                    WHERE id = %(answer_id)s;
                    """, {'answer_id': answer_id})
    image_path = cursor.fetchone()['image']
    cursor.execute("""
                    UPDATE answer
                    SET image = Null
                    WHERE id = %(answer_id)s
                    RETURNING question_id;
                        """, {'answer_id': answer_id})
    question_id = cursor.fetchone()['question_id']
    return question_id, image_path


@connection.connection_handler
def delete_image_from_question(cursor, question_id):
    cursor.execute("""
                    SELECT image
                    FROM question
                    WHERE id = %(question_id)s;
                    """, {'question_id': question_id})
    image_path = cursor.fetchone()['image']
    cursor.execute("""
                    UPDATE question
                    SET image = Null
                    WHERE id = %(question_id)s;
                        """, {'question_id': question_id})
    return image_path


@connection.connection_handler
def get_comment_by_id(cursor, comment_id):
    cursor.execute("""
                    SELECT *
                    FROM comment c
                    WHERE id = %(comment_id)s
                    """, {'comment_id': comment_id})
    comment = cursor.fetchone()
    return comment


@connection.connection_handler
def get_question_id_by_comment_question_or_answer(cursor, comment_id):
    cursor.execute("""
                    SELECT MAX(question_id) AS question_id
                    FROM
                    (SELECT c.question_id
                    FROM comment c
                    WHERE id = %(comment_id)s
                    UNION DISTINCT
                    SELECT a.question_id
                    FROM comment c
                    JOIN answer a ON a.id = c.answer_id
                    WHERE c.id = %(comment_id)s
                    )subquery;             
                    """, {'comment_id': comment_id})
    question_id = cursor.fetchone()["question_id"]
    return question_id


@connection.connection_handler
def update_comment(cursor, comment_id, message):
    submission_time = util.get_time()
    cursor.execute("""
                    UPDATE comment
                    SET 
                    message = %(message)s, 
                    submission_time = %(submission_time)s, 
                    edited_count = COALESCE(edited_count, 0) + 1
                    WHERE id = %(comment_id)s
                    """, {'comment_id': comment_id,
                          "message": message,
                          'submission_time': submission_time})


@connection.connection_handler
def update_answer(cursor, message, answer_id):
    cursor.execute("""
        UPDATE answer
        SET
            message = %(message)s
        WHERE id = %(answer_id)s;""",
                   {'message': message,
                    'answer_id': answer_id})


@connection.connection_handler
def update_image(cursor, answer_id, image_file):
    if image_file.filename != '':
        image_path = util.save_image(image_file)
        cursor.execute("""
            UPDATE answer
            SET
                image = %(image_path)s
            WHERE id = %(answer_id)s;""",
                       {'image_path': image_path,
                        'answer_id': answer_id})


@connection.connection_handler
def get_answer_by_id(cursor, answer_id):
    cursor.execute("""
                    SELECT *
                    FROM answer
                    WHERE id = %(answer_id)s;
                    """, {'answer_id': answer_id})
    return cursor.fetchone()


@connection.connection_handler
def delete_tag(cursor, question_id, tag_id):
    cursor.execute("""
            DELETE FROM question_tag
            WHERE question_id = %(question_id)s 
            AND tag_id = %(tag_id)s;
            
            DELETE FROM tag
            WHERE id = %(tag_id)s
            AND NOT EXISTS(
                SELECT 1
                FROM question_tag
                WHERE tag_id = %(tag_id)s);
                    """, {'question_id': question_id, 'tag_id': tag_id})
