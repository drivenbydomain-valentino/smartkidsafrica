# utils.py
import random

def process_action(student, action, amount):
    result = ""

    if action == "save":
        bonus = amount * 0.2
        student.savings += amount + bonus
        student.coins -= amount
        result = f"You saved ₦{amount} and earned bonus!"

    elif action == "spend":
        student.coins -= amount
        student.happiness += 5
        result = "You bought something fun 🎉"

    elif action == "invest" and student.level == "secondary":
        student.coins -= amount
        if random.random() > 0.5:
            gain = amount * 0.3
            student.savings += amount + gain
            result = "Investment successful 📈"
        else:
            loss = amount * 0.1
            student.savings -= loss
            result = "Investment loss ⚠️"

    student.save()
    return result

# utils.py (add this)

def get_ai_tip(student):
    if student.level == "primary":
        if student.savings < 50:
            return "Try saving more money 💰"
        return "Great job! Keep it up 😊"

    else:
        if student.coins > 50:
            return "Consider investing 📈"
        return "Balance saving and spending wisely"