"""Relent AI - Centralized LLM & Reasoning Engine.

Primary Reasoning & Tone-Matching LLM: Qwen2.5-72B (4-bit quantized)
Hindi-Specialized & Failover Fallback: Sarvam-M
"""

import os
import sys
from typing import Any, Callable

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def safe_print(text: str = "") -> None:
    try:
        print(text)
    except Exception:
        try:
            encoding = sys.stdout.encoding or "utf-8"
            print(str(text).encode(encoding, errors="replace").decode(encoding, errors="replace"))
        except Exception:
            pass


# Primary: Qwen2.5-72B (4-bit quantized for efficient high-reasoning and tone-matching)
PRIMARY_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:72b-instruct-q4_K_M")
# Fallback: Sarvam-M (Hindi & Indic language specialized foundation model)
FALLBACK_MODEL = os.getenv("OLLAMA_FALLBACK_MODEL", os.getenv("SARVAM_MODEL", "sarvam-m"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Set of Indic / Hindi language identifiers for routing
INDIC_LANGUAGES = {
    "hindi",
    "hinglish",
    "indic",
    "bengali",
    "marathi",
    "telugu",
    "tamil",
    "gujarati",
    "kannada",
    "malayalam",
    "odia",
    "punjabi",
}


def is_indic_language(lang: str | None) -> bool:
    """Check if the provided language string corresponds to Hindi / Indic languages."""
    if not lang:
        return False
    return lang.strip().lower() in INDIC_LANGUAGES


class FallbackChatOllama:
    """Wrapper that manages execution between primary (Qwen2.5-72B 4-bit)
    and specialized fallback (Sarvam-M) with lazy initialization and automatic error recovery.
    """

    def __init__(
        self,
        primary_llm: Any = None,
        fallback_llm: Any = None,
        primary_factory: Callable[[], Any] | None = None,
        fallback_factory: Callable[[], Any] | None = None,
        prefer_fallback: bool = False,
    ):
        self._primary_llm = primary_llm
        self._fallback_llm = fallback_llm
        self._primary_factory = primary_factory
        self._fallback_factory = fallback_factory
        self.prefer_fallback = prefer_fallback

    @property
    def primary_llm(self) -> Any:
        if self._primary_llm is None and self._primary_factory is not None:
            self._primary_llm = self._primary_factory()
        return self._primary_llm

    @property
    def fallback_llm(self) -> Any:
        if self._fallback_llm is None and self._fallback_factory is not None:
            self._fallback_llm = self._fallback_factory()
        return self._fallback_llm

    def _get_active_and_backup(self) -> tuple[Any, Any]:
        if self.prefer_fallback:
            return self.fallback_llm, self.primary_llm
        return self.primary_llm, self.fallback_llm

    def invoke(self, input: Any, config: Any = None, **kwargs: Any) -> Any:
        active, backup = self._get_active_and_backup()
        try:
            return active.invoke(input, config=config, **kwargs)
        except Exception as primary_error:
            if backup is not None:
                safe_print(
                    f"⚠️ Primary LLM ({getattr(active, 'model', 'active')}) encountered error: {primary_error}."
                    f" Failing over to fallback LLM ({getattr(backup, 'model', 'fallback')})..."
                )
                try:
                    return backup.invoke(input, config=config, **kwargs)
                except Exception as backup_error:
                    safe_print(f"❌ Fallback LLM also failed: {backup_error}")
                    raise backup_error from primary_error
            raise primary_error

    async def ainvoke(self, input: Any, config: Any = None, **kwargs: Any) -> Any:
        active, backup = self._get_active_and_backup()
        try:
            return await active.ainvoke(input, config=config, **kwargs)
        except Exception as primary_error:
            if backup is not None:
                safe_print(
                    f"⚠️ Primary LLM ({getattr(active, 'model', 'active')}) encountered error: {primary_error}."
                    f" Failing over to fallback LLM ({getattr(backup, 'model', 'fallback')})..."
                )
                try:
                    return await backup.ainvoke(input, config=config, **kwargs)
                except Exception as backup_error:
                    safe_print(f"❌ Fallback LLM also failed: {backup_error}")
                    raise backup_error from primary_error
            raise primary_error

    def batch(self, inputs: list[Any], config: Any = None, **kwargs: Any) -> list[Any]:
        active, backup = self._get_active_and_backup()
        try:
            return active.batch(inputs, config=config, **kwargs)
        except Exception as primary_error:
            if backup is not None:
                safe_print(
                    "⚠️ Primary LLM batch failed. Failing over to fallback LLM..."
                )
                return backup.batch(inputs, config=config, **kwargs)
            raise primary_error

    def stream(self, input: Any, config: Any = None, **kwargs: Any):
        active, backup = self._get_active_and_backup()
        try:
            yield from active.stream(input, config=config, **kwargs)
        except Exception as primary_error:
            if backup is not None:
                safe_print(
                    "⚠️ Primary LLM stream failed. Failing over to fallback LLM..."
                )
                yield from backup.stream(input, config=config, **kwargs)
            else:
                raise primary_error

    def __or__(self, other: Any) -> Any:
        from langchain_core.runnables import RunnableSequence

        return RunnableSequence(self, other)

    def __ror__(self, other: Any) -> Any:
        from langchain_core.runnables import RunnableSequence

        return RunnableSequence(other, self)

    def bind(self, **kwargs: Any) -> Any:
        active, backup = self._get_active_and_backup()
        active_bound = active.bind(**kwargs) if hasattr(active, "bind") else active
        backup_bound = (
            backup.bind(**kwargs)
            if backup is not None and hasattr(backup, "bind")
            else backup
        )
        if self.prefer_fallback:
            return FallbackChatOllama(
                primary_llm=backup_bound,
                fallback_llm=active_bound,
                prefer_fallback=True,
            )
        return FallbackChatOllama(
            primary_llm=active_bound,
            fallback_llm=backup_bound,
            prefer_fallback=False,
        )


def create_ollama_instance(
    model_name: str,
    temperature: float = 0.3,
    format: str | None = None,
    base_url: str | None = None,
    **extra_kwargs: Any,
) -> Any:
    """Create a LangChain ChatOllama instance with GPU auto-detection."""
    from langchain_ollama import ChatOllama

    kwargs = {
        "model": model_name,
        "base_url": base_url or OLLAMA_BASE_URL,
        "temperature": temperature,
    }
    if format:
        kwargs["format"] = format

    num_gpu = os.getenv("OLLAMA_NUM_GPU")
    if num_gpu is not None and num_gpu != "":
        try:
            kwargs["num_gpu"] = int(num_gpu)
        except ValueError:
            pass

    kwargs.update(extra_kwargs)
    return ChatOllama(**kwargs)


def get_llm(
    model: str | None = None,
    fallback_model: str | None = None,
    language: str | None = None,
    temperature: float = 0.3,
    format: str | None = None,
    enable_fallback: bool = True,
    **kwargs: Any,
) -> Any:
    """Instantiate the primary reasoning & tone-matching LLM (Qwen2.5-72B 4-bit)
    with intelligent routing / fallback to Sarvam-M (Hindi-specialized).
    """
    primary_name = model or os.getenv("OLLAMA_MODEL", PRIMARY_MODEL)
    fallback_name = fallback_model or os.getenv("OLLAMA_FALLBACK_MODEL", os.getenv("SARVAM_MODEL", FALLBACK_MODEL))

    prefer_hindi = is_indic_language(language)

    if not enable_fallback or not fallback_name or fallback_name == primary_name:
        return create_ollama_instance(
            model_name=primary_name,
            temperature=temperature,
            format=format,
            **kwargs,
        )

    # Initialize with lazy loading for whichever model is the backup
    if prefer_hindi:
        active_llm = create_ollama_instance(
            model_name=fallback_name,
            temperature=temperature,
            format=format,
            **kwargs,
        )
        return FallbackChatOllama(
            fallback_llm=active_llm,
            primary_factory=lambda: create_ollama_instance(
                model_name=primary_name,
                temperature=temperature,
                format=format,
                **kwargs,
            ),
            prefer_fallback=True,
        )

    primary_llm = create_ollama_instance(
        model_name=primary_name,
        temperature=temperature,
        format=format,
        **kwargs,
    )
    return FallbackChatOllama(
        primary_llm=primary_llm,
        fallback_factory=lambda: create_ollama_instance(
            model_name=fallback_name,
            temperature=temperature,
            format=format,
            **kwargs,
        ),
        prefer_fallback=False,
    )
