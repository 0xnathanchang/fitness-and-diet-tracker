# Fitness and Diet Tracker App

A simple console-based Python app to track calories, food, exercise, and diet.

## Features
- Onboarding: Calculate daily calorie needs based on user info.
- Food logging: Track meals and nutrition.
- Exercise logging: Track activities and calories burned.
- Daily summaries.

## How to Run
1. Install Python.
2. Run `python tracker.py` in your terminal.

## Example
```python
tracker = FitnessTracker(height=180, weight=80, goal_weight=75, age=30, gender='male', activity_level='moderate')
tracker.log_food('Breakfast: Oatmeal', 300, protein=10, carbs=50, fats=5)
tracker.log_exercise('Run 5km', 400)
tracker.daily_summary()