# Standard library imports
import os
import sys
import asyncio
import logging
import tempfile
import json
import io
# Third-party imports
import dropbox
from dropbox.files import WriteMode
# Internal project imports
from config import DATA_DIR
from utils.logger_manager import CONFIG_PATH

# Dropbox storage path
DROPBOX_STATE_PATH = "/modex/state.json"

# Application state persistence manager
class StateManager:
    def __init__(self, dbx):
        self.dbx = dbx
        self.state = {}

    # Load state from remote storage
    def load(self):
        try:
            _, res = self.dbx.files_download(DROPBOX_STATE_PATH)
            remote_state = json.loads(res.content.decode("utf-8"))

            for k, v in remote_state.items():
                self.state.setdefault(k, v)

            logger.info("Estado carregado do Dropbox")
        except Exception:
            logger.warning("Nenhum estado encontrado, mantendo estado atual")

    # Save current state to remote
    def save(self):
        data = json.dumps(self.state, ensure_ascii=False, indent=2)
        self.dbx.files_upload(
            data.encode("utf-8"),
            DROPBOX_STATE_PATH,
            mode=WriteMode.overwrite,
        )
        logger.info("Estado salvo no Dropbox")

# Logger and client initialization
logger = logging.getLogger(__name__)
_dbx_client = None

# Ensure environment variables are loaded
def ensure_env_loaded():
    try:
        # Check for existing environment variables
        test_var = os.getenv("DROPBOX_REFRESH_TOKEN")
        if not test_var:
            # Load .env from source directory
            from dotenv import load_dotenv
            
            # Locate .env path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(current_dir)
            env_path = os.path.join(src_dir, '.env')
            
            if os.path.exists(env_path):
                load_dotenv(env_path)
                logger.debug(f".env carregado de: {env_path}")
            else:
                load_dotenv()
                logger.debug(".env carregado do diretório atual")
    except ImportError:
        logger.error("python-dotenv não instalado")
        return False
    except Exception as e:
        logger.error(f"Erro ao carregar .env: {e}")
        return False
    return True

# Load credentials
ensure_env_loaded()
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")

# Control variables
backup_enabled = True
sync_interval = 3600

# Singleton Dropbox client getter
def get_dropbox_client():
    global _dbx_client

    if _dbx_client:
        return _dbx_client

    if not all([DROPBOX_REFRESH_TOKEN, DROPBOX_APP_KEY, DROPBOX_APP_SECRET]):
        logger.error("Credenciais Dropbox incompletas")
        return None
    try:
        logger.info("Conectando ao Dropbox (singleton)...")

        _dbx_client = dropbox.Dropbox(
            oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
            app_key=DROPBOX_APP_KEY,
            app_secret=DROPBOX_APP_SECRET,
        )

        _dbx_client.users_get_current_account()
        logger.info("Dropbox conectado com sucesso")
        return _dbx_client

    except Exception as e:
        logger.error(f"Erro ao criar cliente Dropbox: {e}")
        _dbx_client = None
        return None

# Upload local file to Dropbox
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
        # Handle missing directory
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

# Sync multiple files
def sync_all_files(data_dir, config_path=None):
    if not backup_enabled:
        return False
    
    logger.info("Sincronizando com Dropbox...")
    
    files_to_sync = []
    
    # Collect data files
    if os.path.exists(data_dir):
        for file_name in ["modos.json", "idiomas.json"]:
            file_path = os.path.join(data_dir, file_name)
            if os.path.exists(file_path):
                files_to_sync.append((file_path, file_name))
    
    # Collect config files
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

# Setup periodic synchronization task
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

# Periodic state backup task
def create_periodic_state_save(state_manager):
    async def _task():
        while True:
            try:
                state_manager.save()
            except Exception as e:
                logger.error(f"Erro ao salvar estado: {e}")
            await asyncio.sleep(300)
    return _task()

# Script entry point for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Teste Dropbox: ")
    
    # Connection test
    dbx = get_dropbox_client()
    if dbx:
        print("Conexão Dropbox OK")
        try:            
            # Temporary test file
            test_content = b"Teste de backup " + os.urandom(10)
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
                f.write(test_content)
                test_file = f.name
            
            # Upload test
            success = sync_file_to_drive(test_file, "test_backup.txt")
            if success:
                print("Upload de teste OK")
            else:
                print("Upload de teste falhou")
            
            # Cleanup
            os.unlink(test_file)
            
        except Exception as e:
            print(f"Teste adicional falhou: {e}")
    else:
        print("Conexão Dropbox falhou")

# Download missing files from remote
def download_file_if_missing(local_path, remote_path):
    dbx = get_dropbox_client()
    if not dbx:
        return False

    if os.path.exists(local_path):
        logger.info(f"Arquivo já existe localmente: {local_path}")
        return True

    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        _, res = dbx.files_download(remote_path)
        with open(local_path, "wb") as f:
            f.write(res.content)

        logger.info(f"Arquivo baixado do Dropbox: {local_path}")
        return True

    except dropbox.exceptions.ApiError as e:
        logger.warning(f"Arquivo não encontrado no Dropbox: {remote_path}")
        return False

# Initialize project data files
def bootstrap_data_files(data_dir, config_path):
    logger.info("Bootstrap de arquivos iniciado")

    files = [
        (os.path.join(data_dir, "modos.json"), "/bot_backup/modos.json"),
        (os.path.join(data_dir, "idiomas.json"), "/bot_backup/idiomas.json"),
    ]

    if config_path:
        files.append((config_path, "/bot_backup/config_debug.json"))

    for local, remote in files:
        download_file_if_missing(local, remote)
