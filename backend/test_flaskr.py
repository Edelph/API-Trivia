import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app

from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        # self.database_path = "postgres://{}/{}".format(
        #     'localhost:5432', self.database_name)
        self.database_path = "postgresql://{}:{}@{}/{}".format("postgres", "root",
                                                               'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)

            # create all tables
            self.db.create_all()

        self.newQuestions = {
            "question": "new Question ?",
            "answer": "yes it's my question",
            "difficulty": "3",
            "category": "3"
        }

        self.id = 0

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_put_question(self):
        put_questions = {
            "question": "new put Question ?",
            "answer": "yes its put my question",
            "difficulty": "3",
            "category": "3"
        }

        question = Question.query.filter(
            Question.answer == self.newQuestions["answer"],
            Question.question == self.newQuestions["question"],
            Question.difficulty == self.newQuestions["difficulty"],
            Question.category == self.newQuestions["category"],
        ).one_or_none()

        res = self.client().put("/questions/" + str(question.id), json=put_questions)
        data = json.loads(res.data)

        self.assertTrue(data["success"])
        self.assertEqual(res.status_code, 200)
        question.delete()

    def test_delete_404_questions(self):
        res = self.client().delete("/questions/200034")
        data = json.loads(res.data)

        self.assertFalse(data["success"])
        self.assertEqual(res.status_code, 404)

    def test_delete_questions(self):
        post_question = {
            "question": "new put Question ?",
            "answer": "yes its put my question",
            "difficulty": "3",
            "category": "3"
        }

        res = self.client().post("/questions", json=post_question)

        question = Question.query.filter(
            Question.answer == post_question["answer"],
            Question.question == post_question["question"],
            Question.difficulty == post_question["difficulty"],
            Question.category == post_question["category"],
        ).one_or_none()

        res = self.client().delete("/questions/"+str(question.id))
        data = json.loads(res.data)

        deleted_question = Question.query.filter(
            Question.id == self.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(deleted_question, None)
        self.assertTrue(data["success"])

    def test_post_question(self):
        res = self.client().post("/questions", json=self.newQuestions)
        data = json.loads(res.data)

        self.id = data["created"]

        self.assertTrue(data["success"])
        self.assertEqual(res.status_code, 201)

    def test_get_paginate_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_get_one_question(self):
        """ assure that id 18 is exist"""
        res = self.client().get("/questions/18")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_get_404_questions(self):
        res = self.client().get("/question")
        data = json.loads(res.data)

        self.assertFalse(data["success"])
        self.assertEqual(res.status_code, 404)

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["total_categories"])

    def test_get_404_categories(self):
        res = self.client().get("/category")
        data = json.loads(res.data)

        self.assertFalse(data["success"])
        self.assertEqual(res.status_code, 404)

    def test_post_404_question(self):
        res = self.client().post("/question", json=self.newQuestions)
        data = json.loads(res.data)

        self.assertFalse(data["success"])
        self.assertEqual(res.status_code, 404)

    def test_post_402_have_not_difficulty_question(self):
        newQuestion = {
            "question": "add Question ?",
            "answer": "yes it's my question",
            "category": "3"
        }
        res = self.client().post("/questions", json=newQuestion)
        data = json.loads(res.data)

        self.assertFalse(data["success"])
        self.assertEqual(res.status_code, 400)

    def test_post_402_invalid_attribute_question(self):
        newQuestion = {
            "question": "add Question ?",
        }
        res = self.client().post("/questions", json=newQuestion)
        data = json.loads(res.data)

        self.assertFalse(data["success"])
        self.assertEqual(res.status_code, 400)

    def test_questions_search(self):
        res = self.client().post("/questions/search",
                                 json={"searchTerm": "Giaconda"})
        data = json.loads(res.data)

        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"])

    def test_questions_search_invalid_url(self):
        res = self.client().post("/questions/search_term",
                                 json={"searchTerm": "Giaconda"})
        data = json.loads(res.data)

        self.assertFalse(data["success"])
        self.assertEqual(res.status_code, 404)

    def test_questions_search_invalid_body(self):
        res = self.client().post("/questions/search",
                                 json={"search_term": "Giaconda"})
        data = json.loads(res.data)

        self.assertFalse(data["success"])
        self.assertEqual(res.status_code, 400)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
