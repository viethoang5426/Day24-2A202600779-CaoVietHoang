# src/pii/detector.py
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider

VI_LANGUAGE = "vi"
SUPPORTED_ENTITIES = ["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"]

def _resolve_vi_model_name() -> str:
    """Try to find a Vietnamese spaCy model, return empty string if none found."""
    import spacy
    for name in ("vi_spacy_model", "vi_core_news_lg"):
        try:
            spacy.load(name)
            return name
        except OSError:
            continue
    return ""

def _blank_vi_model_path() -> str:
    """Create and return path to a blank Vietnamese spaCy model as fallback."""
    import spacy
    from pathlib import Path
    blank_path = Path.cwd() / ".spacy_models" / "vi_blank"
    if not blank_path.exists():
        blank_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            nlp = spacy.blank("vi")
        except ImportError:
            # If pyvi is not available, use English blank model as fallback
            nlp = spacy.blank("en")
        nlp.to_disk(blank_path)
    return str(blank_path)

def build_vietnamese_analyzer() -> AnalyzerEngine:
    """
    Xây dựng AnalyzerEngine với các recognizer tùy chỉnh cho VN.
    Dùng pattern-based recognizers + fallback blank model nếu không có NER model.
    """

    # --- TASK 2.2.1 ---
    # Tạo CCCD recognizer: số CCCD VN có đúng 12 chữ số
    cccd_pattern = Pattern(
        name="cccd_pattern",
        regex=r"\b\d{12}\b",
        score=0.9
    )
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        supported_language=VI_LANGUAGE,
        patterns=[cccd_pattern],
        context=["cccd", "căn cước", "chứng minh", "cmnd"]
    )

    # --- TASK 2.2.2 ---
    # Tạo phone recognizer: số điện thoại VN (0[3|5|7|8|9]xxxxxxxx)
    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        supported_language=VI_LANGUAGE,
        patterns=[Pattern(
            name="vn_phone",
            regex=r"\b0[35789]\d{8}\b",
            score=0.85
        )],
        context=["điện thoại", "sdt", "phone", "liên hệ"]
    )

    # Email recognizer (custom pattern for better Vietnamese context detection)
    email_recognizer = PatternRecognizer(
        supported_entity="EMAIL_ADDRESS",
        supported_language=VI_LANGUAGE,
        patterns=[Pattern(
            name="email_pattern",
            regex=r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
            score=0.9
        )],
        context=["email", "mail", "gmail"]
    )

    # Person recognizer (pattern-based for Vietnamese names)
    person_recognizer = PatternRecognizer(
        supported_entity="PERSON",
        supported_language=VI_LANGUAGE,
        patterns=[Pattern(
            name="vn_person_latin",
            regex=(
                r"\b[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐĐ]"
                r"[a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]*"
                r"(?:\s+[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"
                r"a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+){0,3}\b"
            ),
            score=0.65
        )]
    )

    # --- TASK 2.2.3 ---
    # Tạo NLP engine dùng spaCy Vietnamese model (with fallback)
    model_name = _resolve_vi_model_name()
    if not model_name:
        model_name = _blank_vi_model_path()

    provider = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "vi",
                    "model_name": model_name}]
    })
    nlp_engine = provider.create_engine()

    # --- TASK 2.2.4 ---
    # Khởi tạo AnalyzerEngine và add các recognizer
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=[VI_LANGUAGE]
    )
    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)
    analyzer.registry.add_recognizer(email_recognizer)
    analyzer.registry.add_recognizer(person_recognizer)

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    """
    Detect PII trong text tiếng Việt.
    Trả về list các RecognizerResult.
    Entities cần detect: PERSON, EMAIL_ADDRESS, VN_CCCD, VN_PHONE
    """
    results = analyzer.analyze(
        text=text,
        language=VI_LANGUAGE,
        entities=SUPPORTED_ENTITIES
    )
    return results
