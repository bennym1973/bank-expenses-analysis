
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# פונקציה להצגת פירוט הכנסות/הוצאות למשתמש
def reverse_text(text):
    if text is not None:
        return text[::-1]

# הגדרת סיסמה לשימוש באפליקציה
PASSWORD = "0544752357"  # שנה את זה לסיסמה שלך

# יצירת תיבת קלט לסיסמה
st.title("🔒 התחברות לאפליקציה")

password_input = st.text_input("📌 הזן סיסמה:", type="password")

if password_input != PASSWORD:
    st.error("❌ סיסמה שגויה! נסה שוב.")
    st.stop()  # מפסיק את הרצת האפליקציה אם הסיסמה שגויה

# אם הסיסמה נכונה, מציגים את האפליקציה הרגילה
st.success("✅ סיסמה נכונה! ברוך הבא לאפליקציה.")

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


###########################################################################
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


# old
# הוספת שורות סכום
# income_data.loc['סה"כ הכנסות'] = income_data.sum()
# expense_data.loc['סה"כ הוצאות'] = expense_data.sum()
# חישוב יתרה חודשית
# balance = income_data.loc['סה"כ הכנסות'] - expense_data.loc['סה"כ הוצאות']
# balance.name = 'יתרה חודשית'

# # חיבור הכל לטבלה אחת
# final_table = pd.concat([income_data, expense_data, balance.to_frame().T])
##################################################################################
# כותרת האפליקציה
st.title("📊 ניתוח הוצאות והכנסות")

# הצגת טבלת סיכום כללית
st.subheader("📌 סיכום פיננסי חודשי")
st.dataframe(final_table)

import streamlit as st
import matplotlib.pyplot as plt

st.subheader("📉 גרף הוצאות והכנסות לפי חודש - בחר סוג פירוט")

# בחירת סוג פירוט
option_plot = st.radio("בחר סוג נתונים:", ['יתרה הכנסות הוצאות', 'הכנסות מול הוצאות'])
include_savings = st.checkbox("כולל חיסכונות", value=True)

# נתוני ההכנסות והוצאות (יש להתאים לנתונים שלך)
if include_savings:
    balance_data_plot = balance  # נתונים כולל חיסכונות
    income_data_plot = income_data.loc['סה"כ הכנסות']#income_with_savings
    expense_data_plot = expense_data.loc['סה"כ הוצאות']
    title_suffix = "כולל חיסכונות"
else:
    balance_data_plot = balance_no_savings  # נתונים ללא חיסכונות
    income_data_plot = income_without_savings
    expense_data_plot = expense_without_savings
    title_suffix = "ללא חיסכונות"

fig, ax = plt.subplots()

if option_plot == 'יתרה הכנסות הוצאות':
    bars = balance_data_plot.plot(kind="bar", ax=ax, color=['green' if x >= 0 else 'red' for x in balance_data_plot])

    # הוספת ערכים על כל עמודה
    for bar in ax.patches:
        height = bar.get_height()  
        if height != 0:  
            ax.text(
                bar.get_x() + bar.get_width() / 2,  
                height,  
                f'{height:,.0f}₪',  
                ha='center',  
                va='bottom' if height > 0 else 'top',  
                fontsize=10, 
                fontweight='bold'
            )

    ax.set_xlabel(reverse_text('שנה-חודש'))
    ax.set_ylabel("₪")
    ax.set_title(reverse_text(f"{title_suffix} - יתרה חודשית"))

    st.pyplot(fig)

# else:  # הכנסות מול הוצאות
#     fig, ax = plt.subplots()
    
#     # גרף עמודות להכנסות והוצאות
#     income_data_plot.plot(kind="bar", ax=ax, color='green', position=1, width=0.4, label=reverse_text("הכנסות"))
#     expense_data_plot.plot(kind="bar", ax=ax, color='red', position=0, width=0.4, label=reverse_text("הוצאות"))
    
#     ax.set_xlabel(reverse_text('שנה-חודש'))
#     ax.set_ylabel("₪")
#     ax.set_title(reverse_text(f"{title_suffix} - הכנסות מול הוצאות"))
#     ax.legend()

#     st.pyplot(fig)
else:  # הכנסות מול הוצאות
    fig, ax = plt.subplots()
    
    # גרף עמודות להכנסות והוצאות
    bars_income = income_data_plot.plot(kind="bar", ax=ax, color='green', width=0.4, position=1, label=reverse_text("הכנסות"))
    bars_expense = expense_data_plot.plot(kind="bar", ax=ax, color='red', width=0.4, position=0, label=reverse_text("הוצאות"))
    
    # הוספת ערכים על כל עמודה (הכנסות)
    for bar in ax.containers[0]:  # מתייחס לעמודות של ההכנסות
        height = bar.get_height()
        if height != 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,  
                height,  
                f'{height:,.0f}₪',  
                ha='center',  
                va='bottom',  
                fontsize=8, 
                fontweight='bold',
                color='black'
            )

    # הוספת ערכים על כל עמודה (הוצאות)
    for bar in ax.containers[1]:  # מתייחס לעמודות של ההוצאות
        height = bar.get_height()
        if height != 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,  
                height,  
                f'{height:,.0f}₪',  
                ha='center',  
                va='bottom',  
                fontsize=10, 
                fontweight='bold',
                color='black'
            )

    ax.set_xlabel(reverse_text('שנה-חודש'))
    ax.set_ylabel("₪")
    ax.set_title(reverse_text(f"{title_suffix} - הכנסות מול הוצאות"))
    ax.legend()

    st.pyplot(fig)



if False:
    # גרף ויזואלי של הכנסות והוצאות לפי חודש
    st.subheader("📉 גרף הוצאות והכנסות לפי חודש")
    #####

    fig, ax = plt.subplots()

    bars = balance_no_savings.plot(kind="bar", ax=ax, color=['green' if x >= 0 else 'red' for x in balance_no_savings])

    # הוספת ערכים על כל עמודה
    for bar in ax.patches:
        height = bar.get_height()  # קבלת גובה העמודה (הערך)
        if height != 0:  # להימנע מהצגת 0
            ax.text(
                bar.get_x() + bar.get_width() / 2,  # מיקום X (אמצע העמודה)
                height,  # מיקום Y (גובה הערך)
                f'{height:,.0f}₪',  # הצגת הערך בפורמט שקל עם פסיקים
                ha='center',  # יישור אופקי למרכז
                va='bottom' if height > 0 else 'top',  # אם שלילי - יופיע מעל העמודה
                fontsize=10, 
                fontweight='bold'
            )

    # כותרות וצירים
    ax.set_xlabel(reverse_text('שנה-חודש'))
    ax.set_ylabel("₪")
    ax.set_title(reverse_text("ללא חיסכונות - יתרה חודשית"))

    st.pyplot(fig)




# בחירת חודש להצגת פירוט עסקאות
if False:
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


# בחירת חודש להצגת פירוט עסקאות
st.subheader("🔍 בחר חודש להצגת פירוט העסקאות")
months = ["הכל"] + list(income_data.columns)
selected_month = st.selectbox("📅 בחר חודש:", months)

# בחירת סוג פירוט
st.subheader("📂 בחר סוג פירוט")
option = st.radio("בחר סוג נתונים:", ['הכנסות', 'הוצאות'])

# קביעת הדאטה להצגה
if option == 'הכנסות':
    data = income_data if selected_month == "הכל" else income_data[[selected_month]].dropna()
else:
    data = expense_data if selected_month == "הכל" else expense_data[[selected_month]].dropna()

st.write(f"📃 רשימת {option} עבור {'כל החודשים' if selected_month == 'הכל' else 'חודש ' + selected_month}:")
st.dataframe(data)

# בחירת פעולה ספציפית
st.subheader("📜 פירוט עסקאות לפי פעולה")
selected_action = st.selectbox("🔽 בחר פעולה:", data.index)

# הצגת פירוט העסקאות עבור הפעולה שנבחרה
if selected_month == "הכל":
    transaction_details = summary_df[summary_df['הפעולה'] == selected_action]
else:
    transaction_details = summary_df[(summary_df['שנה-חודש'] == selected_month) & (summary_df['הפעולה'] == selected_action)]

if option == 'הכנסות':
    transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'זכות', 'פרטים']]
else:
    transaction_details_display = transaction_details[['שנה-חודש', 'הפעולה', 'חובה', 'פרטים']]

st.write(f"📜 פירוט עסקאות עבור '{selected_action}' {'בכל החודשים' if selected_month == 'הכל' else 'בחודש ' + selected_month}:")
st.dataframe(transaction_details_display)