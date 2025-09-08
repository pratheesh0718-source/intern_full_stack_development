import os
from pathlib import Path
from dotenv import load_dotenv
import cohere

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Question, Answer

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("ask_question")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("ask_question")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("ask_question")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("ask_question")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def ask_cohere(request):
    if request.method == "POST":
        user_question = request.POST.get("question", "").strip()
        if not user_question:
            return JsonResponse({"answer": "Please enter a question."})

        try:
            # Save the question
            q = Question.objects.create(user=request.user, question_text=user_question)

            # Call Cohere API (older SDK uses `message`, not `messages`)
            response = co.chat(
                model="command",
                message=(
                    "You are an expert in electrical machines. "
                    "Answer ONLY questions related to electrical machines. "
                    "If unrelated, politely say it's outside your expertise.\n\n"
                    f"User question: {user_question}"
                ),
            )

            # Extract answer safely
            if hasattr(response, "text") and response.text:
                answer_text = response.text.strip()
            else:
                answer_text = str(response)

            # Save the answer
            Answer.objects.create(question=q, answer_text=answer_text)

            return JsonResponse({"answer": answer_text})

        except Exception as e:
            import traceback
            print("----- Cohere call failed -----")
            print("User question:", user_question)
            traceback.print_exc()
            print("----- end error -----")
            return JsonResponse({"answer": "⚠️ Sorry, something went wrong. Please try again later."})

    # GET request → render with history
    history = Question.objects.filter(user=request.user).select_related("answer").order_by("-created_at")
    return render(request, "ask_question.html", {"history": history})
