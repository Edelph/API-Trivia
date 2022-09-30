
import os
from queue import Empty
from sre_constants import SUCCESS
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate(request, data, limit=10):
    page = request.args.get("page", 1, type=int)
    start = (page-1) * limit
    end = start + 10

    return data[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
      @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
      '''

    '''
      @TODO: Use the after_request decorator to set Access-Control-Allow
      '''
    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
      @TODO:
      Create an endpoint to handle GET requests
      for all available categories.
      '''

    @app.route('/categories')
    def getAllCategories():
        categories = Category.query.order_by(desc(Category.id)).all()
        formatted_categories = {}
        for c in categories:
            formatted_categories[c.id] = c.type
        return jsonify({
            "categories": formatted_categories,
            "success": True,
            "total_categories": len(categories)
        })

    '''
          @TODO:
          Create an endpoint to handle GET requests for questions,
          including pagination (every 10 questions).
          This endpoint should return a list of questions,
          number of total questions, current category, categories.

          TEST: At this point, when you start the application
          you should see questions and categories generated,
          ten questions per page and pagination at the bottom of the screen for three pages.
          Clicking on the page numbers should update the questions.
          '''

    @app.route('/questions')
    def getAllQuestions():
        questions = Question.query.order_by(desc(Question.id)).all()
        formatted_questions = [q.format() for q in questions]

        return jsonify({
            "questions": paginate(request, formatted_questions),
            "success": True,
            "current_category": Category.query.first().format(),
            "total_questions": len(formatted_questions)
        })
    '''

         @TODO:
         Create an endpoint to DELETE question using a question ID.

         TEST: When you click the trash icon next to a question, the question will be removed.
         This removal will persist in the database and when you refresh the page.
         '''

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def deleteQuestion(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if question is None:
            abort(404)

        question.delete()
        return jsonify({
            "success": True,
            "message": "deleted {}".format(question_id)
        }), 200

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    @app.route('/questions', methods=["POST"])
    def add_questions():
        data = request.get_json()

        answer = data.get("answer", None)
        question = data.get('question', None)
        difficulty = data.get('difficulty', None)
        category = data.get('category', None)

        if answer is None or question is None or difficulty is None or category is None or answer == "":
            abort(400)
        newQuestion = Question(question=question, answer=answer,
                               category=category, difficulty=difficulty)

        newQuestion.insert()

        return jsonify({
            "success": True,
            "created": newQuestion.id
        }), 201

    @app.route('/questions/<int:question_id>', methods=["PUT"])
    def update_questions(question_id):
        data = request.get_json()

        answer = data.get("answer", None)
        question = data.get('question', None)
        difficulty = data.get('difficulty', None)
        category = data.get('category', None)

        if answer is None or question is None or difficulty is None or category is None or answer == "":
            abort(400)

        db_question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if db_question is None:
            abort(404)

        db_question.question = question
        db_question.answer = answer
        db_question.category = category
        db_question.difficulty = difficulty

        db_question.update()
        return jsonify({
            "success": True,
            "updated": question_id
        }), 200

    @app.route('/questions/<int:question_id>', methods=["GET"])
    def get_question(question_id):
        db_question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if db_question is None:
            abort(404)

        return jsonify({
            "question": db_question.format(),
            "success": True
        }), 200

    '''
    
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('/questions/search', methods=["POST"])
    def search_questions():
        search_term = request.get_json().get("searchTerm", None)

        if search_term is None:
            abort(400)

        questions = Question.query.order_by(desc(Question.id)).filter(
            Question.question.ilike("%{}%".format(search_term))).all()

        formatted_questions = [q.format() for q in questions]

        return jsonify({
            "questions": formatted_questions,
            "success": True,
            "total_questions": len(formatted_questions)
        }), 200

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        category = Category.query.filter(
            Category.id == category_id).one_or_none()

        if category is None:
            abort(404)

        questions = Question.query.order_by(desc(Question.id)).filter(
            Question.category == category_id).all()
        formatted_questions = [q.format() for q in questions]

        return jsonify({
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': category.format()
        })

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=["POST"])
    def get_quizzes():
        data = request.get_json()
        previous_questions = data.get("previous_questions")
        quiz_category = data.get("quiz_category")

        if quiz_category.get("id") != 0:
            questions = Question.query.filter(
                Question.category == int(quiz_category.get("id"))).all()
        else:
            questions = Question.query.all()

        isValid = len(questions) == len(previous_questions)
        if(not isValid):
            while(not isValid):
                get_id = random.randint(0, len(questions)-1)
                question = questions[get_id]
                if(previous_questions is not Empty):
                    isValid = question.id not in previous_questions
                else:
                    isValid = True

            return jsonify({
                "question": question.format(),
                "previous_questions": previous_questions})
        return jsonify({
            "question": False,
            "previous_questions": previous_questions})

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    @app.errorhandler(422)
    def error422(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def error404(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def error400(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(500)
    def error500(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "error server"
        }), 500

    return app
