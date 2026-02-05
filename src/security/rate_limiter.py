"""Rate limiting para prevenir abuso"""
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: int) -> bool:
        """Verifica se usuário pode fazer requisição"""
        now = datetime.now()
        
        # Remove requisições antigas
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window
        ]
        
        # Verifica limite
        if len(self.requests[user_id]) >= self.max_requests:
            logger.warning(
                f"Rate limit excedido: user_id={user_id}, "
                f"requests={len(self.requests[user_id])}"
            )
            return False
        
        # Registra requisição
        self.requests[user_id].append(now)
        return True
    
    def get_remaining(self, user_id: int) -> int:
        """Retorna número de requisições restantes"""
        now = datetime.now()
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window
        ]
        return max(0, self.max_requests - len(self.requests[user_id]))

# Instâncias globais
message_limiter = RateLimiter(max_requests=20, window_seconds=60)
media_limiter = RateLimiter(max_requests=5, window_seconds=60)
youtube_limiter = RateLimiter(max_requests=3, window_seconds=300)  # 3 por 5min
