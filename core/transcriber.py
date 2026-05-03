import warnings

import whisper


class Transcriber:
    def __init__(self, model_name="base", device="auto"):
        self.model_name = model_name
        self._model = None

        if device == "auto":
            self.device = "cuda" if whisper.torch.cuda.is_available() else "cpu"
        else:
            self.device = device

    def load(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                self._model = whisper.load_model(self.model_name, device=self.device)
            except RuntimeError:
                self.device = "cpu"
                self._model = whisper.load_model(self.model_name, device=self.device)

    def transcribe(self, audio_path, lang=None, prompt=None):
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        kwargs = {"verbose": False}
        if lang:
            kwargs["language"] = lang
        if prompt:
            kwargs["initial_prompt"] = prompt
        if self.device == "cpu":
            kwargs["fp16"] = False

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return self._model.transcribe(audio_path, **kwargs)
