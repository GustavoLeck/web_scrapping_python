import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Mensagem e envio com anexo
mensagem = "Estou enviando meu currículo com interesse em oportunidades na área de Desenvolvimento ou TI em geral. Acredito que minhas habilidades e minha experiência em possam agregar valor à sua equipe, mesmo que não haja uma posição aberta no momento.\nCaso surjam oportunidades que se alinhem ao meu perfil, ficarei feliz em fazer parte de sua equipe.\nAgradeço pela atenção!\n\nAtenciosamente,\nGustavo Alexsander Leck\n\nTelefone: (47) 9 99216-1096"
sendEmail(
    "gustavoalexsanderleck@gmail.com",
    "enkb axze jknv etrj",
    "gugaleck@gmail.com",
    "Oportunidade de Contratação",
    mensagem,
    "./curriculo/Curriculo - Gustavo Alexsander Leck.pdf"  # Substitua pelo caminho do arquivo
)
