"""应用配置 — 从 .env 文件读取环境变量"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM API（OpenAI兼容接口，支持智谱/百炼/DeepSeek等）
    llm_api_key: str = ""
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "qwen-plus"

    # Unsplash API（景点配图）
    unsplash_access_key: str = ""

    # 高德地图 Web服务API（后端调用）
    amap_api_key: str = ""
    amap_security_key: str = ""

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()