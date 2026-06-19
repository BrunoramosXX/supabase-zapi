import os
import re
import logging
import requests
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)

class ZApiService:
    """
    Serviço responsável pelo envio de mensagens utilizando a API da Z-API.
    """

    def __init__(self) -> None:
        self.instance_id: str | None = os.getenv("ZAPI_INSTANCE_ID")
        self.token: str | None = os.getenv("ZAPI_TOKEN")
        self.client_token: str | None = os.getenv("ZAPI_CLIENT_TOKEN")
        self.timeout: int = int(os.getenv("HTTP_TIMEOUT", "10"))
        
        if not self.instance_id or not self.token or not self.client_token:
            raise ValueError(
                "As credenciais ZAPI_INSTANCE_ID, ZAPI_TOKEN e ZAPI_CLIENT_TOKEN "
                "são obrigatórias no ambiente."
            )
            
        self.base_url: str = (
            f"https://api.z-api.io/instances/{self.instance_id}/token/{self.token}"
        )

    def _validate_phone(self, phone: str) -> str:
        """
        Limpa e valida o formato do número de telefone.
        
        Args:
            phone (str): O número de telefone a ser validado.
            
        Returns:
            str: O número formatado apenas com dígitos.
            
        Raises:
            ValueError: Se o número não contiver a quantidade esperada de dígitos.
        """
        clean_phone: str = re.sub(r"\D", "", str(phone))
        
        # Considera um telefone válido entre 10 e 15 dígitos com DDI e DDD
        if not (10 <= len(clean_phone) <= 15):
            raise ValueError(
                f"Formato inválido ou incompleto: '{phone}'. "
                f"Esperado entre 10 e 15 dígitos numéricos."
            )
            
        return clean_phone

    def send_message(self, phone: str, message: str) -> None:
        """
        Envia uma mensagem de texto via Z-API.
        
        Args:
            phone (str): Número do destinatário.
            message (str): Conteúdo da mensagem.
            
        Raises:
            ValueError: Se o telefone for inválido.
            ConnectionError: Em falhas de comunicação com a API (Timeouts, HTTP Errors).
        """
        clean_phone: str = self._validate_phone(phone)
        
        endpoint: str = f"{self.base_url}/send-text"
        headers: dict[str, str] = {
            "Client-Token": self.client_token,
            "Content-Type": "application/json"
        }
        payload: dict[str, str] = {
            "phone": clean_phone,
            "message": message
        }
        
        logger.debug("Enviando requisição POST para Z-API com destino: %s", clean_phone)
        
        try:
            response = requests.post(
                endpoint, 
                json=payload, 
                headers=headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info("Mensagem enviada com êxito para o número %s.", clean_phone)
            
        except Timeout:
            logger.error(
                "A requisição para a Z-API excedeu o tempo limite (%ds).", 
                self.timeout
            )
            raise ConnectionError("Timeout na comunicação com a Z-API.") from None
            
        except RequestException as e:
            error_details = e.response.text if getattr(e, 'response', None) else str(e)
            status_code = getattr(getattr(e, 'response', None), 'status_code', 'N/A')
            
            logger.error("Falha na comunicação com a Z-API (Status %s): %s", status_code, error_details)
            raise ConnectionError(
                f"Erro ao enviar mensagem para {clean_phone}: {error_details}"
            ) from e
