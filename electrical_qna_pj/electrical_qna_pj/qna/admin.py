from django.contrib import admin
from .models import Question, Answer

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer_text')  # Add more fields if needed


admin.site.register(Question)
admin.site.register(Answer, AnswerAdmin)