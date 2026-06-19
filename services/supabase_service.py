import os
import logging
from typing import Any, Dict, List

from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseService:
    """
    Serviço responsável pela comunicação com o banco de dados Supabase.
    """

    def __init__(self) -> None:
        self.url: str | None = os.getenv("SUPABASE_URL")
        self.key: str | None = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError(
                "As credenciais SUPABASE_URL e SUPABASE_KEY "
                "devem ser configuradas no ambiente."
            )
            
        try:
            self.client: Client = create_client(self.url, self.key)
        except Exception as e:
            logger.error("Falha ao inicializar o cliente Supabase.")
            raise ConnectionError(f"Erro ao conectar ao Supabase: {e}") from e

    def get_contacts(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Recupera os registros da tabela 'contatos'.
        
        Args:
            limit (int): Quantidade máxima de contatos a serem recuperados.
            
        Returns:
            List[Dict[str, Any]]: Lista contendo os dados dos contatos encontrados.
        """
        logger.info("Solicitando dados de contatos no Supabase (limite: %d).", limit)
        try:
            response = self.client.table("contatos").select("*").limit(limit).execute()
            contacts: List[Dict[str, Any]] = response.data
            
            logger.info("Consulta realizada. Total de registros: %d.", len(contacts))
            return contacts
            
        except Exception as e:
            logger.error("Falha ao consultar a tabela 'contatos' no Supabase: %s", e)
            return []
