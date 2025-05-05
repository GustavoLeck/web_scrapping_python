import os
from bs4 import BeautifulSoup
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time

def lerArquivo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            conteudo = arquivo.read()
        return conteudo
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")

def extrairCnpj(conteudo_html):
    try:
        soup = BeautifulSoup(conteudo_html, 'html.parser')
        spans = soup.find_all('span')
        # print([span.get_text(strip=True) for span in spans])
        cnpjList = []
        for span in spans:
            spanFormatted = span.get_text(strip=True)
            if len(spanFormatted) == 18 and spanFormatted[2] == '.' and spanFormatted[6] == '.' and spanFormatted[10] == '/' and spanFormatted[15] == '-' and cnpjList.count(spanFormatted) == 0:
                cnpjList.append(span.get_text(strip=True))
        return cnpjList
    except Exception as e:
        print(f"Erro ao extrair spans: {e}")
        return []

def saveJson(value, fileDirectory):
    if os.path.exists(fileDirectory):
        os.remove(fileDirectory)
    try:
        with open(fileDirectory, 'w', encoding='utf-8') as file:
            json.dump(value, file, ensure_ascii=False, indent=4)
            return
    except Exception as e:
        print(f"Erro ao salvar value em JSON: {e}")

def fetchCNpj(cnpj):
    try:
        headers = {
            "Authorization": "Bearer YOUR_API_TOKEN",
            "Content-Type": "application/json",
            "access-token": "0195a563-4efb-77fb-b4b4-ad11e730912a"
        }
        body = {
            "cnpj": cnpj
        }
        response = requests.post(f"https://extensao.zplugin.com/api/ConsultCnpj", headers=headers, json=body)
        return response.json()
    except Exception as e:
        print(f"Erro ao acessar API para o CNPJ {cnpj}: {e}")
        return e

def sendEmail(sender_email, sender_password, recipient_email, subject, body, attachment_path=None):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Add attachment if provided
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment_path.split("/")[-1]}'
            )
            msg.attach(part)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("Email envido com sucesso para : "+recipient_email)
    except Exception as e:
        print("Erro ao enviar email para : "+recipient_email)
        print(f"Failed to send email: {e}")



# ------------------------------------------------------------------------------------------------------------

pasta = './arquivo/'
cnpjListAll = []
for nome_arquivo in os.listdir(pasta):
    if nome_arquivo.endswith('.html'):
        caminho_completo = os.path.join(pasta, nome_arquivo)
        print(f'    => Processando arquivo: {caminho_completo}')
        fileValue = lerArquivo(caminho_completo)
        print(f'Gerando lista CNPJ...')
        cnpjList = extrairCnpj(fileValue)
        print(f'Adicionando CNPJs a lista geral...')
        for cnpj in cnpjList:
            if cnpjListAll.count(cnpj) == 0: 
                cnpjListAll.append(cnpj)
        print(f'Arquivo {nome_arquivo} processado.')
saveJson(cnpjListAll, './cnpjList.json')

value = lerArquivo('cnpjList.json')
print(f'    => Lista de CNPJ gerada.')
print(f'    => Iniciando consultas de CNPJ...')
cnpjList = json.loads(value)
entrepriseList = []
for cnpj in cnpjList:
    print(f'Consultando CNPJ: {cnpj}')
    responseCnpj = fetchCNpj(cnpj)
    if responseCnpj['email'] != "" and responseCnpj['email'] != None and cnpjList.count(responseCnpj['email']) == 0:
        listEmail = [];
        email = responseCnpj['email'].split('@')
 
        listEmail.append(responseCnpj['email'])
        if email[1] != "gmail.com" and email[1] != "hotmail.com" and email[1] != "outlook.com" and email[1] != "yahoo.com.br":
            emailRh = "rh@" + email[1]
            emailTi = "ti@" + email[1]
            listEmail.append(emailRh)
            listEmail.append(emailTi)
        enterprise = {"enterprise": responseCnpj['nome'],"cnpj": cnpj,"emails": listEmail}
        entrepriseList.append(enterprise)
saveJson(entrepriseList, './cnpjListEmail.json')

listEmail = lerArquivo('./cnpjListEmail.json')
listEmailJson = json.loads(listEmail)
count = 0
for item in listEmailJson:
    for email in item['emails']:
            count += 1
print(f'    => Lista de empresas gerada.')
print(f'    => Total de emails encontrados: {count}')
print(f'    => Iniciando envio de e-mails...')

mensagem = "Estou enviando meu currículo com interesse em oportunidades na área de Desenvolvimento ou TI em geral. Acredito que minhas habilidades e minha experiência em possam agregar valor à sua equipe, mesmo que não haja uma posição aberta no momento.\nCaso surjam oportunidades que se alinhem ao meu perfil, ficarei feliz em fazer parte de sua equipe.\nAgradeço pela atenção!\n\nAtenciosamente,\nGustavo Alexsander Leck\n\nTelefone: (47) 9 99216-1096"
for item in listEmailJson:
    for email in item['emails']:
        sendEmail(
        "gustavoalexsanderleck@gmail.com",
        "enkb axze jknv etrj",
        email,
        "Oportunidade de Contratação",
        mensagem,
        "./curriculo/Curriculo - Gustavo Alexsander Leck.pdf"  # Substitua pelo caminho do arquivo
    )   
    print(f'-----------------------------------------------------------------------------------------')
    time.sleep(10)
print(f'    => Envio de e-mails finalizado.')
print(f'    => Processo finalizado.')