import datetime  # For timestamps
import json  # For saving/loading data
import os  # To check if file exists

class FitnessTracker:
    def __init__(self, height, weight, goal_weight, age, gender, activity_level):
        # New: Validation
        if height <= 0 or weight <= 0 or goal_weight <= 0 or age < 18 or age > 100:
            raise ValueError("Invalid values: Height/weight must be >0, age 18-100.")
        if gender.lower() not in ['male', 'female']:
            raise ValueError("Gender must be 'male' or 'female'.")
        if activity_level.lower() not in ['sedentary', 'light', 'moderate', 'active', 'very_active']:
            raise ValueError("Invalid activity level.")

        self.height = height  # cm
        self.weight = weight  # kg
        self.goal_weight = goal_weight  # kg
        self.age = age  # years
        self.gender = gender.lower()
        self.activity_level = activity_level.lower()
        self.bmr = self.calculate_bmr()
        self.tdee = self.calculate_tdee()
        self.daily_calorie_goal = self.calculate_daily_calories()
        # New: BMI calculation (WHO formula)
        self.bmi = weight / ((height / 100) ** 2)
        bmi_category = self.get_bmi_category()
        self.food_logs = []
        self.exercise_logs = []
        # New: Default macro goals (as % of calories; can be customized later)
        self.macro_goals = {'protein': 0.30, 'carbs': 0.50, 'fats': 0.20}  # Adjust via update if needed
        print(f"Onboarding complete! BMR: {self.bmr:.0f} cal, TDEE: {self.tdee:.0f} cal, Daily Goal: {self.daily_calorie_goal:.0f} cal.")
        print(f"BMI: {self.bmi:.1f} ({bmi_category}). Remember, consult a doctor for health advice.")

    def get_bmi_category(self):
        if self.bmi < 18.5: return "Underweight"
        elif self.bmi < 25: return "Normal"
        elif self.bmi < 30: return "Overweight"
        else: return "Obese"

    def calculate_bmr(self):
        if self.gender == 'male':
            return 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        return 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)

    def calculate_tdee(self):
        factors = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55, 'active': 1.725, 'very_active': 1.9}
        return self.bmr * factors[self.activity_level]

    def calculate_daily_calories(self):
        weight_diff = self.goal_weight - self.weight
        if weight_diff < 0: return self.tdee - 500
        elif weight_diff > 0: return self.tdee + 500
        return self.tdee

    def log_food(self, meal, calories, protein=0, carbs=0, fats=0):
        today = datetime.date.today().isoformat()
        self.food_logs.append({
            'date': today, 'meal': meal, 'calories': calories,
            'nutrition': {'protein': protein, 'carbs': carbs, 'fats': fats}
        })
        print(f"Logged {meal}: {calories} cal.")

    def log_exercise(self, activity, calories_burned):
        today = datetime.date.today().isoformat()
        self.exercise_logs.append({
            'date': today, 'activity': activity, 'calories_burned': calories_burned
        })
        print(f"Logged {activity}: {calories_burned} cal burned.")

    def daily_summary(self, date_str=None):
        if date_str is None:
            date_str = datetime.date.today().isoformat()
        food_cal = sum(log['calories'] for log in self.food_logs if log['date'] == date_str)
        exercise_cal = sum(log['calories_burned'] for log in self.exercise_logs if log['date'] == date_str)
        net_cal = food_cal - exercise_cal - self.bmr
        cal_diff = net_cal - (self.daily_calorie_goal - self.tdee + self.bmr)  # Adjust for net vs goal
        status = "under" if cal_diff < 0 else "over" if cal_diff > 0 else "on"
        print(f"For {date_str}: Eaten {food_cal} cal, Burned {exercise_cal} cal (exercise), Net {net_cal} cal.")
        print(f"You're {abs(cal_diff):.0f} cal {status} goal. Keep going!")

        # Macro breakdown with warnings
        total_protein = sum(log['nutrition']['protein'] for log in self.food_logs if log['date'] == date_str)
        total_carbs = sum(log['nutrition']['carbs'] for log in self.food_logs if log['date'] == date_str)
        total_fats = sum(log['nutrition']['fats'] for log in self.food_logs if log['date'] == date_str)
        total_macros_cal = (total_protein * 4) + (total_carbs * 4) + (total_fats * 9)
        if total_macros_cal > 0:
            protein_pct = (total_protein * 4 / total_macros_cal)
            carbs_pct = (total_carbs * 4 / total_macros_cal)
            fats_pct = (total_fats * 9 / total_macros_cal)
            print(f"Macros: Protein {total_protein}g ({protein_pct:.0%}), Carbs {total_carbs}g ({carbs_pct:.0%}), Fats {total_fats}g ({fats_pct:.0%}).")
            if abs(protein_pct - self.macro_goals['protein']) > 0.20:
                print("Warning: Protein off by >20%—aim for balance.")
            # Similar for carbs/fats (omitted for brevity; add if wanted)
        else:
            print("No macros logged yet.")

    # New: Weekly summary
    def weekly_summary(self):
        today = datetime.date.today()
        week_start = (today - datetime.timedelta(days=6)).isoformat()
        food_cal = sum(log['calories'] for log in self.food_logs if log['date'] >= week_start)
        exercise_cal = sum(log['calories_burned'] for log in self.exercise_logs if log['date'] >= week_start)
        avg_net = (food_cal - exercise_cal - self.bmr * 7) / 7
        print(f"Last 7 days: Avg eaten {(food_cal/7):.0f} cal, Avg burned {(exercise_cal/7):.0f} cal, Avg net {avg_net:.0f} cal.")
        est_weight_change = (food_cal - exercise_cal - self.tdee * 7) / 7700  # ~7700 cal per kg
        direction = "loss" if est_weight_change < 0 else "gain"
        print(f"Estimated weight {direction}: {abs(est_weight_change):.2f} kg (approx; track actual weight).")

    # New: View historical logs
    def view_logs(self, type='all', date_str=None):
        if type == 'food' or type == 'all':
            print("Food Logs:")
            for log in self.food_logs:
                if date_str is None or log['date'] == date_str:
                    print(f"{log['date']}: {log['meal']} - {log['calories']} cal (P:{log['nutrition']['protein']} C:{log['nutrition']['carbs']} F:{log['nutrition']['fats']})")
        if type == 'exercise' or type == 'all':
            print("Exercise Logs:")
            for log in self.exercise_logs:
                if date_str is None or log['date'] == date_str:
                    print(f"{log['date']}: {log['activity']} - {log['calories_burned']} cal burned")

    def save_to_file(self, filename='tracker_data.json'):
        data = {
            'height': self.height, 'weight': self.weight, 'goal_weight': self.goal_weight,
            'age': self.age, 'gender': self.gender, 'activity_level': self.activity_level,
            'food_logs': self.food_logs, 'exercise_logs': self.exercise_logs,
            'macro_goals': self.macro_goals  # New: Save goals
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print("Data saved!")

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
            if 'macro_goals' in data:
                tracker.macro_goals = data['macro_goals']
            print("Loaded saved data!")
            return tracker
        print("No saved data. Starting fresh.")
        return None

# Interactive menu (expanded)
def main():
    filename = 'tracker_data.json'
    tracker = FitnessTracker.load_from_file(filename)
    if tracker is None:
        print("Welcome! Let's onboard.")
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
                print(f"Error: {e}. Try again.")

    while True:
        print("\nFitness & Diet Tracker Menu:")
        print("1. Log Food")
        print("2. Log Exercise")
        print("3. View Daily Summary")
        print("4. View Weekly Summary")
        print("5. View Historical Logs")
        print("6. Update Profile")
        print("7. Exit and Save")
        choice = input("Enter choice (1-7): ").strip()

        if choice == '1':
            meal = input("Meal name: ").strip()
            try:
                calories = float(input("Calories: "))
                protein = float(input("Protein (g, 0 if unknown): ") or 0)
                carbs = float(input("Carbs (g, 0 if unknown): ") or 0)
                fats = float(input("Fats (g, 0 if unknown): ") or 0)
                tracker.log_food(meal, calories, protein, carbs, fats)
            except ValueError:
                print("Invalid number.")

        elif choice == '2':
            activity = input("Activity name: ").strip()
            try:
                calories_burned = float(input("Calories burned: "))
                tracker.log_exercise(activity, calories_burned)
            except ValueError:
                print("Invalid number.")

        elif choice == '3':
            date_input = input("Date (YYYY-MM-DD, blank for today): ").strip() or None
            tracker.daily_summary(date_input)

        elif choice == '4':
            tracker.weekly_summary()

        elif choice == '5':
            log_type = input("Type (food/exercise/all): ").strip() or 'all'
            date_input = input("Date (YYYY-MM-DD, blank for all): ").strip() or None
            tracker.view_logs(log_type, date_input)

        elif choice == '6':
            try:
                # Reuse onboarding prompts
                height = float(input("New height (cm): "))
                weight = float(input("New weight (kg): "))
                goal_weight = float(input("New goal (kg): "))
                age = int(input("New age: "))
                gender = input("New gender: ").strip()
                activity_level = input("New activity level: ").strip()
                tracker = FitnessTracker(height, weight, goal_weight, age, gender, activity_level)
                print("Updated! Logs preserved.")
            except ValueError as e:
                print(f"Error: {e}.")

        elif choice == '7':
            tracker.save_to_file(filename)
            print("Exiting—progress saved!")
            break

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()