import streamlit as st
from main import FamilyExpenseTracker
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from streamlit_option_menu import option_menu
from pathlib import Path
import bcrypt

# Streamlit Configuration
st.set_page_config(page_title="BudgetBuddy", page_icon="💰")

# Path Setup
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "main.css"

if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Expense Tracker
session_state = st.session_state
if "expense_tracker" not in session_state:
    session_state.expense_tracker = FamilyExpenseTracker()
expense_tracker = session_state.expense_tracker

# File Paths
expenses_csv = Path(expense_tracker.expense_csv)
family_csv = Path(expense_tracker.family_csv)
user_csv = current_dir / "users.csv"

# Ensure user.csv exists
if not user_csv.exists():
    pd.DataFrame(columns=["username", "password"]).to_csv(user_csv, index=False)

# Password Hashing
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Authenticate User
def authenticate_user(username, password):
    users = pd.read_csv(user_csv)
    user_row = users[users["username"] == username]
    if not user_row.empty and check_password(password, user_row["password"].iloc[0]):
        return True
    return False

# Register New User
def register_user(username, password):
    users = pd.read_csv(user_csv)
    if username in users["username"].values:
        return False
    hashed_password = hash_password(password)
    new_user = pd.DataFrame([[username, hashed_password.decode()]], columns=["username", "password"])
    new_user.to_csv(user_csv, mode='a', index=False, header=False)
    return True

# Navigation
if "logged_in" not in session_state:
    session_state.logged_in = False

if not session_state.logged_in:
    choice = st.sidebar.radio("Choose Action", ["Login", "Signup"])
    
    if choice == "Login":
        st.title("Login to BudgetBuddy")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate_user(username, password):
                st.success("Login successful!")
                st.session_state.logged_in = True
            else:
                st.error("Invalid username or password.")

    elif choice == "Signup":
        st.title("Create an Account")
        username = st.text_input("Choose a Username")
        password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up", key="signup_button"):
            if password != confirm_password:
                st.error("❌ Passwords do not match. Please try again.")
            else:
                if register_user(username, password):
                    st.success("✅ Account created! Please log in.")
                else:
                    st.error("❌ Username already exists. Please try a different one.")

else:
    # Centered Title
    st.markdown('<h1 style="text-align: center;">BudgetBuddy 💰</h1>', unsafe_allow_html=True)

    # Navigation Menu
    selected = option_menu(
        menu_title=None,
        options=["Data Entry", "Data Overview", "Data Visualization", "Prediction"],
        icons=["pencil-fill", "clipboard2-data", "bar-chart-fill", "graph-up-arrow"],
        orientation="horizontal",
    )

    # ✅ Data Entry Section
    if selected == "Data Entry":
        st.header("Add Family Member")
        with st.expander("Add Family Member"):
            member_name = st.text_input("Name").title()
            earning_status = st.checkbox("Earning Status")
            earnings = st.number_input("Earnings", value=1, min_value=1) if earning_status else 0

            if st.button("Add Member"):
                member = [m for m in expense_tracker.members if m.name == member_name]
                if not member:
                    expense_tracker.add_family_member(member_name, earning_status, earnings)
                    st.success("Member added successfully!")
                else:
                    expense_tracker.update_family_member(member[0], earning_status, earnings)
                    st.success("Member updated successfully!")

        st.header("Add Expenses")
        with st.expander("Add Expenses"):
            expense_category = st.selectbox("Category", ["Housing", "Food", "Transportation", "Entertainment", "Medical", "Investment", "Miscellaneous"])
            expense_description = st.text_input("Description (optional)").title()
            expense_value = st.number_input("Value", min_value=0)
            expense_date = st.date_input("Date")

            remaining_balance = expense_tracker.calculate_total_earnings() - expense_tracker.calculate_total_expenditure()

            if remaining_balance == 0:
                st.warning("⚠️ Your remaining balance is ₹0. Can't add new expenses!")
            elif remaining_balance < 1000:
                st.warning("⚠️ Your remaining balance is below ₹1000. Be cautious before adding new expenses!")

            if st.button("Add Expense"):
                if expense_value == 0:
                    st.error("❌ Expense value cannot be zero.")
                elif expense_value > remaining_balance:
                    st.error("❌ Insufficient balance!")
                else:
                    expense_tracker.merge_similar_category(expense_value, expense_category, expense_description, expense_date)
                    st.success("Expense added successfully!")

    # ✅ Data Overview Section
    elif selected == "Data Overview":
        st.header("Family Members")

        if not expense_tracker.members:
            st.info("No members added yet. Add a member from 'Data Entry'.")
        else:
            for i, member in enumerate(expense_tracker.members):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                col1.write(f"**{member.name}**")
                col2.write("Earning" if member.earning_status else "Not Earning")
                col3.write(f"₹{member.earnings}")
                if col4.button("Delete", key=f"delete_member_{i}"):
                    expense_tracker.delete_family_member(member)
                    st.rerun()

        st.header("Expenses")
        if not expense_tracker.expense_list:
            st.info("No expenses added yet. Add expenses from 'Data Entry'.")
        else:
            expense_data = []
            for i, expense in enumerate(expense_tracker.expense_list):
                col1, col2, col3, col4, col5 = st.columns([3, 2, 3, 2, 2])
                col1.write(f"**{expense.category}**")
                col2.write(f"₹{expense.value}")
                col3.write(expense.description)
                col4.write(expense.date)
                if col5.button("Delete", key=f"delete_expense_{i}"):
                    expense_tracker.delete_expense(expense)
                    st.rerun()
                expense_data.append([expense.category, f"₹{expense.value}", expense.description, expense.date])

    # Calculate total monthly earnings
        total_earnings_per_month = sum(member.earnings for member in expense_tracker.members)

    # Filter current month expenses only
        current_month = pd.to_datetime('today').to_period('M')

        data = pd.DataFrame(
            [(exp.category, exp.value, exp.date) for exp in expense_tracker.expense_list],
            columns=["Category", "Value", "Date"]
        )
        data["Date"] = pd.to_datetime(data["Date"])
        data["Month"] = data["Date"].dt.to_period("M")

        current_month_expenses = data[data["Month"] == current_month]
        total_expenditure = current_month_expenses["Value"].sum()

    # Display metrics without deducting previous months' expenses
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Monthly Earnings", f"₹{total_earnings_per_month}")
        col2.metric("Total Expenditure (Current Month)", f"₹{total_expenditure}")
        col3.metric("Remaining Balance", f"₹{total_earnings_per_month - total_expenditure}")

    # 📅 Monthly Expense Summary by Category
        st.header("📊 Monthly Expense Summary by Category")

        if not current_month_expenses.empty:
            summary = current_month_expenses.groupby("Category")["Value"].sum().reset_index()
            st.dataframe(summary, width=800)
            max_expense_category = summary.loc[summary["Value"].idxmax()]
            st.success(f"💡 **Highest Spending This Month**: ₹{max_expense_category['Value']} on **{max_expense_category['Category']}**.")
        else:
            st.info("No expenses available for this month.")

    # ✅ Data Visualization Section
    elif selected == "Data Visualization":
        st.header("Expense Analysis")

        if not expense_tracker.expense_list:
            st.info("No expenses to visualize. Please add some expenses.")
        else:
        # Convert data to DataFrame
            data = pd.DataFrame(
                [(exp.category, exp.value, exp.date) for exp in expense_tracker.expense_list],
                columns=["Category", "Value", "Date"]
            )
            data["Date"] = pd.to_datetime(data["Date"])

        # **1. Bar Chart - Total Expenses by Category**
            st.subheader("Total Expenses by Category")
            category_totals = data.groupby("Category")["Value"].sum().reset_index()

            fig, ax = plt.subplots(figsize=(8, 4))
            sns.barplot(x="Category", y="Value", data=category_totals, ax=ax, palette="viridis")
            ax.set_ylabel("Total Amount Spent")
            ax.set_xlabel("Expense Category")
            ax.set_title("Total Spending by Category")
            sns.despine()
            st.pyplot(fig)

        # **2. Pie Chart - Expense Distribution**
            st.subheader("Expense Distribution")
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(
                category_totals["Value"],
                labels=category_totals["Category"],
                autopct="%1.1f%%",
                startangle=140,
                colors=sns.color_palette("viridis", len(category_totals)),
            )
            ax.set_title("Expense Breakdown")
            st.pyplot(fig)

        # **3. Line Chart - Expense Trend Over Time**
            st.subheader("Expense Trend Over Time")
            daily_expenses = data.groupby("Date")["Value"].sum().reset_index()

            fig, ax = plt.subplots(figsize=(8, 4))
            sns.lineplot(x="Date", y="Value", data=daily_expenses, marker="o", color="b", ax=ax)
            ax.set_ylabel("Total Expenses")
            ax.set_xlabel("Date")
            ax.set_title("Daily Expense Trend")
            plt.xticks(rotation=45)
            sns.despine()
            st.pyplot(fig)
    elif selected == "Prediction":
        st.header("💡 Expense Prediction & Cost Reduction Suggestions")

        total_item_cost = st.number_input("Enter the total cost of the item:", min_value=1, value=5000)
        months_to_pay = st.number_input("Enter the number of months to pay:", min_value=1, value=6)
        desired_savings = st.number_input("Enter the amount you want to save per month:", min_value=0, value=1000)

        if st.button("🔮 Predict & Suggest"):
            if expenses_csv.exists():
                df_expenses = pd.read_csv(expenses_csv)
            else:
                st.error("🚨 No expense data available. Please add expenses first.")
                df_expenses = pd.DataFrame(columns=["Value", "Category", "Description", "Date", "Member"])

            if family_csv.exists():
                df_family = pd.read_csv(family_csv)
                total_earnings = df_family["Earnings"].sum()
            else:
                st.error("🚨 No family earnings data available. Please add family members first.")
                total_earnings = 0

            total_expenditure = df_expenses["Value"].sum()
            remaining_balance = total_earnings - total_expenditure
            monthly_installment = total_item_cost / months_to_pay
            required_balance = monthly_installment + desired_savings

            st.subheader("📊 Financial Summary")
            col1, col2, col3 = st.columns(3)
            col4,col5,col6=st.columns(3)
            col1.metric("Total Earnings", f"₹{total_earnings}")
            col2.metric("Total Expenditure", f"₹{total_expenditure}")
            col3.metric("Remaining Balance", f"₹{remaining_balance}")
            col6.metric("Required Monthly Balance", f"₹{required_balance:.2f}")
            col4.metric("Monthly Installment", f"₹{monthly_installment:.2f}")
            col5.metric("Desired_savings", f"₹{desired_savings:.2f}")

            if remaining_balance >= required_balance:
                st.success("✅ You can afford this purchase without adjusting expenses.")
            else:
                st.warning("⚠️ Your balance is insufficient. Expense reduction is needed.")
                deficit = required_balance - remaining_balance
                st.subheader("💰 Suggested Expense Reductions")

                # Categorize essential & non-essential expenses
                essential_categories = ["Housing", "Medical", "Investment"]
                non_essential_categories = ["Entertainment", "Food", "Transportation", "Miscellaneous"]

                category_expenses = df_expenses.groupby("Category")["Value"].sum().sort_values(ascending=False)

            reduction_suggestions = []
                
                # Prioritize reducing non-essential expenses first
            for category in non_essential_categories:
                if category in category_expenses:
                    amount = category_expenses[category]
                    if deficit <= 0:
                        break
                    reduction = min(amount * 0.20, deficit)  # Suggest reducing 20% from each category
                    reduction_suggestions.append((category, round(reduction, 2)))
                    deficit -= reduction

                # If still not enough, suggest reducing essential expenses moderately
            if deficit > 0:
                for category in essential_categories:
                    if category in category_expenses:
                        amount = category_expenses[category]
                        if deficit <= 0:
                            break
                        reduction = min(amount * 0.10, deficit)  # Suggest reducing 10% from essential categories
                        reduction_suggestions.append((category, round(reduction, 2)))
                        deficit -= reduction

                # Display Reduction Suggestions
            if reduction_suggestions:
                st.write("📉 To afford the purchase, consider reducing expenses in these categories:")
                for category, reduction in reduction_suggestions:
                    st.write(f"- Reduce **{category}** expenses by ₹{reduction}")
            else:
                st.write("💡 No significant expense reductions are available. Consider increasing savings or extending payment duration.")

  
    # ✅ Logout Button
    if st.sidebar.button("Logout"):
        session_state.logged_in = False
        st.rerun()
