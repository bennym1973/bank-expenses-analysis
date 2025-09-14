import pandas as pd
import matplotlib.pyplot as plt

# פונקציה להפיכת טקסט עברי
def reverse_text(text):
    if text is not None:
        return text[::-1]
    return text

# טעינת הנתונים מקובץ Excel עם קידוד UTF-8
data = pd.read_excel("stock_data_2022-2025.xlsx", engine='openpyxl')

# הדפסת שמות העמודות כדי לוודא את השמות הנכונים
print("שמות העמודות בקובץ Excel (לפני טיפול במרכאות):", data.columns.tolist())

# הסרת מרכאות משמות העמודות
data.columns = [col.strip('"').strip("'") for col in data.columns]

# הדפסת שמות העמודות לאחר הסרת מרכאות
print("שמות העמודות בקובץ Excel (לאחר טיפול במרכאות):", data.columns.tolist())

# רשימת שמות העמודות החדשים לפי התמונה והבנת הנתונים
column_names = {
    'שם נייר': 'שם',
    'מספר נייר': 'מספר',
    'סימבול': 'סימבול',
    'תאריך ערך': 'תאריך ערך',
    'תיאור פעולה': 'תיאור פעולה',
    'כמות': 'כמות',
    'שער': 'שער',
    'הערה': 'הערה',
    'סוג ח-ן': 'סוג ח-ן',
    'סוג מטבע': 'סוג מטבע',
    'תמורה ברוטו': 'תמורה ברוטו',
    'תמורה': 'תמורה',
    'מס בארץ': 'מס בארץ',
    'מס בחו"ל': 'מס בחו"ל',  # עמודה זו עשויה להיות חסרה, נבדוק
    'עמלה': 'עמלה',
    'עמלת דנ"פ': 'עמלת דנ"פ',
    'סיבת אי-ביצוע': 'סיבת אי-ביצוע',
    'תאריך רישום': 'תאריך רישום',
    'תאריך תמורה': 'תאריך תמורה'
}

# שינוי שמות העמודות לנוחות עבודה (אם צריך), לאחר הסרת מרכאות
data = data.rename(columns={key.strip('"').strip("'"): value for key, value in column_names.items()})

# המרת עמודות מספריות לפורמט נכון, עם טיפול בשגיאות
numeric_columns = ['כמות', 'שער', 'תמורה ברוטו', 'תמורה', 'מס בארץ', 'מס בחו"ל', 'עמלה', 'עמלת דנ"פ']
for col in numeric_columns:
    if col in data.columns:  # בדיקה אם העמודה קיימת
        data[col] = pd.to_numeric(data[col], errors='coerce')
    else:
        print(f"אזהרה: העמודה '{col}' לא נמצאה בקובץ, נוצרת עמודה ריקה.")
        data[col] = pd.to_numeric(pd.Series([None] * len(data)), errors='coerce')  # יצירת עמודה ריקה עם אותו מספר שורות

# תיקון סוג מטבע (הסרת מרכאות אם קיימות)
if 'סוג מטבע' in data.columns:
    data['סוג מטבע'] = data['סוג מטבע'].str.replace('"', '').str.replace("'", "")
else:
    print("אזהרה: עמודה 'סוג מטבע' לא נמצאה, נוצרת עמודה ריקה.")
    data['סוג מטבע'] = pd.Series([''] * len(data))  # יצירת עמודה ריקה עם אותו מספר שורות

# המרת עמודה 'תאריך ערך' למחרוזות אם צריך
if 'תאריך ערך' in data.columns:
    if not pd.api.types.is_string_dtype(data['תאריך ערך']):
        # אם זו עמודה של תאריכים (datetime), המר אותה למחרוזות
        data['תאריך ערך'] = data['תאריך ערך'].astype(str).str.strip()
    # אם יש ערכים חסרים או לא תקינים, טפל בהם
    data['תאריך ערך'] = data['תאריך ערך'].fillna('').astype(str)
else:
    print("אזהרה: עמודה 'תאריך ערך' לא נמצאה, נוצרת עמודה ריקה.")
    data['תאריך ערך'] = pd.Series([''] * len(data))

# פונקציה להצגת דוח מסכם
def summary_report():
    total_investment = data[data['תיאור פעולה'].str.contains('קניה|קנ. מחוץ לבורסה', na=False)]['תמורה'].sum()
    total_sales = data[data['תיאור פעולה'].str.contains('מכירה|קיעה', na=False)]['תמורה'].sum()
    total_dividends = data[data['תיאור פעולה'] == 'דיבידנד']['תמורה'].sum()
    total_fees = data['עמלה'].sum() + data['עמלת דנ"פ'].sum()
    total_profit_loss = total_sales + total_dividends - total_investment - total_fees

    print("\n===" + reverse_text("דוח מסכם") + "===")
    print(f"{reverse_text('סך השקעות')}: {total_investment:.2f}")
    print(f"{reverse_text('סך תמורות ממכירות')}: {total_sales:.2f}")
    print(f"{reverse_text('סך דיבידנדים')}: {dividends:.2f}")
    print(f"{reverse_text('סך עמלות')}: {total_fees:.2f}")
    print(f"{reverse_text('רווח/הפסד נטו')}: {total_profit_loss:.2f}")

# פונקציה לניתוח לפי שנה
def analyze_by_year(year):
    year_data = data[data['תאריך ערך'].str.startswith(str(year), na=False)]
    investment = year_data[year_data['תיאור פעולה'].str.contains('קניה|קנ. מחוץ לבורסה', na=False)]['תמורה'].sum()
    sales = year_data[year_data['תיאור פעולה'].str.contains('מכירה|קיעה', na=False)]['תמורה'].sum()
    dividends = year_data[year_data['תיאור פעולה'] == 'דיבידנד']['תמורה'].sum()
    fees = year_data['עמלה'].sum() + year_data['עמלת דנ"פ'].sum()

    print(f"\n===" + reverse_text(f"ניתוח לשנת {year}") + "===")
    print(f"{reverse_text('השקעות')}: {investment:.2f}")
    print(f"{reverse_text('מכירות')}: {sales:.2f}")
    print(f"{reverse_text('דיבידנדים')}: {dividends:.2f}")
    print(f"{reverse_text('עמלות')}: {fees:.2f}")

    # סינון ערכים חיוביים בלבד לגרף עוגה
    values = [v for v in [abs(investment), sales, dividends, fees] if v > 0]
    labels = [reverse_text(label) for label, v in zip(['השקעות', 'מכירות', 'דיבידנדים', 'עמלות'], 
                                                    [abs(investment), sales, dividends, fees]) if v > 0]

    if not values or len(values) < 1:
        print(reverse_text("אין נתונים חיוביים להצגה בגרף עוגה לשנה זו."))
    else:
        # גרף עוגה לפי סוגי פעולות
        plt.pie(values, 
                labels=labels, 
                autopct='%1.1f%%')
        plt.title(reverse_text(f"פילוח פעולות בשנת {year}"))
        plt.show()

# פונקציה לניתוח לפי מטבע
def analyze_by_currency(currency):
    currency_data = data[data['סוג מטבע'] == currency]
    investment = currency_data[currency_data['תיאור פעולה'].str.contains('קניה|קנ. מחוץ לבורסה', na=False)]['תמורה'].sum()
    sales = currency_data[currency_data['תיאור פעולה'].str.contains('מכירה|קיעה', na=False)]['תמורה'].sum()
    dividends = currency_data[currency_data['תיאור פעולה'] == 'דיבידנד']['תמורה'].sum()
    fees = currency_data['עמלה'].sum() + currency_data['עמלת דנ"פ'].sum()

    print(f"\n===" + reverse_text(f"ניתוח לפי מטבע {currency}") + "===")
    print(f"{reverse_text('השקעות')}: {investment:.2f}")
    print(f"{reverse_text('מכירות')}: {sales:.2f}")
    print(f"{reverse_text('דיבידנדים')}: {dividends:.2f}")
    print(f"{reverse_text('עמלות')}: {fees:.2f}")

    # סינון ערכים חיוביים בלבד לגרף עמודות
    values = [v for v in [abs(investment), sales, dividends, fees] if v > 0]
    labels = [reverse_text(label) for label, v in zip(['השקעות', 'מכירות', 'דיבידנדים', 'עמלות'], 
                                                    [abs(investment), sales, dividends, fees]) if v > 0]

    if not values or len(values) < 1:
        print(reverse_text("אין נתונים חיוביים להצגה בגרף עמודות למטבע זה."))
    else:
        # גרף עמודות
        plt.bar(labels, values)
        plt.title(reverse_text(f"פעילות לפי מטבע {currency}"))
        plt.ylabel(reverse_text("סכום"))
        plt.show()

# פונקציה לניתוח עמלות לפי מטבע
def analyze_fees():
    # המרת 'תאריך ערך' למחרוזות אם עדיין לא
    if not pd.api.types.is_string_dtype(data['תאריך ערך']):
        data['תאריך ערך'] = data['תאריך ערך'].astype(str).str.strip()
    data['תאריך ערך'] = data['תאריך ערך'].fillna('').astype(str)

    # חישוב עמלות לפי מטבע
    fees_non_usd = data[data['סוג מטבע'] != 'USD'][['עמלה', 'עמלת דנ"פ']].sum().sum()  # כל המטבעות שלא USD (למשל, ש"ח)
    fees_usd = data[data['סוג מטבע'] == 'USD'][['עמלה', 'עמלת דנ"פ']].sum().sum()

    # חישוב לפי שנים עבור כל מטבע
    fees_by_year_non_usd = data[data['סוג מטבע'] != 'USD'].groupby(data['תאריך ערך'].str[:4])[['עמלה', 'עמלת דנ"פ']].sum().sum(axis=1)
    fees_by_year_usd = data[data['סוג מטבע'] == 'USD'].groupby(data['תאריך ערך'].str[:4])[['עמלה', 'עמלת דנ"פ']].sum().sum(axis=1)

    print("\n===" + reverse_text("ניתוח עמלות") + "===")
    print(f"{reverse_text('סך כל העמלות שלא ב-USD')}: {fees_non_usd:.2f} שח")
    print(f"{reverse_text('סך כל העמלות ב-USD')}: {fees_usd:.2f} USD")
    print(reverse_text("עמלות לפי שנה ומטבע:"))
    print(f"{reverse_text('עמלות שלא ב-USD לפי שנה')}:\n{fees_by_year_non_usd}")
    print(f"{reverse_text('עמלות ב-USD לפי שנה')}:\n{fees_by_year_usd}")

    # גרף עמודות משולבות לעמלות לפי מטבע ושנה
    years = fees_by_year_non_usd.index.union(fees_by_year_usd.index)
    fees_non_usd_values = [fees_by_year_non_usd.get(y, 0) for y in years]
    fees_usd_values = [fees_by_year_usd.get(y, 0) for y in years]

    plt.bar(years, fees_non_usd_values, label=reverse_text('עמלות שלא ב-USD'), color='blue')
    plt.bar(years, fees_usd_values, bottom=fees_non_usd_values, label=reverse_text('עמלות ב-USD'), color='orange')
    plt.title(reverse_text("עמלות לאורך השנים לפי מטבע"))
    plt.xlabel(reverse_text("שנה"))
    plt.ylabel(reverse_text("סכום עמלות"))
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()

# פונקציה חדשה לניתוח דיבידנדים לפי מטבע ושנה
def analyze_dividends():
    # המרת 'תאריך ערך' למחרוזות אם עדיין לא
    if not pd.api.types.is_string_dtype(data['תאריך ערך']):
        data['תאריך ערך'] = data['תאריך ערך'].astype(str).str.strip()
    data['תאריך ערך'] = data['תאריך ערך'].fillna('').astype(str)

    # חישוב דיבידנדים לפי מטבע
    dividends_non_usd = data[(data['תיאור פעולה'] == 'דיבידנד') & (data['סוג מטבע'] != 'USD')]['תמורה'].sum()  # כל המטבעות שלא USD (למשל, ש"ח)
    dividends_usd = data[(data['תיאור פעולה'] == 'דיבידנד') & (data['סוג מטבע'] == 'USD')]['תמורה'].sum()

    # חישוב דיבידנדים לפי שנים עבור כל מטבע
    dividends_by_year_non_usd = data[(data['תיאור פעולה'] == 'דיבידנד') & (data['סוג מטבע'] != 'USD')].groupby(data['תאריך ערך'].str[:4])['תמורה'].sum()
    dividends_by_year_usd = data[(data['תיאור פעולה'] == 'דיבידנד') & (data['סוג מטבע'] == 'USD')].groupby(data['תאריך ערך'].str[:4])['תמורה'].sum()

    print("\n===" + reverse_text("ניתוח דיבידנדים") + "===")
    print(f"{reverse_text('סך כל הדיבידנדים שלא ב-USD')}: {dividends_non_usd:.2f} שח")
    print(f"{reverse_text('סך כל הדיבידנדים ב-USD')}: {dividends_usd:.2f} USD")
    print(reverse_text("דיבידנדים לפי שנה ומטבע:"))
    print(f"{reverse_text('דיבידנדים שלא ב-USD לפי שנה')}:\n{dividends_by_year_non_usd}")
    print(f"{reverse_text('דיבידנדים ב-USD לפי שנה')}:\n{dividends_by_year_usd}")

    # גרף עמודות משולבות לדיבידנדים לפי מטבע ושנה
    years = dividends_by_year_non_usd.index.union(dividends_by_year_usd.index)
    dividends_non_usd_values = [dividends_by_year_non_usd.get(y, 0) for y in years]
    dividends_usd_values = [dividends_by_year_usd.get(y, 0) for y in years]

    plt.bar(years, dividends_non_usd_values, label=reverse_text('דיבידנדים שלא ב-USD'), color='green')
    plt.bar(years, dividends_usd_values, bottom=dividends_non_usd_values, label=reverse_text('דיבידנדים ב-USD'), color='purple')
    plt.title(reverse_text("דיבידנדים לאורך השנים לפי מטבע"))
    plt.xlabel(reverse_text("שנה"))
    plt.ylabel(reverse_text("סכום דיבידנדים"))
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()

# פונקציה לניתוח רווח/הפסד למניה
def analyze_profit_loss_by_stock():
    if 'סימבול' in data.columns:  # בדיקה אם העמודה 'סימבול' קיימת
        stock_data = data.groupby('סימבול').agg({
            'תמורה': 'sum',
            'עמלה': 'sum',
            'עמלת דנ"פ': 'sum'
        })
        stock_data['רווח/הפסד'] = stock_data['תמורה'] - stock_data['עמלה'] - stock_data['עמלת דנ"פ']
        
        print("\n===" + reverse_text("ניתוח רווח/הפסד לפי מניה") + "===")
        print(reverse_text("מניה") + "\t" + reverse_text("רווח/הפסד"))
        for index, row in stock_data.iterrows():
            print(f"{index}\t{row['רווח/הפסד']:.2f}")

        # גרף עמודות לרווח/הפסד לפי מניה
        stock_data['רווח/הפסד'].plot(kind='bar')
        plt.title(reverse_text("רווח/הפסד לפי מניה"))
        plt.xlabel(reverse_text("מניה"))
        plt.ylabel(reverse_text("רווח/הפסד"))
        plt.show()
    else:
        print(reverse_text("אזהרה: עמודה 'סימבול' לא נמצאה, לא ניתן לבצע ניתוח רווח/הפסד לפי מניה."))

# פונקציה חדשה לפילטר לפי שנה עם רשימות מפורטות
def filter_by_year(year):
    year_data = data[data['תאריך ערך'].str.startswith(str(year), na=False)]

    print(f"\n===" + reverse_text(f"פילטר לפי שנה {year}") + "===")

    # קניות
    purchases = year_data[year_data['תיאור פעולה'].str.contains('קניה|קנ. מחוץ לבורסה', na=False)]
    print("\n" + reverse_text("רשימת קניות:"))
    if not purchases.empty:
        print(purchases[['תאריך ערך', 'שם', 'תיאור פעולה', 'תמורה', 'סוג מטבע']])
        print(f"{reverse_text('סך קניות')}: {purchases['תמורה'].sum():.2f}")
    else:
        print(reverse_text("אין קניות בשנה זו."))

    # מכירות
    sales = year_data[year_data['תיאור פעולה'].str.contains('מכירה|קיעה', na=False)]
    print("\n" + reverse_text("רשימת מכירות:"))
    if not sales.empty:
        print(sales[['תאריך ערך', 'שם', 'תיאור פעולה', 'תמורה', 'סוג מטבע']])
        print(f"{reverse_text('סך מכירות')}: {sales['תמורה'].sum():.2f}")
    else:
        print(reverse_text("אין מכירות בשנה זו."))

    # דיבידנדים
    dividends = year_data[year_data['תיאור פעולה'] == 'דיבידנד']
    print("\n" + reverse_text("רשימת דיבידנדים:"))
    if not dividends.empty:
        print(dividends[['תאריך ערך', 'שם', 'תיאור פעולה', 'תמורה', 'סוג מטבע']])
        dividends_non_usd = dividends[dividends['סוג מטבע'] != 'USD']['תמורה'].sum()
        dividends_usd = dividends[dividends['סוג מטבע'] == 'USD']['תמורה'].sum()
        print(f"{reverse_text('סך דיבידנדים שלא ב-USD')}: {dividends_non_usd:.2f} שח")
        print(f"{reverse_text('סך דיבידנדים ב-USD')}: {dividends_usd:.2f} USD")
    else:
        print(reverse_text("אין דיבידנדים בשנה זו."))

    # עמלות
    fees = year_data[['עמלה', 'עמלת דנ"פ', 'סוג מטבע']].dropna(how='all')
    print("\n" + reverse_text("רשימת עמלות:"))
    if not fees.empty:
        fees_non_usd = fees[fees['סוג מטבע'] != 'USD'][['עמלה', 'עמלת דנ"פ']].sum().sum()
        fees_usd = fees[fees['סוג מטבע'] == 'USD'][['עמלה', 'עמלת דנ"פ']].sum().sum()
        print(fees[['סוג מטבע', 'עמלה', 'עמלת דנ"פ']])
        print(f"{reverse_text('סך עמלות שלא ב-USD')}: {fees_non_usd:.2f} שח")
        print(f"{reverse_text('סך עמלות ב-USD')}: {fees_usd:.2f} USD")
    else:
        print(reverse_text("אין עמלות בשנה זו."))

# תפריט ראשי
def main_menu():
    while True:
        print("\n===" + reverse_text("תפריט ניתוח תיק השקעות") + "===")
        print("1. " + reverse_text("הצג דוח מסכם"))
        print("2. " + reverse_text("ניתוח לפי שנה"))
        print("3. " + reverse_text("ניתוח לפי מטבע"))
        print("4. " + reverse_text("ניתוח עמלות"))
        print("5. " + reverse_text("ניתוח דיבידנדים"))
        print("6. " + reverse_text("ניתוח רווח/הפסד לפי מניה"))
        print("7. " + reverse_text("פילטר לפי שנה"))
        print("8. " + reverse_text("יציאה"))
        
        choice = input(reverse_text("בחר אפשרות (1-8): ") + " ")

        if choice == '1':
            summary_report()
        elif choice == '2':
            year = input(reverse_text("הזן שנה (למשל, 2022): ") + " ")
            analyze_by_year(year)
        elif choice == '3':
            currency = input(reverse_text("הזן מטבע (ש''ח או USD): ") + " ")
            analyze_by_currency(currency)
        elif choice == '4':
            analyze_fees()
        elif choice == '5':
            analyze_dividends()
        elif choice == '6':
            analyze_profit_loss_by_stock()
        elif choice == '7':
            year = input(reverse_text("הזן שנה (למשל, 2022): ") + " ")
            filter_by_year(year)
        elif choice == '8':
            print(reverse_text("יוצא מהתוכנית..."))
            break
        else:
            print(reverse_text("בחירה לא תקינה, נסה שוב."))

# הפעעת התפריט
if __name__ == "__main__":
    main_menu()