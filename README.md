# Auto Approve Join Request Bot

यह एक Pyrogram-आधारित Telegram Bot है, जो ग्रुप में आए पेंडिंग Join Requests को Approve या Decline करने में मदद करता है।

## 🔥 फीचर्स

- `.start` – बॉट चालू है या नहीं चेक करें
- `.help` – सभी कमांड्स की जानकारी
- `.ping` – बॉट की गति मापें
- `.approve <limit>` – लिमिट के अनुसार join requests को स्वीकृति दें
- `.decline <limit>` – लिमिट के अनुसार join requests को अस्वीकृत करें
- `.status` – Pending Join Requests की संख्या दिखाएं

---

## ⚙️ आवश्यकताएँ

- Telegram API ID और API HASH  
- Pyrogram String Session  
- एक Telegram User ID (OWNER_ID)

---

## 🛠️ कॉन्फ़िगरेशन (Heroku Config Vars)

| Variable        | Description |
|----------------|-------------|
| `API_ID`       | Telegram API ID |
| `API_HASH`     | Telegram API Hash |
| `OWNER_ID`     | Bot Owner का Telegram User ID |
| `STRING_SESSION` | Pyrogram User String Session |

---

## 🚀 Heroku पर डिप्लॉय करें

नीचे दिए गए बटन पर क्लिक कर के एक क्लिक में डिप्लॉय करें:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Akash8t2/Ak-auto-approve)

> ध्यान दें: आपको ऊपर बताई गई चार वैरिएबल्स Heroku में डालनी होंगी।

---

## ⬇️ Local पर कैसे चलाएं?

1. Dependencies इंस्टॉल करें:
   ```bash
   pip install -r requirements.txt
