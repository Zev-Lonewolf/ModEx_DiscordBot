import os.path
import os
import sys
import smtplib
import ssl
import json 
import time
from flask import Flask, jsonify
from threading import Thread
import asyncio
import logging
import threading
from concurrent import futures 
from email.message import EmailMessage
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from utils.logger_manager import logger
from src.main import bot, app
from src.utils.modos import (
    limpar_mensagens,
    finalizar_modos_em_edicao,
    limpar_modos_usuario,
    limpar_modos_incompletos,
    obter_idioma,
    get_setup_embed,
    enviar_embed
)

load_dotenv() 

# Configurações de caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREDENTIALS_FOLDER = os.path.join(BASE_DIR, 'data')
TOKEN_FILE = os.path.join(CREDENTIALS_FOLDER, 'token.json') 
token_env = os.getenv("TOKEN_JSON")
if token_env:
    os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)
    if not os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            f.write(token_env)

# Variáveis de ambiente
OWNER_EMAIL = os.getenv("OWNER_EMAIL")
FOLDER_ID = os.getenv("FOLDER_ID")
SCOPES = ['https://www.googleapis.com/auth/drive'] 
AUTH_TIMEOUT_SECONDS = 30
CACHE_EXPIRY_SECONDS = 60

# OAuth Pessoal/Aplicativo Instalado
try:
    CLIENT_SECRET_JSON_STRING = os.getenv("DRIVE_CLIENT_SECRET_FILE")
    CLIENT_SECRET_DATA = json.loads(CLIENT_SECRET_JSON_STRING).get('installed', {})
except:
    CLIENT_SECRET_DATA = {}
    
# Service Account (Conta de Serviço)
try:
    SERVICE_ACCOUNT_JSON_STRING = os.getenv("DRIVE_SERVICE_ACCOUNT_FILE")
    SERVICE_ACCOUNT_DATA = json.loads(SERVICE_ACCOUNT_JSON_STRING)
except:
    SERVICE_ACCOUNT_DATA = {}

# Credenciais OAuth
OAUTH_CLIENT_ID = CLIENT_SECRET_DATA.get('client_id')
OAUTH_CLIENT_SECRET = CLIENT_SECRET_DATA.get('client_secret')
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Cache em memória para controle de autenticação
class TemporaryAuthCache:
    def __init__(self):
        self.cache = {
            'global_auth_email_sent': False,
            'first_auth_attempt_time': None,
            'service_account_mode': False,
            'timeout_occurred': False
        }
        self.expiry_time = CACHE_EXPIRY_SECONDS
    
    def set(self, key, value):
        self.cache[key] = value
    
    def get(self, key, default=None):
        return self.cache.get(key, default)
    
    def is_expired(self):
        first_attempt_time = self.cache.get('first_auth_attempt_time')
        if not first_attempt_time:
            return True
        
        elapsed = time.time() - first_attempt_time
        return elapsed > self.expiry_time
    
    def should_attempt_auth(self):
        if not self.cache.get('first_auth_attempt_time'):
            return True
        
        if self.is_expired():
            self.reset_attempt_state()
            return True
        
        if self.cache.get('service_account_mode'):
            return False
        
        return False
    
    def mark_auth_attempt(self):
        self.cache['first_auth_attempt_time'] = time.time()
    
    def reset_attempt_state(self):
        self.cache['first_auth_attempt_time'] = None
        self.cache['timeout_occurred'] = False
    
    def enable_service_account_mode(self):
        self.cache['service_account_mode'] = True
    
    def disable_service_account_mode(self):
        self.cache['service_account_mode'] = False
        self.reset_attempt_state()
    
    def get_status(self):
        return {
            'service_account_mode': self.cache.get('service_account_mode', False),
            'timeout_occurred': self.cache.get('timeout_occurred', False),
            'first_auth_attempted': bool(self.cache.get('first_auth_attempt_time')),
            'cache_expired': self.is_expired(),
            'time_since_last_attempt': time.time() - self.cache.get('first_auth_attempt_time', 0) if self.cache.get('first_auth_attempt_time') else None
        }

auth_cache = TemporaryAuthCache()

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()
    msg = (
        f"Servidor keep-alive iniciado | porta={os.environ.get('PORT', 8080)} | "
        "endpoints=[GET / (status básico), GET /health (health check), GET /ping (ping/pong)]"
    )
    logger.debug(msg)
    print(msg)

# Função que replica o que seu comando setup faz de forma invisível
async def run_setup_periodic():
    await bot.wait_until_ready()
    
    class FakeChannel:
        async def send(self, *args, **kwargs):
            return

    while True:
        for guild in bot.guilds:
            class DummyCtx:
                def __init__(self, guild):
                    self.guild = guild
                    self.author = bot.user
                    self.channel = FakeChannel()  # canal "invisível"
                    self.message = type('msg', (), {'delete': lambda: None})()

            ctx = DummyCtx(guild)
            try:
                limpar_mensagens(ctx.channel, ctx.author, bot.user)
                finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
                limpar_modos_usuario(ctx.guild.id, ctx.author.id)
                limpar_modos_incompletos(ctx.guild.id)
                idioma = obter_idioma(ctx.guild.id)
                embed = get_setup_embed(idioma)
                
                # Envia de forma invisível
                await enviar_embed(ctx.channel, ctx.author.id, embed)
                
                logger.debug(f"[AUTO] setup executado (invisível) no servidor {guild.name} ({guild.id})")
            except Exception as e:
                logger.error(f"Erro ao executar setup automático: {e}")
        
        await asyncio.sleep(600)

# Funções de envio de e-mail
def send_auth_needed_email(recipient_email: str):
    if auth_cache.get('global_auth_email_sent'):
        logger.debug("Email já enviado")
        return
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logger.error("Credenciais ausentes")
        return
    
    logger.critical(f"ALERTA: TOKEN NÃO ENCONTRADO")
    
def send_auth_email(recipient_email: str):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logger.error("Credenciais ausentes")
        return

    msg = EmailMessage()
    msg["Subject"] = "⚠️ Ação Necessária: Autorização do Google Drive Pendente"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg.set_content(
        f"Olá,\n\n"
        "O bot ModEx detectou que não há um token de autenticação válido para o Google Drive.\n\n"
        "Uma janela do navegador foi aberta para você autorizar o acesso. "
        f"Você tem {AUTH_TIMEOUT_SECONDS} segundos para completar a autorização.\n\n"
        "Caso a autorização NÃO seja completada dentro do prazo:\n"
        "1. O bot entrará em modo de hibernação.\n"
        "2. A Service Account será utilizada como fallback.\n"
        "3. Os backups do Google Drive ficarão desativados até o reinício do bot.\n\n"
        "Obrigado,\nEquipe ModEx Bot"
    )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        auth_cache.set('global_auth_email_sent', True)
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail: {e}")


def send_fallback_email(recipient_email: str):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logger.error("Credenciais ausentes")
        return

    logger.critical("ALERTA: Entrando em modo de fallback")

    msg = EmailMessage()
    msg["Subject"] = "🔄 Modo de Hibernação Ativado: Service Account em Uso"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg.set_content(
        f"Olá,\n\n"
        f"O bot ModEx NÃO recebeu autorização dentro dos {AUTH_TIMEOUT_SECONDS} segundos.\n\n"
        "STATUS ATUAL:\n"
        "✅ Bot principal funcionando normalmente\n"
        "✅ Service Account ativada como fallback\n"
        "❌ Backups do Google Drive DESATIVADOS\n\n"
        "Por favor, reinicie o bot após a autorização para retomar os backups normais.\n\n"
        "Obrigado,\nEquipe ModEx Bot"
    )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail de fallback: {e}")

# Autenticação com timeout
class AuthTimeoutError(Exception):
    pass

def run_auth_flow_with_timeout():
    creds = None
    auth_completed = threading.Event()
    auth_error = None
    
    def auth_thread():
        nonlocal creds, auth_error
        try:
            flow = InstalledAppFlow.from_client_config(
                {"installed": CLIENT_SECRET_DATA},
                SCOPES
            )
            creds = flow.run_local_server(port=0)
            auth_completed.set()
        except Exception as e:
            auth_error = e
            auth_completed.set()
    
    thread = threading.Thread(target=auth_thread, daemon=True)
    thread.start()
    
    if auth_completed.wait(timeout=AUTH_TIMEOUT_SECONDS):
        if auth_error:
            raise auth_error
        return creds
    else:
        logger.warning(f"Timeout de {AUTH_TIMEOUT_SECONDS}s atingido")
        raise AuthTimeoutError(f"Timeout de {AUTH_TIMEOUT_SECONDS} segundos")

# Autenticação principal do Google Drive
def google_drive_authenticator():
    creds = None

    if auth_cache.get('service_account_mode'):
        logger.warning("Modo de hibernação ativado")
        try:
            if not SERVICE_ACCOUNT_DATA:
                raise ValueError("Dados da Service Account ausentes")
            
            creds = service_account.Credentials.from_service_account_info(
                SERVICE_ACCOUNT_DATA, 
                scopes=SCOPES
            )
            logger.info("Service Account autenticada")
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            logger.critical(f"Falha na Service Account: {e}")
            return None
    
    # 1. Tenta carregar token existente
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            logger.debug("Token de usuário carregado")
            
            if not creds.expired and auth_cache.get('service_account_mode'):
                auth_cache.disable_service_account_mode()
        except Exception as e:
            logger.warning(f"Falha ao carregar token: {e}")
            creds = None
    
    # 2. Tenta renovar token se expirado
    if creds and creds.expired and creds.refresh_token:
        try:
            if OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET:
                creds.client_id = OAUTH_CLIENT_ID
                creds.client_secret = OAUTH_CLIENT_SECRET
            
            creds.refresh(Request())
            logger.info("Token renovado")
            
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
                
            if auth_cache.get('service_account_mode'):
                auth_cache.disable_service_account_mode()
        except Exception as e:
            logger.warning(f"Falha ao renovar token: {e}")
            creds = None
    
    # 3. Se não tem token válido
    if not creds and CLIENT_SECRET_DATA and auth_cache.should_attempt_auth():
        logger.critical(f"Token ausente. Iniciando fluxo interativo")
        
        auth_cache.mark_auth_attempt()
        
        if not auth_cache.get('global_auth_email_sent'):
            send_auth_needed_email(OWNER_EMAIL)
        
        try:
            creds = run_auth_flow_with_timeout()
            
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            logger.info("Novo token gerado")
            
            auth_cache.reset_attempt_state()
            auth_cache.disable_service_account_mode()
            
        except AuthTimeoutError:
            auth_cache.set('timeout_occurred', True)
            send_fallback_email(OWNER_EMAIL)
            logger.warning("Entrando em modo de hibernação")
            auth_cache.enable_service_account_mode()
            creds = None
            
        except Exception as e:
            logger.warning(f"Erro no fluxo de autenticação: {e}")
            creds = None
    
    # 4. Se está em modo de hibernação, usa Service Account
    if not creds and auth_cache.get('service_account_mode'):
        logger.warning("Usando Service Account como fallback")
        try:
            if not SERVICE_ACCOUNT_DATA:
                raise ValueError("Dados da Service Account ausentes")
            
            creds = service_account.Credentials.from_service_account_info(
                SERVICE_ACCOUNT_DATA, 
                scopes=SCOPES
            )
            logger.info("Service Account autenticada")
        except Exception as e:
            logger.critical(f"Falha na Service Account: {e}")
            return None
    
    # Constrói serviço do Drive
    if creds:
        try:
            service = build('drive', 'v3', credentials=creds)
            if auth_cache.get('service_account_mode'):
                logger.warning("Google Drive em MODO DE HIBERNAÇÃO")
            else:
                logger.info("Google Drive autenticado")
            return service
        except Exception as e:
            logger.error(f'Erro ao construir serviço do Drive: {e}')
            return None
    
    return None

def ensure_file_exists(local_file_path: str):
    if os.path.exists(local_file_path):
        return True
    
    try:
        # Garante que o diretório existe
        directory = os.path.dirname(local_file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Diretório criado: {directory}")
        
        # Cria arquivo JSON vazio
        with open(local_file_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        
        logger.info(f"Arquivo criado: {local_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar arquivo {local_file_path}: {e}")
        return False

def find_file_alternative_paths(filename: str):
    # Lista de caminhos possíveis
    possible_paths = [
        os.path.join(BASE_DIR, 'data', filename),
        os.path.join(BASE_DIR, filename),
        os.path.join('/app', 'data', filename),
        os.path.join('/app', filename),
        os.path.join(os.getcwd(), 'data', filename),
        os.path.join(os.getcwd(), filename),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.debug(f"Arquivo encontrado em caminho alternativo: {path}")
            return path
    
    return None

# Sincronização de arquivos
def sync_file_to_drive(local_file_path: str, drive_file_name: str):
    # Verifica se o arquivo existe no caminho fornecido
    if not os.path.exists(local_file_path):
        logger.warning(f"Arquivo local não encontrado: {local_file_path}")
        
        # Tenta encontrar em caminhos alternativos
        filename = os.path.basename(local_file_path)
        alternative_path = find_file_alternative_paths(filename)
        
        if alternative_path:
            logger.info(f"Usando caminho alternativo: {alternative_path}")
            local_file_path = alternative_path
        else:
            # Tenta criar o arquivo
            logger.info(f"Tentando criar arquivo: {local_file_path}")
            if not ensure_file_exists(local_file_path):
                logger.error(f"Não foi possível criar o arquivo: {local_file_path}")
                return
            logger.info(f"Arquivo criado com sucesso, procedendo com backup")
    
    if auth_cache.get('service_account_mode'):
        if auth_cache.is_expired():
            logger.info("Cache expirado, tentando autenticação normal")
            auth_cache.disable_service_account_mode()
        else:
            logger.critical(f"MODO DE HIBERNAÇÃO - BACKUP BLOQUEADO")
            return
    
    service = google_drive_authenticator()
    if not service:
        return
    
    logger.debug(f"Fazendo backup de '{drive_file_name}'")
    
    try:
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
            file_metadata = {'name': drive_file_name, 'parents': [FOLDER_ID]}
            service.files().create(
                body=file_metadata, 
                media_body=media, 
                fields='id',
                supportsAllDrives=True
            ).execute()
            logger.info(f"Backup criado: {drive_file_name}")
        else:
            file_id = items[0]['id']
            service.files().update(
                fileId=file_id, 
                media_body=media,
                supportsAllDrives=True
            ).execute()
            logger.info(f"Backup atualizado: {drive_file_name}")
            
    except Exception as e:
        error_msg = str(e)
        if 'HttpError 403' in error_msg and 'storage quota' in error_msg:
            logger.critical(f'ERRO 403: Service Account sem cota: {drive_file_name}')
        else:
            logger.error(f'Erro ao sincronizar {drive_file_name}: {e}')

# Funções de controle
def get_auth_status():
    cache_status = auth_cache.get_status()
    return {
        "token_exists": os.path.exists(TOKEN_FILE),
        "timeout_occurred": cache_status['timeout_occurred'],
        "service_account_mode": cache_status['service_account_mode'],
        "first_auth_attempted": cache_status['first_auth_attempted'],
        "cache_expired": cache_status['cache_expired'],
        "backups_blocked": cache_status['service_account_mode'],
        "time_since_last_attempt": cache_status['time_since_last_attempt'],
        "status": "HIBERNAÇÃO" if cache_status['service_account_mode'] else "NORMAL"
    }

def reset_auth_state():
    global auth_cache
    auth_cache = TemporaryAuthCache()
    
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    
    logger.info("Estado de autenticação resetado")
    return True

def force_new_auth():
    auth_cache.reset_attempt_state()
    auth_cache.disable_service_account_mode()
    
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    
    logger.info("Nova autenticação forçada")
    return True

# Inicialização
logger.debug(f"Cache inicial: {auth_cache.get_status()}")
