import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# קריאת קובץ האקסל עם הנתונים
file_path = "הכנסות והוצאות אבא ממאי ועד היום.xlsx"
df = pd.read_excel(file_path, sheet_name='גיליון1')

# המרת עמודת התאריך לפורמט תאריך
df['תאריך'] = pd.to_datetime(df['תאריך'], errors='coerce')

# יצירת עמודת שנה-חודש
df['שנה-חודש'] = df['תאריך'].dt.to_period('M').astype(str)

# בחירת עמודות רלוונטיות
summary_df = df[['שנה-חודש', 'הפעולה', 'חובה', 'זכות', 'פרטים']].copy()

# קיבוץ הנתונים לפי חודש ופעולה
monthly_summary = summary_df.groupby(['שנה-חודש', 'הפעולה'])[['חובה', 'זכות']].sum().reset_index()
monthly_summary = monthly_summary.fillna(0)

# יצירת טבלאות הכנסות והוצאות
income_data = monthly_summary[monthly_summary['זכות'] > 0].pivot(index='הפעולה', columns='שנה-חודש', values='זכות').fillna(0)
expense_data = monthly_summary[monthly_summary['חובה'] > 0].pivot(index='הפעולה', columns='שנה-חודש', values='חובה').fillna(0)

# הוספת שורות סכום
income_data.loc['סה"כ הכנסות'] = income_data.sum()
expense_data.loc['סה"כ הוצאות'] = expense_data.sum()

# חישוב יתרה חודשית
balance = income_data.loc['סה"כ הכנסות'] - expense_data.loc['סה"כ הוצאות']
balance.name = 'יתרה חודשית'

# חיבור הכל לטבלה אחת
final_table = pd.concat([income_data, expense_data, balance.to_frame().T])

# כותרת האפליקציה
st.title("📊 ניתוח הוצאות והכנסות")

# הצגת טבלת סיכום כללית
st.subheader("📌 סיכום פיננסי חודשי")
st.dataframe(final_table)

# גרף ויזואלי של הכנסות והוצאות לפי חודש
st.subheader("📉 גרף הוצאות והכנסות לפי חודש")

fig, ax = plt.subplots()
balance.plot(kind="bar", ax=ax, color=['green' if x >= 0 else 'red' for x in balance])
ax.set_ylabel("₪")
ax.set_title("יתרה חודשית")
st.pyplot(fig)

# בחירת חודש להצגת פירוט עסקאות
st.subheader("🔍 בחר חודש להצגת פירוט העסקאות")
months = list(final_table.columns)
selected_month = st.selectbox("📅 בחר חודש:", months)

# בחירת סוג פירוט
st.subheader("📂 בחר סוג פירוט")
option = st.radio("בחר סוג נתונים:", ['הכנסות', 'הוצאות'])

# הצגת פירוט עסקאות
if option == 'הכנסות':
    data = income_data[selected_month].dropna()
else:
    data = expense_data[selected_month].dropna()

st.write(f"📃 רשימת {option} עבור חודש {selected_month}:")
st.dataframe(data)

# בחירת פעולה ספציפית
st.subheader("📜 פירוט עסקאות לפי פעולה")
selected_action = st.selectbox("🔽 בחר פעולה:", data.index)

# הצגת פירוט העסקאות עבור הפעולה שנבחרה
transaction_details = summary_df[(summary_df['שנה-חודש'] == selected_month) & (summary_df['הפעולה'] == selected_action)]

if option == 'הכנסות':
    transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'זכות', 'פרטים']]
else:
    transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'חובה', 'פרטים']]

st.write(f"📜 פירוט עסקאות עבור '{selected_action}' בחודש {selected_month}:")
st.dataframe(transaction_details_display)
