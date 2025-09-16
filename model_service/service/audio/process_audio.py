from faster_whisper import WhisperModel
import os
from model_service.conf.settings import settings
import base64
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from uuid import uuid4
# 全局模型变量
model = None

def load_model():
    """根据环境变量决定是否加载模型"""
    global model
    if settings.LOAD_MODEL and model is None:
        model_size = "medium"
        # Run on GPU with FP16
        model = WhisperModel(model_size, device="cuda", compute_type="float16")
        print("模型已加载")
    elif not settings.LOAD_MODEL:
        print("环境变量LOAD_MODEL为False，跳过模型加载")
    return model

# 如果环境变量为True，则启动时加载模型
if settings.LOAD_MODEL:
    load_model()

def transcribe(json_data):
    """转录音频文件"""
    if not settings.LOAD_MODEL or model is None:
        print("模型未加载，无法进行转录")
        return None
    audio_data = json_data["data"]
    audio_data = base64.b64decode(audio_data)
    audio_path = f"{uuid4()}.wav"
    with open(audio_path, "wb") as f:
        f.write(audio_data)
    segments, info = model.transcribe(audio_path, beam_size=5, language="zh", initial_prompt="这是一段简体中文的音频")
    os.remove(audio_path)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    text = ""
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        text += segment.text
    if "点赞" in text or "关注" in text or "谢" in text:
        return None
    return text

def check_wake_word(text):
    """检查是否包含唤醒词"""
    if not text:
        return False
    
    # 定义唤醒词列表
    wake_words = [
        "小助手", "助手", "你好助手", "小爱", "小度", "小艺",
        "hey assistant", "hello assistant", "wake up", "开始"
    ]
    
    text_lower = text.lower().strip()
    
    for wake_word in wake_words:
        if wake_word.lower() in text_lower:
            print(f"检测到唤醒词: {wake_word}")
            return True
    
    return False

def transcribe_for_wake_word():
    """专门用于唤醒词检测的转录函数"""
    if not settings.LOAD_MODEL or model is None:
        print("模型未加载，无法进行唤醒词检测")
        return ""
        
    segments, info = model.transcribe("audio.wav", beam_size=5, language="zh", initial_prompt="这是一段简体中文的音频")
    
    text = ""
    for segment in segments:
        text += segment.text
    
    return text.strip()
    