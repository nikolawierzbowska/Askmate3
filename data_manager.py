import connection
import util

@connection.connection_handler
def get_sorted_questions(cursor, order_by, order_direction):
    order = "ASC" if order_direction.upper() == "ASC" else "DESC"
    order_columns = ['submission_time', 'view_number', 'vote_number',
                     'number_of_answers', 'title', 'message']
    if order_by not in order_columns:
        raise Exception('Wrong order by query.')
    cursor.execute(f"""
                    SELECT *,
                    (SELECT COUNT(id) FROM answer a WHERE q.id = a.question_id) AS number_of_answers
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
                    WHERE id = %(question_id)s;
                    """, {'question_id': question_id})


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
                    RETURNING id;""", {'submission_time': submission_time,
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
                    """, {'submission_time': submission_time,
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
                    """, {'question_id': question_id})
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
                    """, {'answer_id': answer_id})
    data = cursor.fetchone()
    image_path = data['image']
    question_id = data['question_id']
    util.delete_image_files([image_path])
    return question_id


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
                    """, {'title': title,
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
                    """, {'question_id': question_id,
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
                    """, {'answer_id': answer_id,
                         'vote_direction': vote_direction})
    question_id = cursor.fetchone()['question_id']
    return question_id


@connection.connection_handler
def get_comments_by_question_id_dm(cursor, question_id):
    cursor.execute("""
                    SELECT *
                    FROM comment
                    WHERE question_id = %(question_id)s
                    ORDER BY submission_time DESC;
                    """, {'question_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def add_comment_question(cursor,question_id, message):
    submission_time = util.get_time()
    cursor.execute("""
                    INSERT INTO comment(question_id, message,submission_time, edited_count)
                    VALUES (%(question_id)s, %(message)s, %(submission_time)s, %(edited_count)s);
                    """,{'question_id':question_id,
                         'message': message,
                         'submission_time': submission_time,
                         'edited_count':0})


@connection.connection_handler
def edit_comment_dm(cursor,question_id, message):
    pass

@connection.connection_handler
def get_comments_to_answers_dm(cursor, question_id):
    cursor.execute("""
                    SELECT c.id, c.answer_id, c.message, c.submission_time, edited_count
                    FROM comment c
                    JOIN answer a on c.answer_id = a.id
                    WHERE a.question_id = %(question_id)s
                    ORDER BY submission_time DESC
                    """, {'question_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def add_comment_to_answer_dm(cursor, answer_id, message):
    submission_time = util.get_time()
    cursor.execute("""
                    INSERT INTO comment(answer_id, message, submission_time, edited_count)
                    VALUES (%(answer_id)s, %(message)s, %(submission_time)s, %(edited_count)s);

                    SELECT question_id
                    FROM answer
                    WHERE id = %(answer_id)s;
                    """, {'answer_id': answer_id,
                          'message': message,
                          'submission_time': submission_time,
                          'edited_count': 0})
    question_id = cursor.fetchone()['question_id']
    return question_id


@connection.connection_handler
def delete_comment_dm(cursor,comment_id):
    cursor.execute("""
                    DELETE FROM comment
                    WHERE id = %(comment_id)s
                    RETURNING question_id;                                    
                    """,{'comment_id':comment_id})

    question_id = cursor.fetchone()["question_id"]
    return question_id

@connection.connection_handler
def get_question_id_to_comment(cursor, comment_id):
    cursor.execute("""
                    SELECT a.question_id
                    FROM comment c
                    JOIN answer a ON a.id = c.answer_id
                    WHERE c.id = %(comment_id)s;                 
                    """, {'comment_id':comment_id})
    return cursor.fetchone()['question_id']

# @connection.connection_handler
# def get_tags_by_question_id(cursor, question_id):
#     cursor.execute("""
#                     SELECT t.id, t.name
#                     FROM tag t
#                     JOIN question_tag q on q.tag_id = t.id
#                     WHERE q.question_id = %(question_id)s;
#                     """, {'question_id': question_id})
#     tags = cursor.fetchall()
#     return tags
#
# @connection.connection_handler
# def add_tags_to_question_dm(cursor, question_id, tags):
#         cursor.execute("""
#         INSERT INTO tag (name)
#         SELECT DISTINCT tag_name
#         FROM (VALUES ('tag1'), ('tag2'), ('tag3')) AS tags(tag_name)
#         WHERE tag_name NOT IN (
#             SELECT name
#             FROM tag);
#             """, {'question_id': question_id,
#                   'tag':tag})
#     tags = cursor.fetchall()
#     return tags

