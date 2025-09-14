import pandas as pd
import matplotlib.pyplot as plt

# Load the data
file_path = r'C:\myproject\cridiate_card\הוצאות אשראי אמא.xlsx'
data = pd.read_excel(file_path, sheet_name='גיליון1')

# פונקציה לבדוק אם טקסט מכיל עברית
def is_hebrew(text):
    if isinstance(text, str):
        return any('\u0590' <= c <= '\u05FF' for c in text)
    return False

# פונקציה להפוך טקסט עברי
def reverse_text(text):
    if isinstance(text, str) and is_hebrew(text):
        return text[::-1]
    return text

# המרת תאריך לפורמט datetime
data['תאריך'] = pd.to_datetime(data['תאריך'], errors='coerce')

# היפוך טקסטים רלוונטיים
data['שם בית עסק'] = data['שם בית עסק'].apply(reverse_text)
data['תאור סוג עסקת אשראי'] = data['תאור סוג עסקת אשראי'].apply(reverse_text)
data['קטגוריה'] = data['קטגוריה'].apply(reverse_text)

# פונקציה לגרף עמודות עם ערכים וטקסטים בעברית
def plot_bar_chart(x, y, title, xlabel, ylabel):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(x, y)
    plt.title(reverse_text(title), fontsize=16)
    plt.xlabel(reverse_text(xlabel), fontsize=12)
    plt.ylabel(reverse_text(ylabel), fontsize=12)
    plt.xticks(rotation=45, ha='right')
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height:,.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords='offset points', ha='center', fontsize=9)
    plt.tight_layout()
    plt.show()

# ניתוח לפי בית עסק
def analyze_by_business():
    print("Analysis by Business Name:")
    business_data = data.groupby('שם בית עסק').agg({'סכום קנייה': 'sum'}).reset_index()
    print(business_data)
    plot_bar_chart(business_data['שם בית עסק'], business_data['סכום קנייה'],
                   'סכום קנייה לפי בית עסק', 'שם בית עסק', 'סכום קנייה בש"ח')

# ניתוח לפי סוג עסקה
def analyze_by_transaction_type():
    print("Analysis by Transaction Type:")
    type_data = data.groupby('תאור סוג עסקת אשראי').agg({'סכום קנייה': 'sum'}).reset_index()
    print(type_data)
    plot_bar_chart(type_data['תאור סוג עסקת אשראי'], type_data['סכום קנייה'],
                   'סכום חיוב לפי סוג עסקה', 'סוג עסקה', 'סכום חיוב בש"ח')

# ניתוח לפי קטגוריה
def analyze_by_category():
    print("Analysis by Category:")
    category_data = data.groupby('קטגוריה').agg({'סכום קנייה': 'sum'}).reset_index()
    print(category_data)
    plot_bar_chart(category_data['קטגוריה'], category_data['סכום קנייה'],
                   'סכום חיוב לפי קטגוריה', 'קטגוריה', 'סכום חיוב בש"ח')

# ניתוח לפי חודש
def analyze_monthly_expenses():
    print("Monthly Financial Analysis:")
    data['חודש'] = data['תאריך'].dt.to_period('M')
    monthly = data.groupby('חודש').agg({'סכום קנייה': 'sum'}).reset_index()
    monthly['חודש'] = monthly['חודש'].astype(str)
    print(monthly)
    plot_bar_chart(monthly['חודש'], monthly['סכום קנייה'],
                   'סכום חיוב חודשי', 'חודש', 'סכום חיוב בש"ח')

# הצגת כל העסקאות
def detailed_transactions():
    print("Detailed Transaction View:")
    print(data)

# הוצאות גבוהות ביותר
def top_expenses():
    print("Top Expenses by Business:")
    top = data.groupby('שם בית עסק').agg({'סכום קנייה': 'sum'}).reset_index()
    top = top.sort_values(by='סכום קנייה', ascending=False)
    print(top.head(10))
    plot_bar_chart(top['שם בית עסק'].head(10), top['סכום קנייה'].head(10),
                   '10 בתי העסק עם ההוצאה הגבוהה ביותר', 'שם בית עסק', 'סכום קנייה בש"ח')

# תפריט למשתמש
def menu():
    while True:
        print("\n" + reverse_text("בחר פעולה:"))
        print("1.", reverse_text("ניתוח לפי בית עסק"))
        print("2.", reverse_text("ניתוח לפי סוג עסקה"))
        print("3.", reverse_text("ניתוח חודשי"))
        print("4.", reverse_text("הצגת כל העסקאות"))
        print("5.", reverse_text("הוצאות גבוהות ביותר"))
        print("6.", reverse_text("ניתוח לפי קטגוריה"))
        print("7.", reverse_text("יציאה"))

        choice = input(reverse_text("בחירה (1-7): "))

        if choice == '1':
            analyze_by_business()
        elif choice == '2':
            analyze_by_transaction_type()
        elif choice == '3':
            analyze_monthly_expenses()
        elif choice == '4':
            detailed_transactions()
        elif choice == '5':
            top_expenses()
        elif choice == '6':
            analyze_by_category()
        elif choice == '7':
            print(reverse_text("יציאה מהתכנית."))
            break
        else:
            print(reverse_text("בחירה לא חוקית. נסה שוב."))

# הרצת התפריט
menu()
