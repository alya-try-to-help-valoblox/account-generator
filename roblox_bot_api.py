from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import random
import string
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Configuration de la base de données
DB_PATH = 'roblox_accounts.db'

def init_db():
    """Initialiser la base de données"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  password TEXT,
                  birthday TEXT,
                  gender TEXT,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_accounts_count_last_12h():
    """Compter les comptes créés dans les 12 dernières heures"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    twelve_hours_ago = datetime.now() - timedelta(hours=12)
    c.execute('SELECT COUNT(*) FROM accounts WHERE created_at > ?', (twelve_hours_ago,))
    count = c.fetchone()[0]
    conn.close()
    return count

def save_account(username, password, birthday, gender):
    """Sauvegarder un compte dans la base de données"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO accounts (username, password, birthday, gender, created_at) VALUES (?, ?, ?, ?, ?)',
              (username, password, birthday, gender, datetime.now()))
    conn.commit()
    conn.close()

def get_all_accounts():
    """Récupérer tous les comptes"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM accounts ORDER BY created_at DESC')
    accounts = c.fetchall()
    conn.close()
    return accounts

def generate_username():
    """Générer un username aléatoire"""
    adjectives = ['Cool', 'Epic', 'Super', 'Mega', 'Ultra', 'Pro', 'Best', 'Top', 'Awesome', 'Great']
    nouns = ['Gamer', 'Player', 'Master', 'King', 'Legend', 'Hero', 'Champion', 'Star', 'Boss', 'Ninja']
    number = random.randint(1000, 9999)
    return f"{random.choice(adjectives)}{random.choice(nouns)}{number}"

def generate_password():
    """Générer un mot de passe sécurisé"""
    chars = string.ascii_letters + string.digits
    password = ''.join(random.choice(chars) for _ in range(12))
    return password

def generate_birthday():
    """Générer une date de naissance (18+)"""
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    year = random.randint(1990, 2005)
    return month, day, year

def create_roblox_account_api():
    """Créer un compte Roblox via l'API"""
    
    try:
        # Générer les infos
        username = generate_username()
        password = generate_password()
        month, day, year = generate_birthday()
        gender = random.choice([2, 3])  # 2 = Male, 3 = Female
        
        print(f"\n📝 Generated credentials:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Birthday: {month}/{day}/{year}")
        print(f"   Gender: {'Male' if gender == 2 else 'Female'}")
        
        # Préparer les données pour l'API
        signup_data = {
            "username": username,
            "password": password,
            "birthday": f"{year}-{month:02d}-{day:02d}T00:00:00.000Z",
            "gender": gender,
            "isTosAgreementBoxChecked": True,
            "context": "MultiverseSignupForm"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print("\n🚀 Calling Roblox API...")
        
        # Appeler l'API de création de compte
        response = requests.post(
            'https://auth.roblox.com/v2/signup',
            json=signup_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 API Response Status: {response.status_code}")
        print(f"📊 API Response: {response.text[:500]}")
        
        if response.status_code == 200:
            # Succès
            birthday_str = f"{month:02d}/{day:02d}/{year}"
            gender_str = 'Male' if gender == 2 else 'Female'
            
            save_account(username, password, birthday_str, gender_str)
            
            print(f"\n✅ Account created successfully!")
            
            return {
                'success': True,
                'username': username,
                'password': password,
                'birthday': birthday_str,
                'gender': gender_str
            }
        else:
            # Erreur
            error_msg = response.json() if response.text else {'error': 'Unknown error'}
            print(f"\n❌ API Error: {error_msg}")
            
            return {
                'success': False,
                'error': f"API returned {response.status_code}: {error_msg}"
            }
        
    except Exception as e:
        print(f"\n❌ Error in create_roblox_account_api: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def home():
    """Page d'accueil avec l'interface"""
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Roblox Bot</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 { color: #333; margin-bottom: 10px; }
            .subtitle { color: #666; margin-bottom: 30px; }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-box {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }
            .stat-value { font-size: 32px; font-weight: bold; }
            .stat-label { font-size: 14px; opacity: 0.9; }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                margin-bottom: 30px;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(102,126,234,0.4); }
            .btn:disabled { opacity: 0.6; cursor: not-allowed; }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th { background: #f8f9fa; font-weight: 600; }
            .loading { display: none; text-align: center; color: #667eea; margin: 20px 0; }
            .loading.show { display: block; }
            .message {
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: none;
            }
            .message.success { background: #d4edda; color: #155724; display: block; }
            .message.error { background: #f8d7da; color: #721c24; display: block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Roblox Account Bot (API Version)</h1>
            <p class="subtitle">Automated account generation via Roblox API</p>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-value" id="totalAccounts">0</div>
                    <div class="stat-label">Total Accounts</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="last12h">0</div>
                    <div class="stat-label">Last 12 Hours</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="remaining">5</div>
                    <div class="stat-label">Remaining (12h)</div>
                </div>
            </div>

            <div id="message" class="message"></div>
            
            <button class="btn" id="createBtn" onclick="createAccount()">Create Account (API)</button>
            
            <div class="loading" id="loading">Creating account via API...</div>
            
            <h2>Created Accounts</h2>
            <table id="accountsTable">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Password</th>
                        <th>Birthday</th>
                        <th>Gender</th>
                        <th>Created At</th>
                    </tr>
                </thead>
                <tbody id="accountsBody">
                </tbody>
            </table>
        </div>

        <script>
            async function loadStats() {
                const res = await fetch('/stats');
                const data = await res.json();
                document.getElementById('totalAccounts').textContent = data.total;
                document.getElementById('last12h').textContent = data.last_12h;
                document.getElementById('remaining').textContent = Math.max(0, 5 - data.last_12h);
                
                if (data.last_12h >= 5) {
                    document.getElementById('createBtn').disabled = true;
                }
            }

            async function loadAccounts() {
                const res = await fetch('/accounts');
                const accounts = await res.json();
                const tbody = document.getElementById('accountsBody');
                tbody.innerHTML = accounts.map(acc => `
                    <tr>
                        <td>${acc.username}</td>
                        <td>${acc.password}</td>
                        <td>${acc.birthday}</td>
                        <td>${acc.gender}</td>
                        <td>${new Date(acc.created_at).toLocaleString()}</td>
                    </tr>
                `).join('');
            }

            async function createAccount() {
                const btn = document.getElementById('createBtn');
                const loading = document.getElementById('loading');
                const message = document.getElementById('message');
                
                btn.disabled = true;
                loading.classList.add('show');
                message.style.display = 'none';
                
                const res = await fetch('/create', { method: 'POST' });
                const data = await res.json();
                
                loading.classList.remove('show');
                btn.disabled = false;
                
                if (data.success) {
                    message.className = 'message success';
                    message.textContent = `Account created: ${data.username}`;
                    loadStats();
                    loadAccounts();
                } else {
                    message.className = 'message error';
                    message.textContent = data.error || 'Error creating account';
                }
            }

            loadStats();
            loadAccounts();
            setInterval(loadStats, 30000);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/stats')
def stats():
    """Statistiques"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM accounts')
    total = c.fetchone()[0]
    conn.close()
    
    last_12h = get_accounts_count_last_12h()
    
    return jsonify({
        'total': total,
        'last_12h': last_12h,
        'remaining': max(0, 5 - last_12h)
    })

@app.route('/accounts')
def accounts():
    """Liste des comptes"""
    accounts = get_all_accounts()
    return jsonify([{
        'username': acc[1],
        'password': acc[2],
        'birthday': acc[3],
        'gender': acc[4],
        'created_at': acc[5]
    } for acc in accounts])

@app.route('/create', methods=['POST'])
def create():
    """Créer un compte"""
    try:
        # Vérifier la limite
        count = get_accounts_count_last_12h()
        if count >= 5:
            return jsonify({
                'success': False,
                'error': 'Limit reached: 5 accounts per 12 hours'
            }), 429
        
        print("\n🚀 Starting account creation via API...")
        
        # Créer le compte
        result = create_roblox_account_api()
        
        print(f"\n📊 Result: {result}")
        
        return jsonify(result)
    except Exception as e:
        print(f"\n❌ ERROR in /create endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
