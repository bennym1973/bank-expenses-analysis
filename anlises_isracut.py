import pandas as pd
# Load the data
file_path = r'C:\myproject\anilses_data\הוצאות אשראי מרץ עמית.xlsx'  # Replace with the path to your file



# פונקציה לבדוק אם טקסט מכיל עברית
def is_hebrew(text):
    # אם הטקסט הוא לא מספרי ולא None, נחשב אותו כעברית אם הוא מכיל תו עברי
    if isinstance(text, str):  # לוודא שהטקסט הוא מיתר מסוג string
        return any("\u0590" <= c <= "\u05FF" for c in text)
    return False

# פונקציה להפיכת טקסט עברי
def reverse_text(text):
    if text is not None and isinstance(text, str) and is_hebrew(text):  # רק אם הטקסט הוא עברי
        return text[::-1]
    return text

# Load the data
# file_path = '/mnt/data/הוצאות אשראי מרץ עמית.xlsx'  # Path to the file uploaded earlier
data = pd.read_excel(file_path, sheet_name='Activities')

# Convert the transaction date to datetime
data['תאריך עסקה'] = pd.to_datetime(data['תאריך עסקה'])

# היפוך שמות העסקים וקטגוריות
data['שם  העסק'] = data['שם  העסק'].apply(reverse_text)
data['קטגוריה'] = data['קטגוריה'].apply(reverse_text)

# Function for analysis by Business Name
def analyze_by_business():
    print("Analysis by Business Name:")
    business_data = data.groupby('שם  העסק').agg({'סכום חיוב': 'sum'}).reset_index()
    print(business_data)

# Function for analysis by Category
def analyze_by_category():
    print("Analysis by Category:")
    category_data = data.groupby('קטגוריה').agg({'סכום חיוב': 'sum'}).reset_index()
    print(category_data)

# Function for Monthly Financial Analysis
def analyze_monthly_expenses():
    print("Monthly Financial Analysis:")
    data['Month'] = data['תאריך עסקה'].dt.to_period('M')
    monthly_expenses = data.groupby('Month').agg({'סכום חיוב': 'sum'}).reset_index()
    print(monthly_expenses)

# Function for Detailed Transaction View
def detailed_transactions():
    print("Detailed Transaction View:")
    print(data)

# Function for Top Expenses by Business
def top_expenses():
    print("Top Expenses by Business:")
    top_expenses_data = data.groupby('שם  העסק').agg({'סכום חיוב': 'sum'}).reset_index()
    top_expenses_data = top_expenses_data.sort_values(by='סכום חיוב', ascending=False)
    print(top_expenses_data.head())

# Menu for User Input
def menu():
    while True:
        print("\nSelect an option for analysis:")
        print("1. Analysis by Business Name")
        print("2. Analysis by Category")
        print("3. Monthly Financial Analysis")
        print("4. Detailed Transaction View")
        print("5. Top Expenses by Business")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            analyze_by_business()
        elif choice == '2':
            analyze_by_category()
        elif choice == '3':
            analyze_monthly_expenses()
        elif choice == '4':
            detailed_transactions()
        elif choice == '5':
            top_expenses()
        elif choice == '6':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the menu
menu()
