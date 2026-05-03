from deep_translator import (
    BaiduTranslator,
    ChatGptTranslator,
    DeeplTranslator,
    GoogleTranslator,
    LibreTranslator,
    LingueeTranslator,
    MicrosoftTranslator,
    MyMemoryTranslator,
    PapagoTranslator,
    PonsTranslator,
    QcriTranslator,
    YandexTranslator,
)

TRANSLATORS = {
    "google": GoogleTranslator,
    "mymemory": MyMemoryTranslator,
    "linguee": LingueeTranslator,
    "pons": PonsTranslator,
    "libre": LibreTranslator,
    "deepl": DeeplTranslator,
    "microsoft": MicrosoftTranslator,
    "yandex": YandexTranslator,
    "qcri": QcriTranslator,
    "chatgpt": ChatGptTranslator,
    "papago": PapagoTranslator,
    "baidu": BaiduTranslator,
}

SINGLE_KEY_TRANSLATORS = {"deepl", "microsoft", "yandex", "qcri", "chatgpt", "libre"}
DUAL_KEY_TRANSLATORS = {"papago", "baidu"}
KEY_REQUIRED_TRANSLATORS = SINGLE_KEY_TRANSLATORS | DUAL_KEY_TRANSLATORS


class Translator:
    def __init__(self, backend="google", target=None, api_key=None):
        self.backend = backend
        self.target = target
        self._api_key = api_key

        if target:
            if backend in KEY_REQUIRED_TRANSLATORS and not api_key:
                raise ValueError(f"--translator {backend} requires --api-key")
            if backend in DUAL_KEY_TRANSLATORS and api_key and ":" not in api_key:
                raise ValueError(f"--translator {backend} requires --api-key in 'id:secret' format")

    def translate(self, result, on_progress=None):
        source_lang = result.get("language") or "auto"
        if not self.target or self.target == source_lang:
            return result

        backend = self._build(source_lang)
        segments = result["segments"]
        translated = []

        for segment in segments:
            segment["text"] = backend.translate(segment["text"])
            translated.append(segment["text"])
            if on_progress:
                on_progress(advance=1)

        result["text"] = " ".join(translated)
        return result

    def _build(self, source):
        cls = TRANSLATORS[self.backend]
        if self.backend in SINGLE_KEY_TRANSLATORS:
            return cls(source=source, target=self.target, api_key=self._api_key)
        if self.backend == "papago":
            client_id, secret_key = self._api_key.split(":", 1)
            return cls(source=source, target=self.target, client_id=client_id, secret_key=secret_key)
        if self.backend == "baidu":
            appid, appkey = self._api_key.split(":", 1)
            return cls(source=source, target=self.target, appid=appid, appkey=appkey)
        return cls(source=source, target=self.target)
