# AskMate (sprint 1)

## Story

It is time to put your newly acquired Flask skills to use.
Your next big task is to implement a crowdsourced Q&A site, similar to Stack Overflow.

The initial version of the site must be able to handle questions and answers.
There is no need for additional functionality, such as user management or comments for questions and answers.

The management is very interested in the agile development methodologies that they recently heard about, so they are handing out a **prioritized list** of user stories, called a product backlog. Try to estimate how many of these stories your team can finish until the demo. As the order is important, choose from the beginning of the list as much as you can. **The first four stories are the most important**.

## What are you going to learn?

- Create a Flask project.
- Use routes with Flask.
- Use HTML and the Jinja templating engine.
- CSV handling.

## Tasks

1. Implement the `/list` page that displays all questions.
    - The page is available under `/list`.
    - The data is loaded and displayed from `question.csv`.
    - The questions are sorted by most recent.

2. Create the `/question/<question_id>` page that displays a question and the answers for it.
    - The page is available under `/question/<question_id>`.
    - There are links to the question pages from the list page.
    - The page displays the question title and message.
    - The page displays all answers to a question.

3. Implement a form that allows the user to add a question.
    - There is an `/add-question` page with a form.
    - The page is linked from the list page.
    - There is a POST form with at least `title` and `message` fields.
    - After submitting, the page redirects to "Display a question" page of this new question.

4. Implement posting a new answer.
    - The page URL is `/question/<question_id>/new-answer`.
    - The question detail page links to the page.
    - The page has a POST form with a form field called `message`.
    - Posting an answer redirects to the question detail page. The new answer is displayed on the question detail page.

5. Implement sorting for the question list.
    - The question list can be sorted by title, submission time, message, number of views, and number of votes.
    - The question list can be put in ascending and descending order.
    - The order is passed as query string parameters, such as `/list?order_by=title&order_direction=desc`.

6. Implement deleting a question.
    - Deleting is implemented by the `/question/<question_id>/delete` endpoint.
    - There is a deletion link on the question page.
    - Deleting redirects to the list of questions.

7. Allow the user to upload an image for a question or answer.
    - The forms for adding question and answer contain an "image" file field.
    - The user can attach an image (.jpg, .png).
    - The image is saved on server and displayed next to the question or the answer.
    - When deleting the question or answer, the image file is also deleted.

8. Implement editing an existing question.
    - There is a `/question/<question_id>/edit` page.
    - The page is linked from the question page.
    - There is a POST form with at least `title` and `message` fields.
    - The fields are pre-filled with existing question data.
    - After submitting, the page redirects to the "Display a question" page. The changed data is visible on the "Display a question" page.

9. Implement deleting an answer.
    - Deleting is implemented by `/answer/<answer_id>/delete` endpoint.
    - There is a deletion link on the question page, next to an answer.
    - Deleting redirects to the question detail page.

10. Implement voting on questions.
    - Vote numbers are displayed next to questions on the question list page.
    - There are "vote up/down" links next to questions on the question list page.
    - Voting uses `/question/<question_id>/vote_up` and `/question/<question_id>/vote_down` endpoints.
    - Voting up increases, voting down decreases the `vote_number` of the question by one.
    - Voting redirects to the question list.

11. Implement voting on answers.
    - Vote numbers are displayed next to answers on the question detail page.
    - There are "vote up/down" links next to answers.
    - Voting uses `/answer/<answer_id>/vote_up` and `/answer/<answer_id>/vote_down` endpoints.
    - Voting up increases, voting down decreases the `vote_number` of the answer by one.
    - Voting redirects to the question detail page.

## General requirements

- All data is persisted to `.csv` files. You need a `questions.csv` for storing all questions and an `answers.csv` for storing all answers.

## Hints

 ### Project structure

- Split the code into modules according to clean code principles.
- Do not put more than 100-150 lines of code into a single file.
- Make sure that files logically contain the same things. For example,
you can split the code into the following 3+1 parts.

**Layer** | **Example filename** | **What should it do/contain?**
---|---|---
Routing layer | `server.py` | This layer contains logic related to Flask, such as server, routes, request handling, session, and so on. This is the only file to be imported from Flask.
Persistence layer | `data_manager.py` | This is the layer between the server and the data. Functions here are called from `server.py` and use generic functions from `connection.py`.
CSV _(later SQL)_ connection layer |  `connection.py` | This layer contains common functions to read, write, or append CSV files without feature-specific knowledge. Only this layer can access long term data storage. In this case, CSV files are used as storage, later this will switch to SQL databases.
- Utility "layer" | `util.py` | Helper functions that can be called from any other layer, but mainly from the business logic layer.

This is just one way to structure code, you do not have to follow it _strictly_.

### Data models

In the `sample_data` folder, there are two sample files for questions and answers.

The content of the files is the following (you can ignore data in the unimplemented fields).

**question.csv**<br>
*id:* A unique identifier for the question.<br>
*submission_time:* The UNIX timestamp when the question is posted.<br>
*view_number:* The number of times this question is displayed in the single question view.<br>
*vote_number:* The sum of votes this question receives.<br>
*title:* The title of the question.<br>
*message:* The question text.<br>
*image:* The path to the image for this question.<br>

**answer.csv**<br>
*id:* A unique identifier for the answer.<br>
*submission_time:* The UNIX timestamp when the answer is posted.<br>
*vote_number:* The sum of votes the answer receives.<br>
*question_id:* The ID of the question to which this answer belongs.<br>
*message:* The answer text.<br>
*image:* The path to the image for this answer.<br>

## Background materials

- <i class="far fa-exclamation"></i> [Understanding the web](project/curriculum/materials/pages/web/understanding-the-web.md)
- <i class="far fa-exclamation"></i> [Introduction to HTML](project/curriculum/materials/tutorials/introduction-to-html.md)
- <i class="far fa-exclamation"></i> [Pip and VirtualEnv](project/curriculum/materials/pages/python/pip-and-virtualenv.md)
- <i class="far fa-exclamation"></i> [A web-framework for Python: Flask](project/curriculum/materials/pages/python/python-flask.md)
- <i class="far fa-book-open"></i> [Flask documentation](http://flask.palletsprojects.com/) (the Quickstart gives a good overview)
- <i class="far fa-book-open"></i> [Jinja2 documentation](https://jinja.palletsprojects.com/en/2.10.x/templates/)
- <i class="far fa-book-open"></i> [HTML tutorials and references on MDN](https://developer.mozilla.org/en-US/docs/Web/HTML)
- [Tips & Tricks](project/curriculum/materials/pages/web/web-with-python-tips.md)
- [About unique identifiers](project/curriculum/materials/pages/general/unique-id.md)
