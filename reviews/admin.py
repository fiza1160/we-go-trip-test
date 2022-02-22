import requests
from django.contrib import admin
from django.http import HttpResponseRedirect

from reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('created', 'is_published', 'author', 'rating', 'text')
    readonly_fields = ('is_published',)
    change_form_template = "reviews_changeform.html"

    def response_change(self, request, obj):
        if obj.is_published:
            self.message_user(request, "Этот отзыв уже опубликован")
            return HttpResponseRedirect(".")

        if "_publish" in request.POST:
            params = {
                'author': obj.author.id,
                'rating': obj.rating,
                'review': obj.text,
            }

            url = 'https://webhook.site/36693e00-8f59-4f7b-9a85-1d1e7ddde4d4'
            response = requests.post(url, params=params)

            if response.status_code == 200:
                obj.is_published = True
                obj.save()
            self.message_user(request, "Отзыв опубликован")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
