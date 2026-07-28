# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StudentProfile, GameHistory
from .utils import process_action, get_ai_tip


@login_required
def game_home(request):
    student, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={'level': 'primary'}
    )

    context = {
        'student': student,
        'ai_tip': get_ai_tip(student),
        'history': GameHistory.objects.filter(student=student).order_by('-created_at')[:5]
    }

    return render(request, 'game/home.html', context)


@login_required
def play_action(request):
    if request.method == "POST":
        action = request.POST.get('action')
        amount = int(request.POST.get('amount'))

        student = StudentProfile.objects.get(user=request.user)

        result = process_action(student, action, amount)

        GameHistory.objects.create(
            student=student,
            action=action,
            amount=amount,
            result=result
        )

    return redirect('game_home')