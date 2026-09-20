"""Run a reproducible A/B evaluation for dense and hybrid retrieval."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from ragas import EvaluationDataset, evaluate
from ragas.llms import llm_factory
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)
from ragas.run_config import RunConfig

from src.task10_generation import SYSTEM_PROMPT, call_llm, format_context, reorder_for_llm
from src.task9_retrieval_pipeline import retrieve


ROOT = Path(__file__).resolve().parents[2]
GOLDEN_PATH = Path(__file__).with_name("golden_dataset.json")
OUTPUT_PATH = Path(__file__).with_name("benchmark_results.json")
TOP_K = 5


def generate_samples(cases: list[dict], use_reranking: bool) -> list[dict]:
    samples = []
    for index, case in enumerate(cases, 1):
        started = time.perf_counter()
        chunks = retrieve(
            case["question"],
            top_k=TOP_K,
            use_reranking=use_reranking,
        )
        contexts = [chunk["content"] for chunk in chunks]
        prompt = (
            f"Context:\n{format_context(reorder_for_llm(chunks))}"
            f"\n\nQuestion: {case['question']}"
        )
        answer = call_llm(SYSTEM_PROMPT, prompt)
        latency = time.perf_counter() - started
        samples.append(
            {
                "case": index,
                "user_input": case["question"],
                "response": answer.strip(),
                "retrieved_contexts": contexts,
                "reference": case["expected_answer"],
                "expected_source": case["expected_context"].split(":", 1)[0],
                "retrieved_sources": [
                    chunk["metadata"]["source"] for chunk in chunks
                ],
                "latency_seconds": latency,
            }
        )
        print(f"Generated {index}/{len(cases)}", flush=True)
    return samples


def score_samples(samples: list[dict], evaluator_llm, evaluator_embeddings) -> list[dict]:
    dataset = EvaluationDataset.from_list(
        [
            {
                "user_input": sample["user_input"],
                "response": sample["response"],
                "retrieved_contexts": sample["retrieved_contexts"],
                "reference": sample["reference"],
            }
            for sample in samples
        ]
    )
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        run_config=RunConfig(timeout=180, max_retries=3, max_workers=4),
        batch_size=4,
        raise_exceptions=True,
    )
    return result.scores


def summarize(samples: list[dict]) -> dict:
    metric_names = [
        "faithfulness",
        "answer_relevancy",
        "context_recall",
        "context_precision",
    ]
    summary = {}
    for metric in metric_names:
        values = [float(sample[metric]) for sample in samples]
        summary[metric] = sum(values) / len(values)
    summary["average"] = sum(summary.values()) / len(metric_names)
    summary["average_latency_seconds"] = sum(
        sample["latency_seconds"] for sample in samples
    ) / len(samples)
    summary["source_hit_at_5"] = sum(
        sample["expected_source"] in sample["retrieved_sources"]
        for sample in samples
    ) / len(samples)
    return summary


def main() -> None:
    load_dotenv(ROOT / ".env", override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required")

    cases = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    model = os.getenv("LLM_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
    embedding_model = (
        os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        or "text-embedding-3-small"
    )
    client = OpenAI(api_key=api_key)
    evaluator_llm = llm_factory(model, client=client, temperature=0)
    evaluator_embeddings = OpenAIEmbeddings(
        model=embedding_model, api_key=api_key
    )

    configuration = {
        "golden_dataset_size": len(cases),
        "top_k": TOP_K,
        "generator_model": model,
        "evaluator_model": model,
        "embedding_model": embedding_model,
    }
    output = {
        "configuration": {
            **configuration,
        },
        "configs": {},
        "in_progress": {},
    }
    if OUTPUT_PATH.exists():
        saved = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        if saved.get("configuration") == configuration:
            output = saved

    for name, use_reranking in (("dense_only", False), ("hybrid_rrf", True)):
        if name in output.get("configs", {}):
            print(f"Reusing scored {name}", flush=True)
            continue
        print(f"Running {name}", flush=True)
        samples = output.get("in_progress", {}).get(name, [])
        if len(samples) != len(cases):
            samples = generate_samples(cases, use_reranking)
        output.setdefault("in_progress", {})[name] = samples
        OUTPUT_PATH.write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        scores = score_samples(samples, evaluator_llm, evaluator_embeddings)
        for sample, score in zip(samples, scores):
            sample.update({key: float(value) for key, value in score.items()})
        output["configs"][name] = {
            "summary": summarize(samples),
            "samples": samples,
        }
        output["in_progress"].pop(name, None)
        OUTPUT_PATH.write_text(
            json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(json.dumps({k: v["summary"] for k, v in output["configs"].items()}, indent=2))
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
