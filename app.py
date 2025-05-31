import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# פונקציה להצגת טקסט הפוך (לעברית)
def reverse_text(text):
    if text is not None:
        return text[::-1]

# סיסמה בסיסית לכניסה
PASSWORD = "0544752357"
st.title("🔒 התחברות לאפליקציה")
password_input = st.text_input("📌 הזן סיסמה:", type="password")
if password_input != PASSWORD:
    st.error("❌ סיסמה שגויה! נסה שוב.")
    st.stop()

st.success("✅ סיסמה נכונה! ברוך הבא לאפליקציה.")

# קריאת הקובץ
file_path = "הכנסות והוצאות אבא ממאי ועד היום.xlsx"
df = pd.read_excel(file_path, sheet_name='גיליון1')
df['תאריך'] = pd.to_datetime(df['תאריך'], errors='coerce')
df['שנה-חודש'] = df['תאריך'].dt.to_period('M').astype(str)
summary_df = df[['שנה-חודש', 'הפעולה', 'חובה', 'זכות', 'פרטים']].copy()

# טבלאות הכנסות/הוצאות
monthly_summary = summary_df.groupby(['שנה-חודש', 'הפעולה'])[['חובה', 'זכות']].sum().reset_index()
income_data = monthly_summary[monthly_summary['זכות'] > 0].pivot(index='הפעולה', columns='שנה-חודש', values='זכות').fillna(0)
expense_data = monthly_summary[monthly_summary['חובה'] > 0].pivot(index='הפעולה', columns='שנה-חודש', values='חובה').fillna(0)

# סיכומים עם וללא חיסכון
keywords_savings = ["זכוי מת. חסכון","פרעון פקדון","הפקדה לחסכון","הפקדה לחסכון",'ני"ע-קניה']
income_data.loc['סה"כ הכנסות'] = income_data.sum(numeric_only=True)
expense_data.loc['סה"כ הוצאות'] = expense_data.sum(numeric_only=True)
savings_income_rows = income_data.loc[income_data.index.str.contains('|'.join(keywords_savings), na=False)]
savings_expense_rows = expense_data.loc[expense_data.index.str.contains('|'.join(keywords_savings), na=False)]
income_without_savings = income_data.loc['סה"כ הכנסות'] - savings_income_rows.sum(numeric_only=True)
income_without_savings.name = 'סה"כ הכנסות ללא חיסכונות'
expense_without_savings = expense_data.loc['סה"כ הוצאות'] - savings_expense_rows.sum(numeric_only=True)
expense_without_savings.name = 'סה"כ הוצאות ללא חיסכונות'
balance = income_data.loc['סה"כ הכנסות'] - expense_data.loc['סה"כ הוצאות']
balance.name = 'הפרש חודשי'
balance_no_savings = income_without_savings - expense_without_savings
balance_no_savings.name = 'הפרש חודשי ללא חיסכונות'
final_table = pd.concat([income_data, pd.DataFrame(income_without_savings).T, expense_data,
                         pd.DataFrame(expense_without_savings).T, pd.DataFrame(balance).T,
                         pd.DataFrame(balance_no_savings).T])

# כותרת
st.title("📊 ניתוח הוצאות והכנסות")
st.subheader("📌 סיכום פיננסי חודשי")
st.dataframe(final_table)

# גרפים
st.subheader("📉 גרף הוצאות והכנסות לפי חודש - בחר סוג פירוט")
option_plot = st.radio("בחר סוג נתונים:", ['יתרה הכנסות הוצאות', 'הכנסות מול הוצאות'])
include_savings = st.checkbox("כולל חיסכונות", value=True)

if include_savings:
    balance_data_plot = balance
    income_data_plot = income_data.loc['סה"כ הכנסות']
    expense_data_plot = expense_data.loc['סה"כ הוצאות']
    title_suffix = "כולל חיסכונות"
else:
    balance_data_plot = balance_no_savings
    income_data_plot = income_without_savings
    expense_data_plot = expense_without_savings
    title_suffix = "ללא חיסכונות"

fig, ax = plt.subplots()
if option_plot == 'יתרה הכנסות הוצאות':
    bars = balance_data_plot.plot(kind="bar", ax=ax, color=['green' if x >= 0 else 'red' for x in balance_data_plot])
    for bar in ax.patches:
        height = bar.get_height()
        if height != 0:
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:,.0f}₪',
                    ha='center', va='bottom' if height > 0 else 'top', fontsize=7, fontweight='bold')
    ax.set_xlabel(reverse_text('שנה-חודש'))
    ax.set_ylabel("₪")
    ax.set_title(reverse_text(f"{title_suffix} - יתרה חודשית"))
    st.pyplot(fig)
else:
    bars_income = income_data_plot.plot(kind="bar", ax=ax, color='green', width=0.4, position=1, label=reverse_text("הכנסות"))
    bars_expense = expense_data_plot.plot(kind="bar", ax=ax, color='red', width=0.4, position=0, label=reverse_text("הוצאות"))
    for bar in ax.containers[0]:
        height = bar.get_height()
        if height != 0:
            ax.text(bar.get_x() + bar.get_width() / 2, height + (abs(height) * 0.05), f'{height:,.0f}₪',
                    ha='center', va='top', fontsize=6, fontweight='bold')
    for bar in ax.containers[1]:
        height = bar.get_height()
        if height != 0:
            ax.text(bar.get_x() + bar.get_width() / 2, height - (abs(height) * 0.05), f'{height:,.0f}₪',
                    ha='center', va='top', fontsize=6, fontweight='bold')
    ax.set_xlabel(reverse_text('שנה-חודש'))
    ax.set_ylabel("₪")
    ax.set_title(reverse_text(f"{title_suffix} - הכנסות מול הוצאות"))
    ax.legend()
    st.pyplot(fig)

# פירוט עסקאות לפי חודשים ופעולה
st.subheader("🔍 בחר חודש להצגת פירוט העסקאות")
months_only = list(income_data.columns)
months = ["הכל"] + months_only
selected_months = st.multiselect("📅 בחר חודש או חודשים:", months, default=[months[-1]])

if "הכל" in selected_months:
    filtered_months = months_only
else:
    filtered_months = selected_months

st.subheader("📂 בחר סוג פירוט")
option = st.radio("בחר סוג נתונים:", ['הכנסות', 'הוצאות'])

if filtered_months:
    if option == 'הכנסות':
        data = income_data[filtered_months].dropna(how='all')
    else:
        data = expense_data[filtered_months].dropna(how='all')

    st.write(f"📃 רשימת {option} עבור חודשים נבחרים:")
    st.dataframe(data)

    st.subheader("📜 פירוט עסקאות לפי פעולה")
    selected_action = st.selectbox("🔽 בחר פעולה:", data.index)

    transaction_details = summary_df[
        (summary_df['שנה-חודש'].isin(filtered_months)) &
        (summary_df['הפעולה'] == selected_action)
    ]

    if option == 'הכנסות':
        transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'זכות', 'פרטים']]
    else:
        transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'חובה', 'פרטים']]

    if len(filtered_months) == 1:
        month_text = f"בחודש {filtered_months[0]}"
    else:
        month_text = f"בחודשים: {', '.join(filtered_months)}"

    st.write(f"📜 פירוט עסקאות עבור '{selected_action}' {month_text}:")
    st.dataframe(transaction_details_display)
else:
    st.warning("בחר לפחות חודש אחד להצגת נתונים.")
