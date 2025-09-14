import pandas as pd
import numpy as np
import subprocess

import os
import subprocess

# # בדיקה שהקוד לא מפעיל את עצמו
# if "RUNNING_FROM_SUBPROCESS" not in os.environ:
#     with open("output.log", "w", encoding="utf-8") as log_file:
#         # הוספת משתנה סביבה כדי למנוע קריאה עצמית אינסופית
#         env = os.environ.copy()
#         env["RUNNING_FROM_SUBPROCESS"] = "1"

#         subprocess.run(["python", "-u", __file__], stdout=log_file, stderr=subprocess.STDOUT, env=env)

#     # פתיחת הקובץ לאחר שההרצה הסתיימה
#     subprocess.run(["notepad", "output.log"])
#     exit()  # מסיים את ההרצה הראשית כדי למנוע לולאות

import os
import subprocess
Debug=True

if not Debug:

    script_name = "Bank Transaction Analysis_dade_rev1.py"  # שם הקובץ שאתה רוצה להריץ
    script_path = os.path.join(os.path.dirname(__file__), script_name)  # יצירת נתיב מלא

    if "RUNNING_FROM_SUBPROCESS" not in os.environ:
        env = os.environ.copy()
        env["RUNNING_FROM_SUBPROCESS"] = "1"

        # הוספת מרכאות נכונות לנתיב כדי למנוע בעיה עם רווחים
        script_path = f'"{script_path}"'  # מרכאות מסביב לנתיב, רק פעם אחת!
        print(f"מריץ את הסקריפט: {script_path}")
        # הרצה ב-CMD נפרד מבלי ליצור לולאה אינסופית
        subprocess.run(f'start cmd /k python -u {script_path}', shell=True, env=env)
        exit()  # מסיים את הריצה של הקובץ הראשי כדי למנוע תקיעה


# פונקציה להצגת פירוט הכנסות/הוצאות למשתמש
def reverse_text(text):
    if text is not None:
        return text[::-1]


# קריאת קובץ האקסל
file_path = "הכנסות והוצאות אבא ממאי ועד היום.xlsx"
df = pd.read_excel(file_path, sheet_name='גיליון1')

# המרת עמודת התאריך לפורמט תאריך
df['תאריך'] = pd.to_datetime(df['תאריך'], errors='coerce')

# יצירת עמודת שנה-חודש
df['שנה-חודש'] = df['תאריך'].dt.to_period('M').astype(str)

# בחירת העמודות הרלוונטיות
summary_df = df[['שנה-חודש', 'הפעולה', 'חובה', 'זכות','פרטים']].copy()

# שמירת הנתונים לקובץ summary.xlsx
summary_file = "summary.xlsx"
summary_df.to_excel(summary_file, index=False)

# קיבוץ הנתונים לפי חודש ופעולה
monthly_summary = summary_df.groupby(['שנה-חודש', 'הפעולה'])[['חובה', 'זכות']].sum().reset_index()

# מילוי ערכים חסרים באפס
monthly_summary = monthly_summary.fillna(0)

# יצירת טבלה מסכמת עם הכנסות בראש והוצאות מתחתיהן
income_data = monthly_summary[monthly_summary['זכות'] > 0].pivot(index='הפעולה', columns='שנה-חודש', values='זכות').fillna(0)
expense_data = monthly_summary[monthly_summary['חובה'] > 0].pivot(index='הפעולה', columns='שנה-חודש', values='חובה').fillna(0)

# # הוספת שורת סכום עבור כל קבוצה
# income_data.loc['סה"כ הכנסות'] = income_data.sum()
# expense_data.loc['סה"כ הוצאות'] = expense_data.sum()

# חישוב ההפרש בין סה"כ הכנסות להוצאות
# balance = income_data.loc['סה"כ הכנסות'] - expense_data.loc['סה"כ הוצאות']
# balance.name = 'הפרש חודשי'

# חיבור הכל לטבלה אחת
# final_table = pd.concat([income_data, expense_data, balance.to_frame().T])

###
# סינון עסקאות חיסכון
keywords_savings = ["זכוי מת. חסכון","פרעון פקדון","הפקדה לחסכון","הפקדה לחסכון",'ני"ע-קניה']  # ניתן להוסיף עוד מילים רלוונטיות

# **שלב 1: הוספת שורות סיכום רגילות**
income_data.loc['סה"כ הכנסות'] = income_data.sum(numeric_only=True)
expense_data.loc['סה"כ הוצאות'] = expense_data.sum(numeric_only=True)

# **שלב 2: רק עכשיו לבצע סינון חיסכונות**
savings_income_rows = income_data.loc[income_data.index.str.contains('|'.join(keywords_savings), na=False)]
savings_expense_rows = expense_data.loc[expense_data.index.str.contains('|'.join(keywords_savings), na=False)]

# **שלב 3: חישוב סה"כ הכנסות ללא חיסכונות**
income_without_savings = income_data.loc['סה"כ הכנסות'] - savings_income_rows.sum(numeric_only=True)
income_without_savings.name = 'סה"כ הכנסות ללא חיסכונות'

# **שלב 4: חישוב סה"כ הוצאות ללא חיסכונות**
expense_without_savings = expense_data.loc['סה"כ הוצאות'] - savings_expense_rows.sum(numeric_only=True)
expense_without_savings.name = 'סה"כ הוצאות ללא חיסכונות'

# **שלב 5: חישוב הפרשים**
balance = income_data.loc['סה"כ הכנסות'] - expense_data.loc['סה"כ הוצאות']
balance.name = 'הפרש חודשי'

balance_no_savings = income_without_savings - expense_without_savings
balance_no_savings.name = 'הפרש חודשי ללא חיסכונות'

# **שלב 6: הוספת כל הנתונים לטבלה הסופית**
final_table = pd.concat([
    income_data, 
    pd.DataFrame(income_without_savings).T,  
    expense_data, 
    pd.DataFrame(expense_without_savings).T, 
    pd.DataFrame(balance).T,  
    pd.DataFrame(balance_no_savings).T  
])



###

# שמירת הנתונים לטבלה מסודרת בקובץ אקסל
excel_file = "monthly_financial_summary.xlsx"
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    final_table.to_excel(writer, sheet_name='סיכום חודשי')

print(f"\n📁 {reverse_text('הטבלה נשמרה בקובץ')}: {excel_file}")



def display_detailed_transactions_old():
    print(f"\n📊 {reverse_text('לאחר שקובץ עובר ושב הוטען ,ניתן לראות את ההוצאות או הכנסות של כו לחודש בהתאם לבחירה של המשתמש  ')}:")
    # print(f"\n📊 {reverse_text(' של הכנסות או הוצאות המשתמש צריך להזין את מספר החודש שבו הוא רוצה לראות פירוט')}:")
    # print(f"\n📊 {reverse_text('סיכום חודשי')}:")
    # print(final_table)
    final_table_display = final_table.copy()

    # הפיכת שם האינדקס של העמודות (כותרת 'שנה-חודש')
    if final_table_display.columns.name == 'שנה-חודש':
        final_table_display.columns.name = reverse_text('שנה-חודש')

    # הפיכת שמות השורות בעברית
    final_table_display.index = [reverse_text(idx) for idx in final_table_display.index]

    print("\n" + "="*50)
    print("📊", reverse_text("סיכום חודשי"))
    print("="*50)
    print(final_table_display)
    print("="*50)

    months = list(final_table.columns)
    print(f"\n📅 {reverse_text('בחר חודש להצגת פירוט')}: ")
    for i, month in enumerate(months):
        print(f"{i+1}.{month}")
    
    month_choice = int(input(f"{reverse_text('הזן את מספר החודש')}: ")) - 1
    selected_month = months[month_choice]
    
    print(f"\n📂 {reverse_text('בחר סוג פירוט')}: ")
    print(f"1. {reverse_text('הכנסות')}")
    print(f"2. {reverse_text('הוצאות')}")
    type_choice = int(input(f"{reverse_text('הזן את מספר האפשרות')}: "))
    
    if type_choice == 1:
        data = income_data[selected_month].dropna()
    else:
        data = expense_data[selected_month].dropna()
    
    print(f"\n💰 {reverse_text('בחר פעולה להצגת פירוט')}: ")
    for i, action in enumerate(data.index):
        print(f"{i+1}. {reverse_text(action)} - ₪{data[action]:,.2f}")
    
    action_choice = int(input(f"{reverse_text('הזן את מספר הפעולה')}: ")) - 1
    selected_action = data.index[action_choice]
    
    print(f"\n📜 {reverse_text('פירוט העסקאות עבור')} '{reverse_text(selected_action)}' {reverse_text('בחודש')} {reverse_text(selected_month)}:")
    transaction_details = summary_df[(summary_df['שנה-חודש'] == selected_month) & (summary_df['הפעולה'] == selected_action)]
    
    if type_choice == 1:
        transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'זכות', 'פרטים']].copy()
    else:
        transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'חובה', 'פרטים']].copy()
    # היפוך רק של הערכים בטבלה
    transaction_details_display['הפעולה'] = transaction_details_display['הפעולה'].apply(reverse_text)
    transaction_details_display['פרטים'] = transaction_details_display['פרטים'].apply(reverse_text)

    # הפיכת שמות העמודות רק בזמן ההדפסה
    transaction_details_display.columns = [reverse_text(col) for col in transaction_details_display.columns]

    print(transaction_details_display)

def display_detailed_transactions_2_16():
    print(f"\n📊 {reverse_text('לאחר שקובץ עובר ושב הוטען ,ניתן לראות את ההוצאות או הכנסות של כו לחודש בהתאם לבחירה של המשתמש  ')}:")
    
    final_table_display = final_table.copy()
    
    if final_table_display.columns.name == 'שנה-חודש':
        final_table_display.columns.name = reverse_text('שנה-חודש')
    
    final_table_display.index = [reverse_text(idx) for idx in final_table_display.index]
    
    print("\n" + "="*50)
    print("📊", reverse_text("סיכום חודשי"))
    print("="*50)
    print(final_table_display)
    print("="*50)
    
    months = list(final_table.columns)
    print(f"\n📅 {reverse_text('בחר חודש להצגת פירוט (או 0 ליציאה)')}: ")
    for i, month in enumerate(months):
        print(f"{i+1}.{month}")
    
    month_choice = input(f"{reverse_text('הזן את מספר החודש')}: ")
    if month_choice == '0':
        return
    month_choice = int(month_choice) - 1
    selected_month = months[month_choice]
    
    print(f"\n📂 {reverse_text('בחר סוג פירוט (או 0 ליציאה)')}: ")
    print(f"1. {reverse_text('הכנסות')}")
    print(f"2. {reverse_text('הוצאות')}")
    
    type_choice = input(f"{reverse_text('הזן את מספר האפשרות')}: ")
    if type_choice == '0':
        return
    type_choice = int(type_choice)
    
    if type_choice == 1:
        data = income_data[selected_month].dropna()
    else:
        data = expense_data[selected_month].dropna()
    
    print(f"\n💰 {reverse_text('בחר פעולה להצגת פירוט (או 0 ליציאה)')}: ")
    for i, action in enumerate(data.index):
        print(f"{i+1}. {reverse_text(action)} - ₪{data[action]:,.2f}")
    
    action_choice = input(f"{reverse_text('הזן את מספר הפעולה')}: ")
    if action_choice == '0':
        return
    action_choice = int(action_choice) - 1
    selected_action = data.index[action_choice]
    
    print(f"\n📝 {reverse_text('פירוט העסקאות עבור')} '{reverse_text(selected_action)}' {reverse_text('בחודש')} {reverse_text(selected_month)}:")
    transaction_details = summary_df[(summary_df['שנה-חודש'] == selected_month) & (summary_df['הפעולה'] == selected_action)]
    
    if type_choice == 1:
        transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'זכות', 'פרטים']].copy()
    else:
        transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'חובה', 'פרטים']].copy()
    
    transaction_details_display['הפעולה'] = transaction_details_display['הפעולה'].apply(reverse_text)
    transaction_details_display['פרטים'] = transaction_details_display['פרטים'].apply(reverse_text)
    transaction_details_display.columns = [reverse_text(col) for col in transaction_details_display.columns]
    
    print(transaction_details_display)

def display_detailed_transactions():
    while True:
        print(f"\n📊 {reverse_text('לאחר שקובץ עובר ושב הוטען ,ניתן לראות את ההוצאות או הכנסות של כו לחודש בהתאם לבחירה של המשתמש  ')}:")
        
        final_table_display = final_table.copy()
        
        if final_table_display.columns.name == 'שנה-חודש':
            final_table_display.columns.name = reverse_text('שנה-חודש')
        
        final_table_display.index = [reverse_text(idx) for idx in final_table_display.index]
        
        print("\n" + "="*50)
        print("📊", reverse_text("סיכום חודשי"))
        print("="*50)
        print(final_table_display)
        print("="*50)
        
        months = list(final_table.columns)
        print(f"\n📅 {reverse_text('בחר חודש להצגת פירוט (או 0 ליציאה לתפריט הראשי)')}: ")
        for i, month in enumerate(months):
            print(f"{i+1}.{month}")
        
        month_choice = input(f"{reverse_text('הזן את מספר החודש')}: ")
        if month_choice == '0':
            return
        month_choice = int(month_choice) - 1
        selected_month = months[month_choice]
        
        print(f"\n📂 {reverse_text('בחר סוג פירוט (או 0 ליציאה לתפריט הראשי)')}: ")
        print(f"1. {reverse_text('הכנסות')}")
        print(f"2. {reverse_text('הוצאות')}")
        
        type_choice = input(f"{reverse_text('הזן את מספר האפשרות')}: ")
        if type_choice == '0':
            return
        type_choice = int(type_choice)
        
        if type_choice == 1:
            data = income_data[selected_month].dropna()
        else:
            data = expense_data[selected_month].dropna()
        
        print(f"\n💰 {reverse_text('בחר פעולה להצגת פירוט (או 0 ליציאה לתפריט הראשי)')}: ")
        for i, action in enumerate(data.index):
            print(f"{i+1}. {reverse_text(action)} - ₪{data[action]:,.2f}")
        
        action_choice = input(f"{reverse_text('הזן את מספר הפעולה')}: ")
        if action_choice == '0':
            return
        action_choice = int(action_choice) - 1
        selected_action = data.index[action_choice]
        
        print(f"\n📝 {reverse_text('פירוט העסקאות עבור')} '{reverse_text(selected_action)}' {reverse_text('בחודש')} {reverse_text(selected_month)}:")
        transaction_details = summary_df[(summary_df['שנה-חודש'] == selected_month) & (summary_df['הפעולה'] == selected_action)]
        
        if type_choice == 1:
            transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'זכות', 'פרטים']].copy()
        else:
            transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'חובה', 'פרטים']].copy()
        
        transaction_details_display['הפעולה'] = transaction_details_display['הפעולה'].apply(reverse_text)
        transaction_details_display['פרטים'] = transaction_details_display['פרטים'].apply(reverse_text)
        transaction_details_display.columns = [reverse_text(col) for col in transaction_details_display.columns]
        
        print(transaction_details_display)


while True:
    display_detailed_transactions()
    exit_choice = input(f"{reverse_text('הזן 0 ליציאה או כל מספר אחר לבדיקת נתונים נוספים')}: ")
    if exit_choice == '0':
        break



# הפעלת תפריט הפירוט
# display_detailed_transactions()
# while True:
#     display_detailed_transactions()
#     exit_choice = input(f"{reverse_text('הזן 0 ליציאה או כל מספר אחר לבדיקת נתונים נוספים')}: ")
#     if exit_choice == '0':
#         break
