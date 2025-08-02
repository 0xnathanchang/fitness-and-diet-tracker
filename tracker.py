import datetime  # For timestamps
import json  # New: For saving/loading data
import os  # New: To check if file exists

class FitnessTracker:
    def __init__(self, height, weight, goal_weight, age, gender, activity_level):
        self.height = height  # cm
        self.weight = weight  # kg
        self.goal_weight = goal_weight  # kg
        self.age = age  # years
        self.gender = gender.lower()  # 'male' or 'female'
        self.activity_level = activity_level.lower()  # 'sedentary', 'light', 'moderate', 'active', 'very_active'
        self.bmr = self.calculate_bmr()
        self.tdee = self.calculate_tdee()
        self.daily_calorie_goal = self.calculate_daily_calories()
        self.food_logs = []  # List of dicts: {'date': str (isoformat), 'meal': str, 'calories': float, 'nutrition': {'protein': float, 'carbs': float, 'fats': float}}
        self.exercise_logs = []  # List of dicts: {'date': str (isoformat), 'activity': str, 'calories_burned': float}
        print(f"Onboarding complete! Your BMR: {self.bmr:.0f} cal, TDEE: {self.tdee:.0f} cal, Daily Goal: {self.daily_calorie_goal:.0f} cal.")

    def calculate_bmr(self):
        if self.gender == 'male':
            return 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        elif self.gender == 'female':
            return 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)
        else:
            raise ValueError("Gender must be 'male' or 'female'.")

    def calculate_tdee(self):
        factors = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55, 'active': 1.725, 'very_active': 1.9}
        factor = factors.get(self.activity_level, 1.2)
        return self.bmr * factor

    def calculate_daily_calories(self):
        weight_diff = self.goal_weight - self.weight
        if weight_diff < 0:
            return self.tdee - 500  # Deficit for loss
        elif weight_diff > 0:
            return self.tdee + 500  # Surplus for gain
        return self.tdee  # Maintenance

    def log_food(self, meal, calories, protein=0, carbs=0, fats=0):
        today = datetime.date.today().isoformat()  # Use string for JSON compatibility
        self.food_logs.append({
            'date': today,
            'meal': meal,
            'calories': calories,
            'nutrition': {'protein': protein, 'carbs': carbs, 'fats': fats}
        })
        print(f"Logged {meal}: {calories} cal.")

    def log_exercise(self, activity, calories_burned):
        today = datetime.date.today().isoformat()  # String for JSON
        self.exercise_logs.append({
            'date': today,
            'activity': activity,
            'calories_burned': calories_burned
        })
        print(f"Logged {activity}: {calories_burned} cal burned.")

    def daily_summary(self):
        today = datetime.date.today().isoformat()
        food_cal = sum(log['calories'] for log in self.food_logs if log['date'] == today)
        exercise_cal = sum(log['calories_burned'] for log in self.exercise_logs if log['date'] == today)
        net_cal = food_cal - exercise_cal - self.bmr  # Approximate net
        print(f"Today: Eaten {food_cal} cal, Burned {exercise_cal} cal (exercise), Net {net_cal} cal vs. goal {self.daily_calorie_goal}.")
        total_protein = sum(log['nutrition']['protein'] for log in self.food_logs if log['date'] == today)
        total_carbs = sum(log['nutrition']['carbs'] for log in self.food_logs if log['date'] == today)
        total_fats = sum(log['nutrition']['fats'] for log in self.food_logs if log['date'] == today)
        print(f"Macros: Protein {total_protein}g, Carbs {total_carbs}g, Fats {total_fats}g.")

    # New: Save state to JSON
    def save_to_file(self, filename='tracker_data.json'):
        data = {
            'height': self.height,
            'weight': self.weight,
            'goal_weight': self.goal_weight,
            'age': self.age,
            'gender': self.gender,
            'activity_level': self.activity_level,
            'food_logs': self.food_logs,
            'exercise_logs': self.exercise_logs
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print("Data saved!")

    # New: Load state from JSON
    @classmethod
    def load_from_file(cls, filename='tracker_data.json'):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
            tracker = cls(
                data['height'], data['weight'], data['goal_weight'],
                data['age'], data['gender'], data['activity_level']
            )
            tracker.food_logs = data['food_logs']
            tracker.exercise_logs = data['exercise_logs']
            print("Loaded saved data!")
            return tracker
        else:
            print("No saved data found. Starting fresh.")
            return None

# Interactive menu function
def main():
    filename = 'tracker_data.json'
    tracker = FitnessTracker.load_from_file(filename)
    if tracker is None:
        # Prompt for onboarding if no load
        while True:
            try:
                height = float(input("Height (cm): "))
                weight = float(input("Current weight (kg): "))
                goal_weight = float(input("Goal weight (kg): "))
                age = int(input("Age (years): "))
                gender = input("Gender (male/female): ").strip()
                activity_level = input("Activity level (sedentary/light/moderate/active/very_active): ").strip()
                tracker = FitnessTracker(height, weight, goal_weight, age, gender, activity_level)
                break
            except ValueError as e:
                print(f"Invalid input: {e}. Try again.")

    while True:
        print("\nFitness & Diet Tracker Menu:")
        print("1. Log Food")
        print("2. Log Exercise")
        print("3. View Daily Summary")
        print("4. Update Profile (Re-onboard)")
        print("5. Exit and Save")
        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            meal = input("Meal name: ").strip()
            try:
                calories = float(input("Calories: "))
                protein = float(input("Protein (g, optional - enter 0 if unknown): ") or 0)
                carbs = float(input("Carbs (g, optional): ") or 0)
                fats = float(input("Fats (g, optional): ") or 0)
                tracker.log_food(meal, calories, protein, carbs, fats)
            except ValueError:
                print("Invalid number. Try again.")

        elif choice == '2':
            activity = input("Activity name: ").strip()
            try:
                calories_burned = float(input("Calories burned: "))
                tracker.log_exercise(activity, calories_burned)
            except ValueError:
                print("Invalid number. Try again.")

        elif choice == '3':
            tracker.daily_summary()

        elif choice == '4':
            try:
                height = float(input("New height (cm): "))
                weight = float(input("New current weight (kg): "))
                goal_weight = float(input("New goal weight (kg): "))
                age = int(input("New age (years): "))
                gender = input("New gender (male/female): ").strip()
                activity_level = input("New activity level: ").strip()
                tracker = FitnessTracker(height, weight, goal_weight, age, gender, activity_level)
                # Preserve logs if wanted, or clear them
                print("Profile updated! Logs preserved.")
            except ValueError as e:
                print(f"Invalid input: {e}. Try again.")

        elif choice == '5':
            tracker.save_to_file(filename)
            print("Exiting. Keep up the great work!")
            break

        else:
            print("Invalid choice. Try 1-5.")

if __name__ == "__main__":
    main()