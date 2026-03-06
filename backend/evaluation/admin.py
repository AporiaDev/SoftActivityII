from django.contrib import admin
from .models import Question, Submission, Answer, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'question_type', 'text_short']
    list_filter = ['question_type']
    ordering = ['order', 'id']

    def text_short(self, obj):
        return obj.text[:70] + '...' if len(obj.text) > 70 else obj.text
    text_short.short_description = 'Texto'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'value']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'user', 'result_type']
    list_filter = ['result_type', 'created_at']
    readonly_fields = ['created_at', 'result_type']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'submission', 'question', 'value']
    list_filter = ['submission', 'question__question_type']
