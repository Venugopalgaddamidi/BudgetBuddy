import csv
import os

class FamilyMember:
    def __init__(self, name, earning_status, earnings):
        self.name = name
        self.earning_status = earning_status
        self.earnings = earnings

class Expense:
    def __init__(self, value, category, description, date):
        self.value = value
        self.category = category
        self.description = description
        self.date = date

class FamilyExpenseTracker:
    def __init__(self):
        self.members = []
        self.expense_list = []
        self.family_csv = "family_data.csv"
        self.expense_csv = "expense_data.csv"
        self.load_family_data()
        self.load_expense_data()

    def save_family_data(self):
        """Save family members data to CSV"""
        with open(self.family_csv, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Earning Status", "Earnings"])
            for member in self.members:
                writer.writerow([member.name, member.earning_status, member.earnings])

    def load_family_data(self):
        """Load family members from CSV"""
        if os.path.exists(self.family_csv):
            with open(self.family_csv, mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.add_family_member(
                        row["Name"], row["Earning Status"] == "True", int(row["Earnings"])
                    )

    def save_expense_data(self):
        """Save expenses to CSV"""
        with open(self.expense_csv, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Value", "Category", "Description", "Date"])
            for expense in self.expense_list:
                writer.writerow(
                    [expense.value, expense.category, expense.description, expense.date]
                )

    def load_expense_data(self):
        """Load expenses from CSV"""
        if os.path.exists(self.expense_csv):
            with open(self.expense_csv, mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.merge_similar_category(
                        int(row["Value"]), row["Category"], row["Description"], row["Date"]
                    )

    def add_family_member(self, name, earning_status, earnings):
        member = FamilyMember(name, earning_status, earnings)
        self.members.append(member)
        self.save_family_data()

    def update_family_member(self, member, earning_status, earnings):
        member.earning_status = earning_status
        member.earnings = earnings
        self.save_family_data()

    def delete_family_member(self, member):
        self.members.remove(member)
        self.save_family_data()

    def merge_similar_category(self, value, category, description, date):
        expense = Expense(value, category, description, date)
        self.expense_list.append(expense)
        self.save_expense_data()

    def delete_expense(self, expense):
        self.expense_list.remove(expense)
        self.save_expense_data()

    def calculate_total_earnings(self):
        return sum(member.earnings for member in self.members)

    def calculate_total_expenditure(self):
        return sum(expense.value for expense in self.expense_list)
