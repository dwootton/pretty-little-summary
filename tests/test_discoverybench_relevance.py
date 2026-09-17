import json
from pathlib import Path

from benchmarks.discoverybench_relevance.corpus import (
    ColumnSpec,
    RelevanceExample,
    _training_partition,
    planner_label_examples,
    relevant_column_ids,
    semantic_label_examples,
)


def column(name: str, description: str = "") -> ColumnSpec:
    return ColumnSpec(name=name, description=description, dataset="data.csv", card_id=name)


def test_silver_labels_use_answer_only_to_create_labels_not_model_input():
    columns = (
        column("household_income"),
        column("educ_years"),
        column("unrelated_identifier"),
    )

    labels = relevant_column_ids(
        "Does education predict earnings?",
        "Household income increases with educ years.",
        columns,
    )

    assert labels == ("household_income", "educ_years")


def test_group_partition_is_stable_and_has_no_random_state():
    assert _training_partition("discoverybench/synth/train/example") == _training_partition(
        "discoverybench/synth/train/example"
    )
    assert _training_partition("discoverybench/synth/train/example") in {"train", "validation"}


def test_planner_audit_uses_only_exact_normalized_schema_matches(tmp_path: Path):
    example = RelevanceExample(
        task_id="task-1",
        partition="test",
        source_split="test",
        kind="synthetic",
        dataset_group="group",
        question="question",
        columns=(column("household_income"), column("age")),
        positive_card_ids=("age",),
    )
    raw = {
        "results": {
            "hypothesis-executor-gpt-oss-120b": [
                {
                    "task_id": "task-1",
                    "executor": {
                        "analysis_plan": {"required_variables": ["Household Income", "not_a_column"]}
                    },
                }
            ]
        }
    }
    path = tmp_path / "raw.json"
    path.write_text(json.dumps(raw))

    audited = planner_label_examples([example], path)

    assert audited[0].positive_card_ids == ("household_income",)


def test_semantic_audit_removes_positive_columns_named_in_the_question():
    example = RelevanceExample(
        task_id="task-1",
        partition="test",
        source_split="test",
        kind="real",
        dataset_group="group",
        question="Does education predict earnings?",
        columns=(column("education"), column("household_income")),
        positive_card_ids=("education", "household_income"),
    )

    semantic = semantic_label_examples([example])

    assert semantic[0].positive_card_ids == ("household_income",)
