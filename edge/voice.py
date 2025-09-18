import shutil
import subprocess
import sys
from typing import Optional
from tex_to_text import latex_to_text


def is_spd_say_available() -> bool:
    """
    Проверяет, доступна ли утилита spd-say (Speech Dispatcher), используемая RHVoice.
    """
    return shutil.which("spd-say") is not None


def is_rhvoice_available() -> bool:
    """
    Считаем доступным TTS через Speech Dispatcher, если есть spd-say.
    Конкретный модуль (RHVoice) выбирается настройкой speech-dispatcher.
    """
    return is_spd_say_available()


def speak_rhvoice(text: str, voice: Optional[str] = None, rate: Optional[int] = None,
                  pitch: Optional[int] = None, volume: Optional[int] = None, lang: Optional[str] = None,
                  module: Optional[str] = None, convert_latex: bool = True) -> None:
    """
    Озвучивает текст через RHVoice (через spd-say). Можно указать голос, скорость, тон, громкость и язык.
    Примеры голосов: anna, elena, aleksandr и т.д. (см. spd-say -L)
    Параметры:
      - voice: имя голоса (например, "anna")
      - rate: скорость речи  -100..100 (spd-say -r)
      - pitch: высота тона  -100..100 (spd-say -p)
      - volume: громкость   -100..100 (spd-say -i)
      - lang: язык, например "ru", "en" (spd-say -l)
      - convert_latex: преобразовывать LaTeX символы в текст (по умолчанию True)
    """
    if not text:
        return
    
    # Преобразуем LaTeX символы в текст, если включено
    if convert_latex:
        text = latex_to_text(text)
    
    if not is_spd_say_available():
        raise RuntimeError("spd-say не найден. Установите speech-dispatcher и RHVoice.")
    cmd = ["spd-say"]
    if module:
        cmd += ["-o", module]
    if lang:
        cmd += ["-l", lang]
    if voice:
        cmd += ["-y", voice]
    if rate is not None:
        cmd += ["-r", str(rate)]
    if pitch is not None:
        cmd += ["-p", str(pitch)]
    if volume is not None:
        cmd += ["-i", str(volume)]
    cmd += [text]
    subprocess.run(cmd, check=True)


def list_rhvoice_voices() -> str:
    """
    Возвращает список доступных голосов из spd-say -L.
    """
    if not is_spd_say_available():
        return ""
    try:
        result = subprocess.run(["spd-say", "-L"], capture_output=True, text=True, check=True)
        return (result.stdout or "") + (result.stderr or "")
    except Exception:
        return ""


def main() -> int:
    # Аргументы: [текст] [--voice NAME] [--lang ru|en] [--rate -100..100] [--pitch -100..100] [--volume -100..100] [--module rhvoice] [--no-latex] [--list]
    args = [a for a in sys.argv[1:] if a]
    text_parts = []
    lang: Optional[str] = "ru"
    voice: Optional[str] = None
    rate: Optional[int] = None
    pitch: Optional[int] = None
    volume: Optional[int] = None
    list_only = False
    module: Optional[str] = None
    convert_latex: bool = True

    i = 0
    while i < len(args):
        a = args[i]
        if a == "--lang" and i + 1 < len(args):
            lang = args[i + 1].strip().lower()
            i += 2
            continue
        if a == "--voice" and i + 1 < len(args):
            voice = args[i + 1].strip()
            i += 2
            continue
        if a == "--rate" and i + 1 < len(args):
            rate = int(args[i + 1])
            i += 2
            continue
        if a == "--pitch" and i + 1 < len(args):
            pitch = int(args[i + 1])
            i += 2
            continue
        if a == "--volume" and i + 1 < len(args):
            volume = int(args[i + 1])
            i += 2
            continue
        if a == "--list":
            list_only = True
            i += 1
            continue
        if a == "--module" and i + 1 < len(args):
            module = args[i + 1].strip()
            i += 2
            continue
        if a == "--no-latex":
            convert_latex = False
            i += 1
            continue
        text_parts.append(a)
        i += 1

    if list_only:
        voices = list_rhvoice_voices()
        print(voices or "Список голосов пуст. Убедитесь, что установлен RHVoice и настроен speech-dispatcher.")
        return 0

    text = " ".join(text_parts).strip()
    if not text:
        text = "Привет! Это RHVoice."

    if not is_rhvoice_available():
        print("Speech Dispatcher (spd-say) не обнаружен. Установите 'speech-dispatcher'.")
        return 1

    try:
        speak_rhvoice(text, voice=voice, rate=rate, pitch=pitch, volume=volume, lang=lang, module=module, convert_latex=convert_latex)
    except subprocess.CalledProcessError as exc:
        print(f"Ошибка запуска RHVoice: {exc}")
        return exc.returncode or 1
    except Exception as exc:
        print(f"Ошибка: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



