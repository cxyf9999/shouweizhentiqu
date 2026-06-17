import os
import json
import base64
import requests
from dotenv import load_dotenv

class ModelManager:
    def __init__(self, env_path=None):
        if env_path is None:
            env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path)
        
        # 模型分类配置
        self.model_categories = {
            "text_to_text": {
                "name": "文本对文本",
                "models": [
                    {"id": "openai", "name": "GPT-4o (OpenAI)", "provider": "openai"},
                    {"id": "anthropic", "name": "Claude 3.5 Sonnet (Anthropic)", "provider": "anthropic"},
                    {"id": "google", "name": "Gemini 2.0 Pro (Google)", "provider": "google"},
                    {"id": "deepseek", "name": "DeepSeek Chat (深度求索)", "provider": "deepseek"},
                    {"id": "qianwen", "name": "Qwen Max (通义千问)", "provider": "qianwen"},
                    {"id": "doubao", "name": "Doubao Pro (豆包)", "provider": "doubao"},
                    {"id": "yi", "name": "Yi Large (零一万物)", "provider": "yi"},
                    {"id": "moonshot", "name": "Moonshot (月之暗面)", "provider": "moonshot"},
                    {"id": "spark", "name": "Spark 4.0 (星火)", "provider": "spark"}
                ]
            },
            "text_to_image": {
                "name": "文本到图像",
                "models": [
                    {"id": "dalle", "name": "DALL-E 3 (OpenAI)", "provider": "dalle"},
                    {"id": "midjourney", "name": "Midjourney v6", "provider": "midjourney"},
                    {"id": "wanx", "name": "WanX v2 (通义万相)", "provider": "wanx"},
                    {"id": "hunyuan", "name": "Hunyuan DIT (混元生图)", "provider": "hunyuan"}
                ]
            },
            "text_to_video": {
                "name": "文本到视频",
                "models": [
                    {"id": "sora", "name": "Sora (OpenAI)", "provider": "sora"},
                    {"id": "runway", "name": "Runway Gen-3", "provider": "runway"},
                    {"id": "sora_china", "name": "Sora CN", "provider": "sora_china"},
                    {"id": "kaichao", "name": "Kaichao Video (开朝)", "provider": "kaichao"},
                    {"id": "wanx_video", "name": "WanX Video (通义万相)", "provider": "wanx_video"}
                ]
            },
            "image_to_video": {
                "name": "图像到视频",
                "models": [
                    {"id": "runway_image", "name": "Runway Image-to-Video", "provider": "runway_image_to_video"},
                    {"id": "pika", "name": "Pika 1.0", "provider": "pika"},
                    {"id": "minimax", "name": "MiniMax VideoCraft", "provider": "minimax"},
                    {"id": "qianwen_image_video", "name": "Qwen VideoCraft", "provider": "qianwen_image_to_video"}
                ]
            },
            "video_to_video": {
                "name": "视频到视频",
                "models": [
                    {"id": "runway_video_edit", "name": "Runway Video-to-Video", "provider": "runway_video_edit"},
                    {"id": "minimax_video_edit", "name": "MiniMax Video Editing", "provider": "minimax_video_edit"},
                    {"id": "qianwen_video_edit", "name": "Qwen Video Edit", "provider": "qianwen_video_edit"}
                ]
            },
            "vision": {
                "name": "图像分析",
                "models": [
                    {"id": "openai_vision", "name": "GPT-4o Vision (OpenAI)", "provider": "openai_vision"},
                    {"id": "gemini_vision", "name": "Gemini 2.0 Vision (Google)", "provider": "gemini_vision"},
                    {"id": "qianwen_vision", "name": "Qwen VL Max (通义千问)", "provider": "qianwen_vision"},
                    {"id": "doubao_vision", "name": "Doubao Pro Vision (豆包)", "provider": "doubao_vision"}
                ]
            }
        }
        
        # 模型提供商配置
        self.providers = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
                "api_url": os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
            },
            "anthropic": {
                "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                "api_url": os.getenv("ANTHROPIC_API_URL", "https://api.anthropic.com/v1/messages")
            },
            "google": {
                "api_key": os.getenv("GOOGLE_API_KEY", ""),
                "model": os.getenv("GOOGLE_MODEL", "gemini-2.0-pro-exp-02-05"),
                "api_url": os.getenv("GOOGLE_API_URL", "https://generativelanguage.googleapis.com/v1beta/models")
            },
            "deepseek": {
                "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                "api_url": os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
            },
            "qianwen": {
                "api_key": os.getenv("QIANWEN_API_KEY", ""),
                "model": os.getenv("QIANWEN_MODEL", "qwen-max-latest"),
                "api_url": os.getenv("QIANWEN_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
            },
            "doubao": {
                "api_key": os.getenv("DOUBAO_API_KEY", ""),
                "model": os.getenv("DOUBAO_MODEL", "doubao-pro-4k"),
                "api_url": os.getenv("DOUBAO_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
            },
            "yi": {
                "api_key": os.getenv("YI_API_KEY", ""),
                "model": os.getenv("YI_MODEL", "yi-large-preview"),
                "api_url": os.getenv("YI_API_URL", "https://api.lingyiwanwu.com/v1/chat/completions")
            },
            "moonshot": {
                "api_key": os.getenv("MOONSHOT_API_KEY", ""),
                "model": os.getenv("MOONSHOT_MODEL", "moonshot-v1-128k"),
                "api_url": os.getenv("MOONSHOT_API_URL", "https://api.moonshot.cn/v1/chat/completions")
            },
            "spark": {
                "api_key": os.getenv("SPARK_API_KEY", ""),
                "model": os.getenv("SPARK_MODEL", "spark-4.0"),
                "api_url": os.getenv("SPARK_API_URL", "https://spark-api-open.xf-yun.com/v1/chat/completions")
            },
            "openai_vision": {
                "api_key": os.getenv("OPENAI_VISION_API_KEY", ""),
                "model": os.getenv("OPENAI_VISION_MODEL", "gpt-4o"),
                "api_url": os.getenv("OPENAI_VISION_API_URL", "https://api.openai.com/v1/chat/completions")
            },
            "qianwen_vision": {
                "api_key": os.getenv("QIANWEN_VISION_API_KEY", ""),
                "model": os.getenv("QIANWEN_VISION_MODEL", "qwen-vl-max-latest"),
                "api_url": os.getenv("QIANWEN_VISION_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
            },
            "doubao_vision": {
                "api_key": os.getenv("DOUBAO_VISION_API_KEY", ""),
                "model": os.getenv("DOUBAO_VISION_MODEL", "doubao-pro-vision"),
                "api_url": os.getenv("DOUBAO_VISION_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
            }
        }
    
    def get_categories(self):
        """获取所有模型分类"""
        return self.model_categories
    
    def get_models_by_category(self, category_id):
        """获取指定分类的模型列表"""
        if category_id in self.model_categories:
            return self.model_categories[category_id]["models"]
        return []
    
    def get_model_config(self, provider_id):
        """获取指定提供商的配置"""
        return self.providers.get(provider_id, {})
    
    def set_api_key(self, provider_id, api_key):
        """设置指定提供商的API Key"""
        if provider_id in self.providers:
            self.providers[provider_id]["api_key"] = api_key
    
    def chat_completion(self, provider_id, messages, temperature=0.7, max_tokens=2000):
        """文本聊天完成"""
        config = self.get_model_config(provider_id)
        if not config["api_key"]:
            raise ValueError(f"未配置 {provider_id} 的API Key")
        
        # 兼容OpenAI格式的API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        data = {
            "model": config["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(config["api_url"], headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if provider_id == "anthropic":
            return result["content"][0]["text"]
        else:
            return result["choices"][0]["message"]["content"]
    
    def vision_completion(self, provider_id, text_prompt, image_b64, temperature=0.7, max_tokens=2000):
        """视觉理解（图片分析）"""
        config = self.get_model_config(provider_id)
        if not config["api_key"]:
            raise ValueError(f"未配置 {provider_id} 的API Key")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    }
                ]
            }
        ]
        
        data = {
            "model": config["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(config["api_url"], headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def generate_image(self, provider_id, prompt, size="1024x1024", n=1):
        """文本生成图像"""
        config = self.get_model_config(provider_id)
        if not config["api_key"]:
            raise ValueError(f"未配置 {provider_id} 的API Key")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        data = {
            "model": config["model"],
            "prompt": prompt,
            "size": size,
            "n": n
        }
        
        response = requests.post(config["api_url"], headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if provider_id == "dalle" or provider_id == "wanx":
            return result["data"][0]["url"]
        else:
            return result
    
    def generate_video(self, provider_id, prompt, duration=5, resolution="1920x1080"):
        """文本生成视频"""
        config = self.get_model_config(provider_id)
        if not config["api_key"]:
            raise ValueError(f"未配置 {provider_id} 的API Key")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        data = {
            "model": config["model"],
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution
        }
        
        response = requests.post(config["api_url"], headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        return response.json()
    
    def image_to_video(self, provider_id, image_b64, prompt="", duration=5):
        """图像生成视频"""
        config = self.get_model_config(provider_id)
        if not config["api_key"]:
            raise ValueError(f"未配置 {provider_id} 的API Key")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        data = {
            "model": config["model"],
            "prompt": prompt,
            "duration": duration,
            "image": f"data:image/jpeg;base64,{image_b64}"
        }
        
        response = requests.post(config["api_url"], headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        return response.json()
