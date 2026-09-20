from src.demo_config import DEMO_PROMPTS, WORKFLOW_STAGES


def test_demo_prompts_cover_positive_and_negative_scenarios():
    tones = {item["tone"] for item in DEMO_PROMPTS}
    categories = {item["category"] for item in DEMO_PROMPTS}

    assert len(DEMO_PROMPTS) >= 8
    assert tones == {"success", "warning", "error"}
    assert {"Tra cứu trực tiếp", "Ngoài domain", "Prompt injection", "Tiền đề sai"} <= categories
    assert all(item["prompt"].strip() and item["expectation"].strip() for item in DEMO_PROMPTS)


def test_demo_workflow_shows_complete_rag_flow():
    labels = " ".join(title for _, title, _ in WORKFLOW_STAGES).lower()

    assert len(WORKFLOW_STAGES) >= 6
    for expected in ("nguồn dữ liệu", "chuẩn hóa", "chunk", "retrieval", "generation"):
        assert expected in labels

