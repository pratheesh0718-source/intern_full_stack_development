from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]   # newest questions first
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return f"Q{self.id} by {self.user.username}: {self.question_text[:50]}"


class Answer(models.Model):
    question = models.OneToOneField(   # 🔹 one question = one answer
        Question, on_delete=models.CASCADE, related_name="answer"
    )
    answer_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

    def __str__(self):
        return f"Answer to Q{self.question.id}"
