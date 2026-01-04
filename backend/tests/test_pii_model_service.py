import pytest
from app.services.model_service import (
    ModelRuleAbAi,
    RemovalServiceModel,
)


@pytest.fixture
def pii_model_service():
    rules = [ModelRuleAbAi()]
    return RemovalServiceModel(rules=rules)


class TestPiiModelService:
    @pytest.mark.parametrize(
        "original_text, expected_result",
        [
            (
                "My email is test@gmail.com and my phone is 123-456-7890.",
                "My email is [EMAIL_1] and my phone is [PHONENUMBER_1].",
            ),
        ],
    )
    def test_model_service_cleaning(
        self,
        monkeypatch,
        pii_model_service,
        original_text: str,
        expected_result: str,
    ) -> None:
        # IMPORTANT: patch where pipeline is imported/used (your module), not transformers.pipeline
        import app.services.model_service as ms

        def fake_pipeline(*args, **kwargs):
            # mimic HF token-classification pipeline returning aggregated spans
            def run(text: str):
                return [
                    {
                        "start": text.index("test@gmail.com"),
                        "end": text.index("test@gmail.com") + len("test@gmail.com"),
                        "entity_group": "EMAIL",
                        "score": 0.99,
                        "word": "test@gmail.com",
                    },
                    {
                        "start": text.index("123-456-7890"),
                        "end": text.index("123-456-7890") + len("123-456-7890"),
                        "entity_group": "PHONENUMBER",
                        "score": 0.98,
                        "word": "123-456-7890",
                    },
                ]

            return run

        monkeypatch.setattr(ms, "pipeline", fake_pipeline)

        result = pii_model_service.clean(original_text)

        assert result.cleaned_text == expected_result
        assert result.method == "model"
