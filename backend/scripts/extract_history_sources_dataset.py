import json
from pathlib import Path


SOURCE_HINTS = (
    "source",
    "study source",
    "source a",
    "source b",
    "source c",
    "cartoon",
    "poster",
    "photograph",
)


def is_source_question(question_text: str) -> bool:
    normalized = question_text.lower().strip()
    return any(hint in normalized for hint in SOURCE_HINTS)


def main():
    root_dir = Path(__file__).resolve().parents[2]
    input_path = root_dir / "data" / "history_data.json"
    output_path = root_dir / "data" / "history_sources" / "paper1_sources_dataset.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    entries = []

    def walk(node, path):
        if isinstance(node, dict):
            if "question" in node and isinstance(node.get("question"), str):
                question = node.get("question", "")
                marks = node.get("marks")
                if is_source_question(question) and marks in (3, 5):
                    entries.append(
                        {
                            "year": "unknown",
                            "session": "unknown",
                            "paper": "paper_1_sources",
                            "question": question,
                            "marks": marks,
                            "answer_sample": node.get("answer", ""),
                            "mark_scheme_points": node.get("mark_scheme_points", node.get("points", [])),
                            "examiner_tips": node.get("examiner_tips", []),
                            "origin_path": ".".join(path),
                        }
                    )

            for key, value in node.items():
                walk(value, path + [str(key)])
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                walk(item, path + [str(idx)])

    walk(data, [])

    dataset = {
        "dataset_name": "history_sources_paper1",
        "source": "Extracted from local history_data past_papers (Papacambridge-origin structured data)",
        "total_entries": len(entries),
        "entries": entries,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(entries)} entries to {output_path}")


if __name__ == "__main__":
    main()
