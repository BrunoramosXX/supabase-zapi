import logging
from typing import Any, Dict, List

from dotenv import load_dotenv

from services.supabase_service import SupabaseService
from services.zapi_service import ZApiService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main() -> None:
    logger.info("Iniciando processamento de envio de mensagens.")
    
    load_dotenv()
    
    try:
        supabase_service = SupabaseService()
        zapi_service = ZApiService()
        
        contacts: List[Dict[str, Any]] = supabase_service.get_contacts(limit=3)
        
        if not contacts:
            logger.info("A fila de contatos está vazia ou não pôde ser lida.")
            return

        for contact in contacts:
            contact_name: str = str(contact.get("nome") or "Contato").strip()
            contact_phone: str = contact.get("telefone", "")
            
            if not contact_phone:
                logger.warning("Contato '%s' sem número de telefone. Ignorando.", contact_name)
                continue
                
            message: str = f"Olá, {contact_name} tudo bem com você?"
            
            try:
                zapi_service.send_message(phone=contact_phone, message=message)
            except Exception as e:
                logger.error("Falha ao enviar mensagem para '%s': %s", contact_name, e)
            
    except Exception as e:
        logger.error("Erro durante a execução: %s", e)
    finally:
        logger.info("Processamento finalizado.")

if __name__ == "__main__":
    main()
