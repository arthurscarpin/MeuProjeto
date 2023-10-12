# Importando modulos das bibliotecas
from flask import Flask, jsonify, request, Response, render_template, redirect, flash, url_for, session
from datetime import datetime

# Importando bibliotecas
import cv2
import os
import pytesseract
import requests
import pyodbc

# Caminho local do Tesseract
tesseract_path = r"C:\Users\admin\Documents\Faculdade\Sistemas de Informação\TCC\MeuProjeto\Tesseract-OCR"
os.environ["PATH"] += os.pathsep + tesseract_path

# Captura da câmera
camera = cv2.VideoCapture(1)

# Contador de resultados
contador = 0

# Pre Processamento da imagem
def pre_processamento(imagem):
    # Realiza o corte da imagem de acordo com as dimensões especificadas
    imagem_cortada = imagem[300:, 100:550]

    # Converte a imagem para escala de cinza
    gray = cv2.cvtColor(imagem_cortada, cv2.COLOR_BGR2GRAY)

    # Aplique a equalização do histograma para melhorar o contraste
    gray_equalized = cv2.equalizeHist(gray)

    # Realize a binarização adaptativa
    _, binary = cv2.threshold(gray_equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Realiza o desfoque da imagem
    desfoque = cv2.GaussianBlur(binary, (5, 5), 0)

    # Encontra e aproxima os contornos da imagem desfocada
    contornos, _ = cv2.findContours(desfoque, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Faz a identificação dos contornos e retorna a imagem com os retângulos
    imagem_com_retangulos, placa = ContornoImagem(contornos, imagem_cortada)

    if placa is not None:
        # Converte a imagem para escala de cinza
        gray_recorte = cv2.cvtColor(placa, cv2.COLOR_BGR2GRAY)

        # Aplique a equalização do histograma para melhorar o contraste
        gray_recorte_equalized = cv2.equalizeHist(gray_recorte)

        # Realize a binarização adaptativa usando a técnica Otsu
        _, binary_recorte = cv2.threshold(gray_recorte_equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Realiza o desfoque da imagem
        desfoque_recorte = cv2.GaussianBlur(binary_recorte, (5, 5), 0)

        # Encontra e aproxima os contornos da imagem desfocada
        contornos_recorte, _ = cv2.findContours(desfoque_recorte, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
        # Chama a função (ContornoImagem)
        imagem_recorte_retangulos, desfoque_recorte = ContornoImagem(contornos_recorte, desfoque_recorte)

        # Chama a função (TesseractOCR)
        array_console = TesseractOCR(imagem_recorte_retangulos)

    return imagem_com_retangulos, placa

def TesseractOCR(imagem):
    # Contador
    global contador

    # Configuração para melhorar a precisão do OCR
    config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6'

    # Configuração de linguagem do Tesseract
    console = pytesseract.image_to_string(imagem, lang='eng', config=config)

    # Filtro dos caracteres retornados
    console = console.replace(" ", "").replace("\n", "").replace("\r", "")

    # Armazena a data e horário do resultado do OCR
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    if console.strip() and len(console.strip()) == 7:
        contador += 1

        id_placa = int(contador)

        # Consultar o banco de dados para obter o id_status associado à placa
        id_status = obter_id_status_da_placa(console)

        resultado = {  
            'id': id_placa,
            'Placa': console,
            'Data Hora': data_hora,
            'id_status': id_status
        }

        # Enviar a requisição POST para a API
        url = "http://localhost:5000/contador_placas"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=resultado, headers=headers)

        # Verificar o status da resposta
        if response.status_code == 201:
            print("Placa adicionada com sucesso!")
        else:
            print("Erro ao adicionar a placa. Certifique-se de que os dados JSON estão corretos.")

    else:
        resultado = {}

    return resultado

def obter_id_status_da_placa(placa):
    try:
        # Configuração do banco de dados SQL Server
        dados_conexao = (
            "Driver={SQL Server};"
            "Server=localhost\\SQLEXPRESS01;"
            "Database=PythonSQL;"
            "Trusted_Connection=yes;"
        )

        # Conectar ao banco de dados
        conexao = pyodbc.connect(dados_conexao)
        cursor = conexao.cursor()

        # Consulta para obter o id_status associado à placa
        query = "SELECT id_status FROM placa WHERE placa_nome = ?"
        cursor.execute(query, placa)
        row = cursor.fetchone()

        # Fechar a conexão
        cursor.close()
        conexao.close()

        # Se a consulta retornou algum resultado, retornar o id_status encontrado, caso contrário, retornar None
        if row:
            return row[0]
        else:
            return None

    except pyodbc.Error as e:
        # Lida com possíveis erros de conexão com o banco de dados
        print("Erro ao acessar o banco de dados:", e)
        return None

    except Exception as e:
        # Lida com possíveis erros desconhecidos
        print("Erro desconhecido:", e)
        return None

# Contorno das imagens
def ContornoImagem(contornos, imagem):
    placa = None
    for c in contornos:

        # Procura somente contornos fechados
        perimetro = cv2.arcLength(c, True)
        if perimetro > 120:

            # Faz a aproximação dos contornos
            area = cv2.approxPolyDP(c, 0.03 * perimetro, True)

            # Faz a validação geométrica encontrando os retângulos
            if len(area) == 4:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(imagem, (x, y), (x + w, y + h), (0, 255, 0), 2)
                placa = imagem[y:y + h, x:x + w]

    return imagem, placa

# Captura dos frames
def VideoCaptura():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Realiza o pré-processamento da imagem e o OCR
            imagem_com_retangulos, placa = pre_processamento(frame)
            if placa is not None:
                resultado_ocr = TesseractOCR(placa)

            ret, buffer = cv2.imencode('.jpg', imagem_com_retangulos)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
