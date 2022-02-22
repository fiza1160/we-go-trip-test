import json
import os
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from rest_framework.exceptions import ErrorDetail

from reviews.models import Review

base_dir = os.path.abspath(os.path.dirname(__file__))
settings_dir = f'{base_dir}\\static'


class ReviewListTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        for i in range(1, 3):
            User.objects.create(username=f'user {i}', password='12345').save()

        with mock.patch('django.utils.timezone.now') as mocked_now:
            mocked_now.return_value = '2022-02-21T15:06:04.723409Z'
            for user in User.objects.all():
                for i in range(1, 3):
                    Review.objects.create(
                        author=user,
                        rating=i,
                        text=f'Review #{i} from user {user.username}'
                    ).save()

    def test_get(self):
        with self.subTest(case='The GET request should return a list of reviews with all the fields'):
            with open(f'{settings_dir}\\get_response_correct.json') as f:
                correct_response = json.load(f)

            response = self.client.get('/reviews/')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), correct_response)

    def test_post(self):
        user = User.objects.get(id=1)
        self.client.force_login(user)

        with self.subTest(case='For an authorized user, the POST request should create a new review.'):
            mock_time = '2022-02-21T15:06:04.723409Z'
            review_id = Review.objects.count() + 1

            with mock.patch('django.utils.timezone.now') as mocked_now:
                mocked_now.return_value = mock_time
                response = self.client.post('/reviews/', {
                    'author': user.id,
                    'rating': 5,
                    'text': 'some text here',
                })

            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['id'], review_id)
            self.assertEqual(response.data['author'], user.id)
            self.assertEqual(response.data['rating'], 5)
            self.assertEqual(response.data['text'], 'some text here')
            self.assertEqual(response.data['created'], mock_time)
            self.assertEqual(response.data['is_published'], False)

        with self.subTest(case='For a new review, the "is_published" field must always be False.'):
            response = self.client.post('/reviews/', {
                'author': user.id,
                'rating': 5,
                'text': 'some text here',
                'is_published': True,
            })

            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['is_published'], False)

        with self.subTest(case='The "author" field is required.'):
            response = self.client.post('/reviews/', {
                'rating': 5,
                'text': 'some text here',
            })

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data, {'author': [ErrorDetail(string='Обязательное поле.', code='required')]})

        with self.subTest(case='The "rating" field is required.'):
            response = self.client.post('/reviews/', {
                'author': user.id,
                'text': 'some text here',
            })

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data, {'rating': [ErrorDetail(string='Обязательное поле.', code='required')]})

        with self.subTest(case='The "rating" field must be greater than or equal to 1.'):
            response = self.client.post('/reviews/', {
                'author': user.id,
                'rating': 0,
                'text': 'some text here',
            })

            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.data,
                {'rating': [ErrorDetail(string='Убедитесь, что это значение больше либо равно 1.', code='min_value')]}
            )

        with self.subTest(case='The "rating" field must be ess than or equal to 5.'):
            response = self.client.post('/reviews/', {
                'author': user.id,
                'rating': 8,
                'text': 'some text here',
            })

            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.data,
                {'rating': [
                    ErrorDetail(string='Убедитесь, что это значение меньше либо равно 5.', code='max_value')]}
            )

        with self.subTest(case='The "rating" field be an integer'):
            response = self.client.post('/reviews/', {
                'author': user.id,
                'rating': 3.5675,
                'text': 'some text here',
            })

            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.data,
                {'rating': [ErrorDetail(string='Введите правильное число.', code='invalid')]}
            )

        with self.subTest(case='The "text" field is optional.'):
            response = self.client.post('/reviews/', {
                'author': user.id,
                'rating': 3,
            })

            self.assertEqual(response.status_code, 201)

        with self.subTest(case='For an unauthorized user, the POST request should return 403 error.'):
            self.client.logout()

            response = self.client.post('/reviews/', {
                'author': user.id,
                'rating': 5,
                'text': 'some text here',
            })

            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                response.data,
                {'detail': ErrorDetail(string='Учетные данные не были предоставлены.', code='not_authenticated')}
            )
