import streamlit as st
import requests

# כותרת האפליקציה
st.set_page_config(page_title="AI Agent - Chen", page_icon="🤖")
st.title("ברוך הבא אל הסוכן החכם של עמיחי וחן 🤖")

API_KEY = "enter your key here"
URL = "https://server.iac.ac.il/api/v1/studentapi/responses"

# ניהול היסטוריית השיחה
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת ההודעות הקודמות
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# קלט מהמשתמש
if prompt := st.chat_input("מה תרצו לשאול את הסוכן?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("מחפש תשובה... תנו לו לחשוב! לא להפריע לו בבקשה")

        payload = {
            "model": "gpt-5-nano",
            "input": prompt,
            "instructions": "עני בעברית ברורה ומסוגננת.",
            "tools": [{"type": "web_search"}],  # הפעלת יכולת הסוכן
            "reasoning": {"effort": "low"}
        }
        headers = {"Authorization": f"Bearer {API_KEY}"}

        try:
            response = requests.post(URL, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                final_answer = ""

                # מעבר על כל חלקי התשובה
                for item in result:
                    
                    if isinstance(item, dict) and item.get("type") == "message":
                        content_list = item.get("content", [])
                        for content_block in content_list:
                            # כאן נמצא הטקסט האמיתי שהסוכן כתב
                            if content_block.get("type") == "output_text":
                                final_answer = content_block.get("text")

                # אם מצאנו טקסט, נציג אותו יפה
                if final_answer:
                    message_placeholder.markdown(final_answer)
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})
                else:
                    # גיבוי למקרה שהמבנה שונה
                    message_placeholder.markdown(str(result))
            else:
                message_placeholder.error(f"שגיאת שרת: {response.status_code}")
        except Exception as e:
            message_placeholder.error(f"קרתה שגיאה בקוד: {e}")


        try:
            response = requests.post(URL, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()

                # חילוץ התשובה מתוך שדה ה-output החדש
                final_answer = ""
                output_list = result.get("otput", [])

                for item in output_list:
                    if item.get("type") == "message":
                        for content_item in item.get("content", []):
                            if content_item.get("type") == "output_text":
                                final_answer = content_item.get("text")

                if final_answer:
                    message_placeholder.markdown(final_answer)
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})

                # הצגת המכסה מתוך המקום המדויק ב-JSON ששלחת
                quota = result.get("iac_quota_status", {})
                remaining = quota.get("tokens_used_daily", "0")
                st.caption(f"טוקנים שנוצלו היום: {remaining} מתוך 800,000")
            else:
                st.error(f"שגיאת שרת: {response.status_code}")
        except Exception as e:
            st.error(f"שגיאה בקוד: {e}")
