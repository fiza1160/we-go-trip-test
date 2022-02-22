from unittest.mock import patch, Mock

from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase
from django.test.client import Client

from reviews.admin import ReviewAdmin
from reviews.models import Review


class ReviewAdminTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        user = User(username='test_user', password='12345')
        user.save()
        self.user = user

    @patch('reviews.admin.requests.post')
    def test_response_change(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        request = self.client.post("/")
        request.POST = {"_publish": True}
        request.session = "session"
        request._messages = FallbackStorage(request)
        request.path = "/awesome/url/"

        admin_site = AdminSite()
        admin = ReviewAdmin(Review, admin_site)

        with self.subTest(case='If the review is not published, '
                               'a POST request must be sent '
                               'and "is_published" must become True'):
            review = Review(author=self.user, rating=4, text='test review')
            review.save()

            admin.response_change(request, review)

            params = {
                'author': review.author.id,
                'rating': review.rating,
                'review': review.text,
            }

            url = 'https://webhook.site/36693e00-8f59-4f7b-9a85-1d1e7ddde4d4'
            mock_post.assert_called_with(url, params=params)

            self.assertTrue(review.is_published)

        with self.subTest(case='If the review is published, '
                               'the POST request should not be sent.'):
            mock_post.reset_mock()

            published_review = Review(author=self.user, rating=4, text='test review', is_published=True)
            published_review.save()

            admin.response_change(request, published_review)

            mock_post.assert_not_called()
