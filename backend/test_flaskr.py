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

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginate_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["total_categories"])

    def test_delete_questions(self):
        newQuestion = {
            "question": "add Question ?",
            "answer": "yes it's my question",
            "difficulty": "3",
            "category": "3"
        }
        res = self.client().post('/questions', json=newQuestion)
        question = Question.query.filter(
            Question.question == "add Question ?", Question.category == 3).one_or_none()

        res = self.client().delete("/questions/"+str(question.id))
        data = json.loads(res.data)

        deleted_question = Question.query.filter(
            Question.id == question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(deleted_question, None)
        self.assertTrue(data["success"])

    def test_post_question(self):
        res = self.client().post("/questions", json=self.newQuestions)
        data = json.loads(res.data)

        self.assertTrue(data["success"])
        self.assertEqual(res.status_code, 201)

    def test_questions_search(self):
        res = self.client().post("/questions/search",
                                 json={"search_term": "Giaconda"})
        data = json.loads(res.data)

        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
