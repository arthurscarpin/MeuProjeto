# Importando modulos das bibliotecas
from flask import Flask, jsonify, request, Response, render_template, redirect, flash, url_for, session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Importando bibliotecas
import cv2
import pyodbc
import smtplib
import random
import string
import re

# Importando outros scripts .py
from backend import VideoCaptura, TesseractOCR

# Construção do Flask
app = Flask(__name__)
app.secret_key = 'A123456'

# Acesso ao banco de dados (SQL SERVER)
dados_conexao = (
    "Driver={SQL Server};"
    "Server=localhost\\SQLEXPRESS01;"
    "Database=PythonSQL;"
    "Trusted_Connection=yes;"
)

# Configurações do servidor de e-mail (GMAIL)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587 

# Redirecionamento de rotas
@app.route('/') # Redirecionamento para a rota /login
def redirecionar_login():
    return redirect('/login')

# Definicao de rotas 
@app.route('/login') # /login
def login():
    return render_template('login.html')

@app.route('/login_cadastro') # /login_cadastro
def login_cadastro():
    return render_template('login_cadastro.html')

@app.route('/login_alterar_senha') # /login_senha
def login_alterar_senha():
    return render_template('login_alterar_senha.html')

@app.route('/login_esqueci_minha_senha') # /login_esqueci_minha_senha
def login_esqueci_minha_senha():
    return render_template('login_esqueci_minha_senha.html')

@app.route('/home') # /home
def home():
    return render_template('home.html')

camera = cv2.VideoCapture(1) # Idice da camera
@app.route('/camera')
def camera():
    return Response(VideoCaptura(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/home_cadastro') # /home_cadastro
def home_cadastro():
    return render_template('home_cadastro.html')

@app.route('/home_cadastro_sucesso') # /home_cadastro_sucesso
def home_cadastro_sucesso():
    return render_template('home_cadastro_sucesso.html')

@app.route('/home_cadastro_erro') # /home_cadastro_erro
def home_cadastro_erro():
    return render_template('home_cadastro_erro.html')

@app.route('/login_alterar_senha_sucesso') # /login_alterar_senha_sucesso
def login_alterar_senha_sucesso():
    return render_template('login_alterar_senha_sucesso.html')

@app.route('/login_alterar_senha_erro') # /login_alterar_senha_erro
def login_alterar_senha_erro():
    return render_template('login_alterar_senha_erro.html')

# Resultados OCR
placas = [] 

@app.route('/contador_placas', methods=['GET'])
def get_contador_placas():
    return jsonify(placas)

@app.route('/contador_placas', methods=['POST'])
def contador_placas():
    if request.is_json:
        data = request.get_json()
        placas.append(data)

def maxId_contador_placas():
    if placas:
        return placas[-1]['id']
    return None

@app.route('/maxid_placa', methods=['GET'])
def maxId_placa():
    ultimo_id = maxId_contador_placas()
    if ultimo_id:
        return jsonify(placas[-1])

# Validacao /login
@app.route('/login', methods=['POST'])
def validacao_login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    try:
        conexao = pyodbc.connect(dados_conexao)
        cursor = conexao.cursor()
        consulta = "SELECT * FROM usuario"
        cursor.execute(consulta)
        usuariosDB = cursor.fetchall()
        autenticado = False
        for usuario in usuariosDB:
            emailNome = str(usuario[3])
            senhaNome = str(usuario[4])
            if emailNome == email and senhaNome == senha:
                autenticado = True
                break
        if autenticado:
            return redirect('/home')
        else:
            flash("Atenção! Dados inválidos, tente novamente")
            return redirect('/')
    except pyodbc.Error as e:
        flash("Erro de conexão com o banco de dados!")
        return redirect('/login')

# Validacao /login_esqueci_minha_senha
def senha_aleatoria(tamanho=12):
    caracteres = string.ascii_letters + string.digits
    senha_aleatoria = ''.join(random.choice(caracteres) for _ in range(tamanho))
    return senha_aleatoria

@app.route('/login_esqueci_minha_senha', methods=['POST'])
def email():   
    smtp_email = 'carvalhoscarpin@gmail.com'
    smtp_senha = 'pzdjpnjtfedybylu'
    email = request.form['email']
    titulo_email = 'Recuperação de Senha'
    try:
        
        # Validaçao de cadastro do e-mail
        conexao = pyodbc.connect(dados_conexao)
        cursor = conexao.cursor()
        consulta = "SELECT * FROM usuario WHERE email = ?"
        cursor.execute(consulta, email)
        usuario = cursor.fetchone()
        if usuario is not None:
            
            # Faz a atualizacao no bando de dados
            nova_senha = senha_aleatoria()
            consulta_atualizar_senha = "UPDATE usuario SET senha = ? WHERE email = ?"
            cursor.execute(consulta_atualizar_senha, nova_senha, email)
            conexao.commit()
            
            # Envia o e-mail
            mensagem = f'Olá,\n\nVocê solicitou a recuperação de senha. Sua nova senha é: {nova_senha}\n\nAtenciosamente,'
            msg = MIMEMultipart()
            msg['From'] = smtp_email
            msg['To'] = email
            msg['Subject'] = titulo_email
            msg.attach(MIMEText(mensagem, 'plain'))
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(smtp_email, smtp_senha)
            server.sendmail(smtp_email, email, msg.as_string())
            server.quit()
            flash("E-mail enviado com sucesso!","sucesso")
            return render_template('login_esqueci_minha_senha.html')
        else:
            flash ("E-mail inválido! Tente novamente", "erro")
            return render_template('login_esqueci_minha_senha.html')       
    except pyodbc.Error as e:
        flash("Erro de conexão com o banco de dados!", "erro")
        return render_template('login_esqueci_minha_senha.html') 
    except Exception as e:
        flash("Erro ao enviar e-mail", "erro")
        return render_template('login_esqueci_minha_senha.html') 

# Validacao /login_cadastro
@app.route('/login_cadastro', methods=['POST'])
def login_cadastro_formulario():
    nome = request.form.get('nome')
    sobrenome = request.form.get('sobrenome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    # Formatação antes de salvar o nome e sobrenome no banco de dados
    nome_formatado = nome.capitalize()
    sobrenome_formatado = sobrenome.capitalize()

    try:
        
        # Validaçao de cadastro do e-mail
        conexao = pyodbc.connect(dados_conexao)
        cursor = conexao.cursor()
        consulta_verificacao = "SELECT COUNT(*) FROM usuario WHERE email = ?"
        cursor.execute(consulta_verificacao, email)
        if cursor.fetchone()[0] > 0:
            flash("O e-mail já possui cadastro","erro")
            return render_template('login_cadastro.html')
        else:
            
            # Realiza a INSERT no banco de dados se o e-mail não possuir cadastro
            comando = "INSERT INTO usuario (nome, sobrenome, email, senha, data_cadastro) VALUES (?, ?, ?, ?, GETDATE())"
            cursor.execute(comando, nome_formatado, sobrenome_formatado, email, senha)
            conexao.commit()
            flash("Cadastro realizado com sucesso.","sucesso")
            return render_template('login_cadastro.html')    
    except pyodbc.Error as e:
        flash("Erro de conexão com o banco de dados!", "erro")
        return render_template('login_cadastro.html')    
    except Exception as e:
        flash("Erro ao inserir informações no banco de dados!", "erro")
        return render_template('login_cadastro.html') 

@app.route('/home_cadastro', methods=['GET', 'POST'])
def cadastro_placa():
    if request.method == 'POST':
        try:
            placa = request.form['placa'].upper()
            status = 1

            # Validação de cadastro da placa
            conexao = pyodbc.connect(dados_conexao)
            cursor = conexao.cursor()
            consulta_verificacao = "SELECT COUNT(*) FROM placa WHERE placa_nome = ?"
            cursor.execute(consulta_verificacao, placa)
            if cursor.fetchone()[0] > 0:

                # Mensagem de erro
                flash("A placa já possui cadastro!", "erro")
                return render_template('home_cadastro_erro.html')

            # Verificação se a placa tem exatamente 7 caracteres alfanuméricos
            if not re.match("^[A-Za-z0-9]{7}$", placa):
                flash("A placa deve conter 7 caracteres alfanuméricos", "erro")
                return render_template('home_cadastro_erro.html')

            # Caso a placa não tenha cadastro e cumpra a validação, insere a placa no banco de dados
            else:
                comando = pyodbc.connect(dados_conexao)
                cursor = comando.cursor()
                query = "INSERT INTO placa (placa_nome, id_status) VALUES (?, ?)"
                cursor.execute(query, placa, status)
                comando.commit()
                cursor.close()
                comando.close()

                # Mensagem de sucesso
                flash("A placa foi cadastrada com sucesso", "sucesso")
                return render_template('home_cadastro_sucesso.html')

        # Exceção banco de dados
        except pyodbc.Error as e:
            flash("Erro de conexão com o banco de dados!", "erro")
            return render_template('home_cadastro.html')

        except Exception as e:
            flash("Erro ao inserir informações no banco de dados!", "erro")
            return render_template('home_cadastro.html')

    return render_template('home_cadastro.html')


# Validacao /tabela_placa - Consultar placa na tabela
@app.route('/tabela_placa', methods=['GET'])
def consulta_placa():
    
    # Pesquisar placa
    pesquisa = request.args.get('pesquisa')

    try:
        # Realiza a consulta da placa no banco de dados
        conn = pyodbc.connect(dados_conexao)
        cursor = conn.cursor()
        consulta = 'SELECT * FROM placa'
        if pesquisa:
            consulta += f" WHERE placa_nome LIKE '%{pesquisa}%'"
        cursor.execute(consulta)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        resultado = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return jsonify(resultado)

    except pyodbc.Error as e:
        return jsonify({"message": "Erro de conexão com o banco de dados."}), 500
    except Exception as e:
        return jsonify({"message": "Erro ao realizar a consulta no banco de dados."}), 500

# Validacao /login_alterar_senha
@app.route('/login_alterar_senha', methods=['POST'])
def atualizacao_login_alterar_senha():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            senha_atual = request.form.get('senha_atual')
            nova_senha = request.form.get('nova_senha')

            # Realiza a consulta da usuario no banco de dados
            comando = pyodbc.connect(dados_conexao)
            cursor = comando.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuario WHERE email = ? AND senha = ?", email, senha_atual)
            exists = cursor.fetchone()[0]

            if exists > 0:
                # Realiza o UPDATE da nova senha no banco de dadis
                cursor.execute("UPDATE usuario SET senha = ? WHERE email = ?", nova_senha, email)
                comando.commit()
                comando.close()

                return jsonify({"success": True, "message": "Senha alterada com sucesso!"}), 200
            else:
                comando.close()
                return jsonify({"success": False, "message": "Erro ao alterar a senha! Tente novamente"}), 400

        # Exceção banco de dados
        except pyodbc.Error as e:
            return jsonify({"success": False, "message": "Erro de conexão com o banco de dados"}), 500

        except Exception as e:
            return jsonify({"success": False, "message": "Erro ao alterar a senha"}), 400

@app.route('/delete/<placa>', methods=['POST'])
def deletar_placa (placa):
    try:
        comando = pyodbc.connect(dados_conexao)
        cursor = comando.cursor()
        query = "DELETE FROM placa WHERE placa_nome = ?"
        cursor.execute(query, placa)
        comando.commit()
        cursor.close()
        comando.close()
        return jsonify({"message": "Placa excluída com sucesso!"}), 200

    except pyodbc.Error as e:
        return jsonify({"message": "Erro de conexão com o banco de dados."}), 500

    except Exception as e:
        return jsonify({"message": "Erro ao o DELETE no banco de dados."}), 500

# Main
if __name__ == "__main__":
    app.run(port=5000, host='localhost', debug=True)
