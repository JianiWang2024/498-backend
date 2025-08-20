# test the API endpoints - unit tests
# This file contains tests for the FAQ API endpoints using Flask's test client and unittest framework.
import unittest
from app import app, db, FAQ
import json

class FAQApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Set up the in-memory SQLite database for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()

        
    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_get_faqs(self):
        response = self.app.get('/api/faqs')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])

    def test_add_faq(self):
        response = self.app.post('/api/faqs', json={"question": "What is AI?", "answer": "Artificial Intelligence"})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("What is AI?", data['question'])

    def test_get_faq(self):
        response = self.app.post('/api/faqs', json={"question": "What is AI?", "answer": "Artificial Intelligence"})
        faq_id = json.loads(response.data)['id']
        response = self.app.get(f'/api/faqs/{faq_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['question'], "What is AI?")

    def test_update_faq(self):
        response = self.app.post('/api/faqs', json={"question": "What is AI?", "answer": "Artificial Intelligence"})
        faq_id = json.loads(response.data)['id']
        response = self.app.put(f'/api/faqs/{faq_id}', json={"answer": "Updated Answer"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['answer'], "Updated Answer")

    def test_delete_faq(self):
        response = self.app.post('/api/faqs', json={"question": "What is AI?", "answer": "Artificial Intelligence"})
        faq_id = json.loads(response.data)['id']
        response = self.app.delete(f'/api/faqs/{faq_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], "FAQ deleted successfully")

if __name__ == '__main__':
    unittest.main()