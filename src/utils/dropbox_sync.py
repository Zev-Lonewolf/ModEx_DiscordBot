import os
import sys
import dropbox
import asyncio
import logging
import tempfile
from config import DATA_DIR
from utils.logger_manager import CONFIG_PATH

logger = logging.getLogger(__name__)

def ensure_env_loaded():
    try:
        # Tenta ler qualquer variável do .env
        test_var = os.getenv("TOKEN")
        if not test_var:
            # Se não tem, carrega o .env de src/
            from dotenv import load_dotenv
            
            # Encontra o caminho para src/.env
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(current_dir)
            env_path = os.path.join(src_dir, '.env')
            
            if os.path.exists(env_path):
                load_dotenv(env_path)
                logger.debug(f".env carregado de: {env_path}")
            else:
                # Fallback
                load_dotenv()
                logger.debug(".env carregado do diretório atual")
    except ImportError:
        logger.error("python-dotenv não instalado")
        return False
    except Exception as e:
        logger.error(f"Erro ao carregar .env: {e}")
        return False
    return True

# Garante que o .env está carregado
ensure_env_loaded()
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

if DROPBOX_ACCESS_TOKEN:
    logger.debug(f"Token length: {len(DROPBOX_ACCESS_TOKEN)}")
    if DROPBOX_ACCESS_TOKEN.startswith('sl.'):
        logger.debug("Formato correto (starts with 'sl.')")

# Variáveis de controle
backup_enabled = True
sync_interval = 3600

def get_dropbox_client():
    if not DROPBOX_ACCESS_TOKEN:
        logger.error("DROPBOX_ACCESS_TOKEN não encontrado")
        logger.error("Verifique se o arquivo src/.env contém: DROPBOX_ACCESS_TOKEN=seu_token")
        return None
    
    try:
        token_clean = DROPBOX_ACCESS_TOKEN.strip()
        logger.info("Conectando ao Dropbox...")
        dbx = dropbox.Dropbox(token_clean)
        
        # Testa conexão
        account = dbx.users_get_current_account()
        logger.info(f"Conectado ao Dropbox como: {account.name.display_name}")
        return dbx
        
    except dropbox.exceptions.AuthError as e:
        logger.error(f"Erro de autenticação: {e}")
        logger.error("Token pode estar expirado. Gere um novo em: https://www.dropbox.com/developers/apps")
        return None
    except Exception as e:
        logger.error(f"Erro: {e}")
        return None

def sync_file_to_drive(local_path, remote_filename):
    if not backup_enabled:
        return False
    
    dbx = get_dropbox_client()
    if not dbx:
        return False
    
    try:
        if not os.path.exists(local_path):
            logger.error(f"Arquivo não existe: {local_path}")
            return False
        
        remote_path = f"/bot_backup/{remote_filename}"
        
        with open(local_path, 'rb') as f:
            file_data = f.read()
        
        dbx.files_upload(
            file_data,
            remote_path,
            mode=dropbox.files.WriteMode.overwrite
        )
        
        logger.info(f"{remote_filename} sincronizado")
        return True
        
    except dropbox.exceptions.ApiError as e:
        if e.error.is_path() and e.error.get_path().is_not_found():
            try:
                dbx.files_create_folder_v2("/bot_backup")
                logger.info("Pasta /bot_backup criada")
                return sync_file_to_drive(local_path, remote_filename)
            except Exception as create_error:
                logger.error(f"Erro ao criar pasta: {create_error}")
                return False
        else:
            logger.error(f"Erro API: {e}")
            return False
    except Exception as e:
        logger.error(f"Erro: {e}")
        return False

def sync_all_files(data_dir, config_path=None):
    if not backup_enabled:
        return False
    
    logger.info("Sincronizando com Dropbox...")
    
    files_to_sync = []
    
    if os.path.exists(data_dir):
        for file_name in ["modos.json", "idiomas.json"]:
            file_path = os.path.join(data_dir, file_name)
            if os.path.exists(file_path):
                files_to_sync.append((file_path, file_name))
    
    if config_path and os.path.exists(config_path):
        files_to_sync.append((config_path, "config_debug.json"))
    
    if not files_to_sync:
        logger.warning("Nenhum arquivo para sincronizar")
        return False
    
    success_count = 0
    for local_path, remote_name in files_to_sync:
        if sync_file_to_drive(local_path, remote_name):
            success_count += 1
    
    total = len(files_to_sync)
    if success_count == total:
        logger.info(f"Sincronizado: {success_count}/{total} arquivos")
        return True
    elif success_count > 0:
        logger.warning(f"Parcial: {success_count}/{total} arquivos")
        return False
    else:
        logger.error(f"Falhou: 0/{total} arquivos")
        return False

def keep_alive():
    pass

def run_setup_periodic():    
    async def periodic_sync():
        logger.info("Tarefa Dropbox iniciada")
        
        await asyncio.sleep(60)
        while True:
            try:
                logger.info("Sincronização periódica...")
                success = sync_all_files(DATA_DIR, CONFIG_PATH)
                
                if success:
                    logger.info("Sincronização completa")
                else:
                    logger.warning("Sincronização falhou")
                
                await asyncio.sleep(sync_interval)
                
            except Exception as e:
                logger.error(f"Erro: {e}")
                await asyncio.sleep(300)
    return periodic_sync()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Teste Dropbox: ")
    
    # Testa conexão
    dbx = get_dropbox_client()
    if dbx:
        print("Conexão Dropbox OK")
        try:            
            # Cria arquivo de teste
            test_content = b"Teste de backup " + os.urandom(10)
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
                f.write(test_content)
                test_file = f.name
            
            # Tenta upload
            success = sync_file_to_drive(test_file, "test_backup.txt")
            if success:
                print("Upload de teste OK")
            else:
                print("Upload de teste falhou")
            
            # Limpa
            os.unlink(test_file)
            
        except Exception as e:
            print(f"Teste adicional falhou: {e}")
    else:
        print("Conexão Dropbox falhou")
