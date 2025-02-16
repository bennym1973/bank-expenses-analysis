import pandas as pd
import numpy as np

# קריאת קובץ האקסל
file_path = "הכנסות והוצאות אבא ממאי ועד היום.xlsx"
df = pd.read_excel(file_path, sheet_name='גיליון1')

# המרת עמודת התאריך לפורמט תאריך
df['תאריך'] = pd.to_datetime(df['תאריך'], errors='coerce')

# יצירת עמודת שנה-חודש
df['שנה-חודש'] = df['תאריך'].dt.to_period('M').astype(str)

# בחירת העמודות הרלוונטיות
summary_df = df[['שנה-חודש', 'הפעולה', 'חובה', 'זכות']].copy()

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

# הוספת שורת סכום עבור כל קבוצה
income_data.loc['סה"כ הכנסות'] = income_data.sum()
expense_data.loc['סה"כ הוצאות'] = expense_data.sum()

# חישוב ההפרש בין סה"כ הכנסות להוצאות
balance = income_data.loc['סה"כ הכנסות'] - expense_data.loc['סה"כ הוצאות']
balance.name = 'הפרש חודשי'

# חיבור הכל לטבלה אחת
final_table = pd.concat([income_data, expense_data, balance.to_frame().T])

# שמירת הנתונים לטבלה מסודרת בקובץ אקסל
excel_file = "monthly_financial_summary.xlsx"
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    final_table.to_excel(writer, sheet_name='סיכום חודשי')

print(f"הטבלה נשמרה בקובץ {excel_file}")
