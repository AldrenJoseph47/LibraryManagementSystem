from django.contrib import admin
from .models import Plan, Genre, Author, Book, Feedback, Payment

# Register your models here.
admin.site.register(Plan)
admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Payment)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback', 'response', 'is_responded')
    list_filter = ('user', 'response')
    search_fields = ('user__username', 'feedback')


admin.site.register(Feedback, FeedbackAdmin)
