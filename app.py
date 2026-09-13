import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
import json

app = Flask(__name__)

try:
    gemini_client = genai.Client()
except Exception as e:
    gemini_client = None
    print(f"Lỗi khởi tạo Gemini: {e}. Vui lòng set biến môi trường GEMINI_API_KEY")

def load_accounts():
    config_path = os.path.join(os.path.dirname(__file__), 'accounts.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_account_credentials(target_email):
    accounts = load_accounts()
    
    for acc in accounts:
        if acc.get('email') == target_email:
            return acc.get('email'), acc.get('app_password')
            
    # Fallback: Nếu không tìm thấy hoặc là 'default', lấy tài khoản đầu tiên
    if accounts:
        return accounts[0].get('email'), accounts[0].get('app_password')
        
    # Fallback cuối cùng: Lấy từ biến môi trường
    env_user = os.environ.get('GMAIL_USER')
    env_pass = os.environ.get('GMAIL_APP_PASSWORD')
    if env_user and env_user != "YOUR_GMAIL_ADDRESS@gmail.com":
        return env_user, env_pass
        
    return None, None

def clean_text(text):
    if not text: return ""
    return text.replace('\r', '').replace('\n', ' ').strip()

def decode_mime_header(header_value):
    if not header_value:
        return ""
    decoded_fragments = decode_header(header_value)
    header_text = ""
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            try:
                header_text += fragment.decode(encoding or 'utf-8')
            except:
                header_text += fragment.decode('utf-8', errors='ignore')
        else:
            header_text += str(fragment)
    return header_text

def get_email_body_from_msg(msg):
    text_body = ""
    html_body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" not in content_disposition:
                if content_type == "text/plain" and not text_body:
                    try:
                        text_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except: pass
                elif content_type == "text/html" and not html_body:
                    try:
                        html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except: pass
    else:
        content_type = msg.get_content_type()
        try:
            payload = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            if content_type == "text/html":
                html_body = payload
            else:
                text_body = payload
        except: pass
        
    if not html_body and text_body:
        html_body = f"<pre style='font-family: sans-serif; white-space: pre-wrap; padding: 1rem;'>{text_body}</pre>"
    if not text_body and html_body:
        import re
        text_body = re.sub('<[^<]+>', ' ', html_body) 
        
    return text_body, html_body

def get_gmail_emails(account_email, days_back=0, exact_date_str=None):
    user, password = get_account_credentials(account_email)
    
    if not user or not password or user == "YOUR_GMAIL_ADDRESS@gmail.com":
        raise Exception("Vui lòng cấu hình tài khoản Gmail và App Password trong file accounts.json")
        
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, password)
    mail.select("inbox")
    
    if exact_date_str:
        dt = datetime.strptime(exact_date_str, "%Y-%m-%d")
        date_query = f'ON "{dt.strftime("%d-%b-%Y")}"'
    else:
        target_date = datetime.now() - timedelta(days=days_back)
        date_query = f'SINCE "{target_date.strftime("%d-%b-%Y")}"'
    
    status, messages = mail.search(None, f'({date_query})')
    
    emails = []
    if status == "OK":
        mail_ids = messages[0].split()
        mail_ids.reverse()
        
        for num in mail_ids[:50]:
            status, data = mail.fetch(num, "(RFC822)")
            if status != "OK": continue
                
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject = decode_mime_header(msg.get("Subject"))
                    sender = decode_mime_header(msg.get("From"))
                    if '<' in sender:
                        sender = sender.split('<')[0].strip()
                        
                    text_b, html_b = get_email_body_from_msg(msg)
                    preview = clean_text(text_b)[:100] + "..." if text_b else ""
                    
                    time_str = ""
                    if msg.get("Date"):
                        try:
                            time_obj = email.utils.parsedate_to_datetime(msg.get("Date"))
                            time_str = time_obj.strftime("%H:%M %d/%m")
                        except:
                            time_str = msg.get("Date")[:10]
                    
                    emails.append({
                        "id": num.decode(),
                        "subject": subject,
                        "sender": sender,
                        "time": time_str,
                        "preview": preview
                    })
    mail.logout()
    return emails

def get_email_body_by_id(account_email, entry_id):
    user, password = get_account_credentials(account_email)
    
    if not user or not password:
        raise Exception(f"Lỗi: Không tìm thấy tài khoản {account_email} trong accounts.json")
        
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, password)
    mail.select("inbox")
    
    status, data = mail.fetch(entry_id, "(RFC822)")
    text_b = ""
    html_b = ""
    if status == "OK":
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                text_b, html_b = get_email_body_from_msg(msg)
    mail.logout()
    return text_b, html_b

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/accounts', methods=['GET'])
def fetch_accounts():
    accounts = load_accounts()
    emails = [acc['email'] for acc in accounts]
    # Default to env user if no accounts.json
    if not emails:
        env_user = os.environ.get('GMAIL_USER')
        if env_user and env_user != "YOUR_GMAIL_ADDRESS@gmail.com":
            emails.append(env_user)
    return jsonify({"accounts": emails})

@app.route('/api/emails', methods=['POST'])
def fetch_emails():
    data = request.json
    days = int(data.get('days', 0))
    exact_date = data.get('exact_date')
    account_email = data.get('account', 'default')
    
    try:
        emails = get_gmail_emails(account_email, days, exact_date_str=exact_date)
    except Exception as e:
        return jsonify({"error": str(e)})
    
    if not emails:
        return jsonify({"categories": {"Trống": []}})
        
    if not gemini_client:
        return jsonify({"error": "Chưa cấu hình GEMINI_API_KEY"})

    prompt = "Phân loại danh sách email sau thành các nhóm logic (VD: Học tập, Công việc, Mạng xã hội, Quảng cáo, Khác). Trả về định dạng JSON, key là tên nhóm, value là danh sách các ID của email thuộc nhóm đó. Chỉ trả về JSON hợp lệ, không kèm văn bản khác.\n\nDanh sách email:\n"
    for e in emails:
        prompt += f"ID: {e['id']} | Sender: {e['sender']} | Subject: {e['subject']}\n"
        
    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        category_mapping = json.loads(response.text)
        
        result = {}
        for cat, ids in category_mapping.items():
            result[cat] = [e for e in emails if e['id'] in ids]
            
        return jsonify({"categories": result})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/summarize', methods=['POST'])
def summarize_email():
    entry_id = request.json.get('id')
    account_email = request.json.get('account', 'default')
    
    try:
        text_b, html_b = get_email_body_by_id(account_email, entry_id)
    except Exception as e:
        return jsonify({"error": str(e)})
    
    if not text_b or len(text_b.strip()) == 0:
        return jsonify({"summary": "Email không có nội dung văn bản (có thể là ảnh hoặc HTML phức tạp).", "html_content": html_b})
        
    if not gemini_client:
        return jsonify({"error": "Chưa cấu hình GEMINI_API_KEY", "html_content": html_b})

    prompt = f"Tóm tắt email sau bằng tiếng Việt thật ngắn gọn, tự nhiên, đi thẳng vào vấn đề. Tối đa 3-4 câu. Trình bày dạng bullet points nếu có hành động cần làm:\n\n{text_b[:3000]}"
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        return jsonify({"summary": response.text, "html_content": html_b})
    except Exception as e:
        return jsonify({"error": str(e), "html_content": html_b})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
