import os.path
import os
import sys
import smtplib
import ssl
import json 
from email.message import EmailMessage
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from utils.logger_manager import logger

load_dotenv() 

GLOBAL_AUTH_EMAIL_SENT = False 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREDENTIALS_FOLDER = os.path.join(BASE_DIR, 'data')
TOKEN_FILE = os.path.join(CREDENTIALS_FOLDER, 'token.json') 
OWNER_EMAIL = os.getenv("OWNER_EMAIL")
FOLDER_ID = os.getenv("FOLDER_ID")
SCOPES = ['https://www.googleapis.com/auth/drive'] 

# 1. OAuth Pessoal/Aplicativo Instalado
try:
    CLIENT_SECRET_JSON_STRING = os.getenv("DRIVE_CLIENT_SECRET_FILE")
    CLIENT_SECRET_DATA = json.loads(CLIENT_SECRET_JSON_STRING).get('installed', {})
except:
    CLIENT_SECRET_DATA = {}
    
# 2. Service Account (Conta de Serviço)
try:
    SERVICE_ACCOUNT_JSON_STRING = os.getenv("DRIVE_SERVICE_ACCOUNT_FILE")
    SERVICE_ACCOUNT_DATA = json.loads(SERVICE_ACCOUNT_JSON_STRING)
except:
    SERVICE_ACCOUNT_DATA = {}

# Extrai Client ID e Secret para o Refresh Token (se o fluxo for o de usuário)
OAUTH_CLIENT_ID = CLIENT_SECRET_DATA.get('client_id')
OAUTH_CLIENT_SECRET = CLIENT_SECRET_DATA.get('client_secret')
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# FUNÇÃO DE ENVIO DE E-MAIL
def send_auth_needed_email(recipient_email: str):
    global GLOBAL_AUTH_EMAIL_SENT 

    if GLOBAL_AUTH_EMAIL_SENT:
        return

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logger.error("Credenciais SENDER_EMAIL/SENDER_PASSWORD ausentes no .env.")
        return

    logger.critical(f"ALERTA: TODAS AS AUTENTICAÇÕES FALHARAM. Notificando {recipient_email}.")
    
    msg = EmailMessage()
    msg["Subject"] = "⚠️ Alerta Crítico: Falha de Autenticação no Google Drive"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg.set_content(
        "Não foi possível renovar o token de autenticação do usuário (token.json) e a autenticação da Service Account também falhou.\n"
        "\n"
        "Como resultado, o processo de backup não pôde ser concluído.\n"
        "\n"
        "Ação necessária:\n"
        "- Verifique as permissões configuradas para a Service Account; ou\n"
        "- Gere manualmente um novo 'token.json' via navegador.\n"
        "\n"
        "Assim que uma das ações for realizada, o backup poderá ser executado normalmente."
    )
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        logger.warning(f"E-mail de ALERTA FINAL enviado com sucesso para {recipient_email}.")
        GLOBAL_AUTH_EMAIL_SENT = True 
        
    except smtplib.SMTPAuthenticationError:
        logger.error(f"Erro de Autenticação SMTP. Verifique se a 'App Password' foi usada corretamente para {SENDER_EMAIL}.")
    except Exception as e:
        logger.error(f"Falha crítica ao enviar e-mail: {e}")

# FUNÇÃO PRINCIPAL: AUTENTICAÇÃO
def google_drive_authenticator():
    creds = None
    
    # 1. Tenta carregar token de usuário existente
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        logger.debug("Token de usuário carregado.")
        
        # 2. Tenta renovar o token se expirado e válido
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    # Injeta Client ID e Secret para o refresh funcionar
                    creds.client_id = OAUTH_CLIENT_ID
                    creds.client_secret = OAUTH_CLIENT_SECRET
                    creds.refresh(Request())
                    logger.info("Google Drive token renovado com sucesso (silencioso).")
                    
                    # Salva o novo token/refresh token
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                    
                except Exception as e:
                    logger.warning(f"Falha ao renovar token silenciosamente: {e}. Prosseguindo para fallback.")
                    creds = None
            else:
                logger.warning("Token de usuário inválido e sem refresh token. Prosseguindo para fallback.")
                creds = None

    # Se token não existe ou falhou na renovação, tenta Service Account
    if not creds:
        logger.warning("Iniciando fallback para Service Account (100% em segundo plano).")
        try:
            if not SERVICE_ACCOUNT_DATA:
                raise ValueError("Dados da Conta de Serviço ausentes ou inválidos no .env.")

            # Cria credenciais a partir dos dados JSON líquidos
            creds = service_account.Credentials.from_service_account_info(
                SERVICE_ACCOUNT_DATA, 
                scopes=SCOPES
            )
            logger.info("Autenticação por Service Account bem-sucedida.")
            # Service Account não usa token.json.
            
        except Exception as e:
            # Se Service Account falhar, é a última alternativa
            logger.critical(f"Falha na autenticação da Conta de Serviço (Fallback): {e}")
            send_auth_needed_email(OWNER_EMAIL)
            return None

    # 3. Constrói o serviço do Drive
    try:
        service = build('drive', 'v3',credentials=creds)
        logger.info("Google Drive authentication successful!")
        return service
    except Exception as e:
        logger.error(f'Erro ao construir o serviço do Drive: {e}')
        return None

# FUNÇÃO DE SINCRONIZAÇÃO (CHAMADA PRINCIPAL)
def sync_file_to_drive(local_file_path: str, drive_file_name: str):
    if not os.path.exists(local_file_path):
        logger.error(f"Arquivo local não encontrado para backup: {local_file_path}")
        return

    service = google_drive_authenticator()
    if not service:
        return

    try:
        logger.debug(f"Buscando arquivo '{drive_file_name}' no Drive...")

        query = f"name = '{drive_file_name}' and '{FOLDER_ID}' in parents and trashed = false"
        
        results = service.files().list(
            q=query, 
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True 
        ).execute()
        items = results.get('files', [])

        media = MediaFileUpload(local_file_path, mimetype='application/json')

        if not items:
            # --- CRIAR ---
            file_metadata = {'name': drive_file_name, 'parents': [FOLDER_ID]}
            service.files().create(
                body=file_metadata, 
                media_body=media, 
                fields='id',
                supportsAllDrives=True 
            ).execute()
            logger.info(f"Novo backup criado: {drive_file_name}")
        else:
            # --- ATUALIZAR ---
            file_id = items[0]['id']
            service.files().update(
                fileId=file_id, 
                media_body=media,
                supportsAllDrives=True
            ).execute()
            logger.info(f"Backup atualizado: {drive_file_name}")

    except Exception as e:
        logger.error(f'Erro ao sincronizar {drive_file_name} com o Drive: {e}')
