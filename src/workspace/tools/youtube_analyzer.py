"""YouTube Video Analyzer - Analisa vídeos do YouTube com Groq Vision"""
import os
import tempfile
import requests
import logging
from typing import Optional

from security.sanitizer import sanitize_youtube_url
from security.executor import SafeSubprocessExecutor

logger = logging.getLogger(__name__)

class YouTubeAnalyzer:
    """Analisador de vídeos do YouTube usando Groq Vision"""
    
    def __init__(self):
        # GLM removido - agora usa apenas Groq Vision (mais rápido e confiável)
        pass

    async def _download_video(self, youtube_url: str, output_path: str) -> bool:
        """Baixa vídeo do YouTube (URL sanitizada, executor seguro)."""
        ok, clean_url = sanitize_youtube_url(youtube_url.strip())
        if not ok:
            logger.warning(f"URL do YouTube rejeitada: {youtube_url[:80]}")
            return False
        try:
            success, _, err = await SafeSubprocessExecutor.run(
                ["yt-dlp", "-f", "worst", "-o", output_path, clean_url],
                timeout=120,
            )
            if not success:
                logger.error(f"yt-dlp falhou: {err}")
            return success
        except Exception as e:
            logger.error(f"Erro ao baixar vídeo: {e}")
            return False
    
    async def _extract_frames(self, video_path: str, output_dir: str, fps: float = 0.2) -> list:
        """Extrai frames do vídeo (1 frame a cada 5 segundos por padrão)"""
        try:
            frame_pattern = os.path.join(output_dir, "frame_%03d.jpg")
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"fps={fps}",
                "-q:v", "5",  # Qualidade média
                frame_pattern
            ]
            success, _, _ = await SafeSubprocessExecutor.run(cmd, timeout=60)
            if not success:
                logger.error("FFmpeg falhou ao extrair frames")
                return []
            
            # Lista frames gerados
            frames = sorted([
                os.path.join(output_dir, f) 
                for f in os.listdir(output_dir) 
                if f.startswith("frame_") and f.endswith(".jpg")
            ])
            return frames[:20]  # Máximo 20 frames
        except Exception as e:
            logger.error(f"Erro ao extrair frames: {e}")
            return []
    
    def _upload_frame(self, frame_path: str) -> Optional[str]:
        """Upload frame para Imgur (temporário)"""
        imgur_client_id = os.getenv("IMGUR_CLIENT_ID")
        if not imgur_client_id:
            logger.warning("IMGUR_CLIENT_ID não configurado - upload de frame desabilitado")
            return None
        
        try:
            with open(frame_path, 'rb') as f:
                response = requests.post(
                    'https://api.imgur.com/3/image',
                    headers={'Authorization': f'Client-ID {imgur_client_id}'},
                    files={'image': f},
                    timeout=10
                )
            if response.status_code == 200:
                return response.json()['data']['link']
        except Exception as e:
            logger.error(f"Erro ao fazer upload: {e}")
        return None
    def _analyze_frames_groq(self, frame_paths: list, prompt: str) -> Optional[str]:
        """Analisa frames com Groq Vision (mais confiável)"""
        try:
            from groq import Groq
            import base64
            
            groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            
            # Pega apenas 3 frames (início, meio, fim)
            selected_frames = []
            if len(frame_paths) >= 3:
                selected_frames = [
                    frame_paths[0],  # Início
                    frame_paths[len(frame_paths)//2],  # Meio
                    frame_paths[-1]  # Fim
                ]
            else:
                selected_frames = frame_paths
            
            # Converte frames para base64
            content = [{"type": "text", "text": prompt}]
            for frame_path in selected_frames:
                with open(frame_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
                    })
            
            response = groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": content}],
                temperature=0.5,
                max_completion_tokens=1024
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao analisar frames com Groq: {e}")
            return None
    
    async def analyze_youtube_video(self, youtube_url: str, user_prompt: str = None) -> str:
        """Analisa vídeo do YouTube e retorna resumo"""
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                # 1. Baixa vídeo
                video_path = os.path.join(tmpdir, "video.mp4")
                logger.info(f"Baixando vídeo: {youtube_url}")
                if not await self._download_video(youtube_url, video_path):
                    return "❌ Erro ao baixar vídeo. Verifique o link."
                
                # 2. Extrai frames
                logger.info("Extraindo frames...")
                frames_dir = os.path.join(tmpdir, "frames")
                os.makedirs(frames_dir)
                frame_paths = await self._extract_frames(video_path, frames_dir)
                
                if not frame_paths:
                    return "❌ Erro ao extrair frames do vídeo."
                
                logger.info(f"Extraídos {len(frame_paths)} frames")
                
                # 4. Analisa com Groq Vision (sem precisar de upload)
                prompt = user_prompt or "Analise esta sequência de frames de um vídeo e forneça um resumo detalhado do conteúdo, incluindo: tema principal, eventos importantes, e conclusão."
                
                logger.info("Analisando vídeo com Groq Vision...")
                result = self._analyze_frames_groq(frame_paths, prompt)
                
                if result:
                    return f"🎬 **Resumo do Vídeo:**\n\n{result}"
                else:
                    return "❌ Erro ao analisar vídeo."
                
            except Exception as e:
                logger.error(f"Erro geral: {e}")
                return "❌ Erro ao processar vídeo. Tente novamente."
