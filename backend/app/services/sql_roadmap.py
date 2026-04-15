"""Load and assemble roadmap data from the SQL seed files in backend/data."""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import re
from typing import Any


_SQL_FILES = (
    "faculties.sql",
    "fields.sql",
    "roadmaps.sql",
    "stages.sql",
    "skills.sql",
    "resources.sql",
)

_INSERT_PATTERN = re.compile(
    r"INSERT\s+INTO\s+(?P<table>\w+)\s*\((?P<columns>.*?)\)\s*VALUES\s*(?P<values>.*?);",
    re.IGNORECASE | re.DOTALL,
)

_PRIMARY_KEYS = {
    "faculties": "faculty_id",
    "fields": "field_id",
    "roadmaps": "roadmap_id",
    "stages": "stage_id",
    "skills": "skill_id",
    "resources": "resource_id",
    "students": "student_id",
    "student_skill_progress": "progress_id",
    "certifications": "certification_id",
}


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


def _strip_sql_comments(text: str) -> str:
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        if "--" in line:
            line = line.split("--", 1)[0]
        cleaned_lines.append(line.rstrip())
    return "\n".join(cleaned_lines)


def _parse_value(value: str) -> Any:
    cleaned = value.strip()
    if not cleaned:
        return ""
    if cleaned.upper() == "NULL":
        return None
    if re.fullmatch(r"-?\d+", cleaned):
        return int(cleaned)
    return cleaned


def _parse_values_block(values_block: str) -> list[list[Any]]:
    rows: list[list[Any]] = []
    current_row: list[Any] = []
    current_token: list[str] = []
    in_string = False
    depth = 0
    index = 0

    while index < len(values_block):
        char = values_block[index]

        if in_string:
            if char == "'":
                if index + 1 < len(values_block) and values_block[index + 1] == "'":
                    current_token.append("'")
                    index += 2
                    continue
                in_string = False
                index += 1
                continue
            current_token.append(char)
            index += 1
            continue

        if char == "'":
            in_string = True
            index += 1
            continue

        if char == "(":
            if depth > 0:
                current_token.append(char)
            depth += 1
            index += 1
            continue

        if char == ")":
            depth -= 1
            if depth > 0:
                current_token.append(char)
            else:
                current_row.append(_parse_value("".join(current_token)))
                rows.append(current_row)
                current_row = []
                current_token = []
            index += 1
            continue

        if char == "," and depth == 1:
            current_row.append(_parse_value("".join(current_token)))
            current_token = []
            index += 1
            continue

        if depth >= 1:
            current_token.append(char)

        index += 1

    return rows


def _load_sql_tables() -> dict[str, list[dict[str, Any]]]:
    tables: dict[str, list[dict[str, Any]]] = defaultdict(list)
    counters: dict[str, int] = defaultdict(int)

    for filename in _SQL_FILES:
        path = _data_dir() / filename
        if not path.exists():
            continue

        text = _strip_sql_comments(path.read_text(encoding="utf-8"))
        for match in _INSERT_PATTERN.finditer(text):
            table = match.group("table").lower()
            columns = [column.strip() for column in match.group("columns").split(",")]
            rows = _parse_values_block(match.group("values"))

            for row in rows:
                if len(row) != len(columns):
                    continue
                record = dict(zip(columns, row))
                primary_key = _PRIMARY_KEYS.get(table)
                if primary_key and primary_key not in record:
                    counters[table] += 1
                    record[primary_key] = counters[table]
                tables[table].append(record)

    return tables


@lru_cache(maxsize=1)
def load_roadmap_catalog() -> dict[str, list[dict[str, Any]]]:
    return _load_sql_tables()


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _initials(text: str) -> str:
    return "".join(part[0] for part in _normalize(text).split() if part)


def _match_score(haystack: str, terms: list[str]) -> int:
    haystack_norm = _normalize(haystack)
    haystack_initials = _initials(haystack)
    score = 0

    for term in terms:
        term_norm = _normalize(term)
        if not term_norm:
            continue

        if term_norm == haystack_norm:
            score += 100
        if term_norm == haystack_initials:
            score += 90
        if term_norm in haystack_norm or haystack_norm in term_norm:
            score += 60

        term_words = term_norm.split()
        score += sum(10 for word in term_words if word and word in haystack_norm)

    return score


def _select_field(tables: dict[str, list[dict[str, Any]]], department: str, interests: list[str], target_career: str) -> dict[str, Any] | None:
    fields = tables.get("fields", [])
    if not fields:
        return None

    search_terms = [department, target_career, *interests]
    best_field = fields[0]
    best_score = -1

    for field in fields:
        related_text = " ".join(
            str(part)
            for part in (
                field.get("field_name", ""),
                field.get("description", ""),
            )
            if part
        )
        score = _match_score(related_text, search_terms)
        if score > best_score:
            best_field = field
            best_score = score

    return best_field


def _preferred_resource(resources: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not resources:
        return None

    for resource in resources:
        if _normalize(str(resource.get("resource_type", ""))) == "course":
            return resource

    return resources[0]


def _starting_stage_index(level: int) -> int:
    if level >= 300:
        return 2
    if level >= 200:
        return 1
    return 0


def _matches_completed_skill(
    skill_name: str,
    description: str,
    completed_courses: list[str],
) -> bool:
    skill_norm = _normalize(skill_name)
    skill_terms = set(skill_norm.split())
    skill_terms.update(_normalize(description).split())
    skill_terms = {term for term in skill_terms if term}

    if not skill_terms:
        return False

    for completed in completed_courses:
        completed_norm = _normalize(completed)
        if not completed_norm:
            continue

        if (
            completed_norm == skill_norm
            or completed_norm in skill_norm
            or skill_norm in completed_norm
        ):
            return True

        completed_terms = set(completed_norm.split())
        overlap = skill_terms & completed_terms
        if len(overlap) >= 2:
            return True

        if overlap and any(term not in {"basic", "basics", "intro", "introduction", "overview"} for term in overlap):
            return True

    return False


def build_sql_roadmap(
    level: int,
    interests: list[str],
    completed_courses: list[str],
    target_career: str = "",
    skills: list[str] | None = None,
    department: str = "Computer Science",
) -> dict[str, Any]:
    tables = load_roadmap_catalog()
    field = _select_field(tables, department, interests, target_career)

    if not field:
        return {"roadmap": [], "sources": [f"{name}" for name in _SQL_FILES]}

    roadmaps = [
        roadmap
        for roadmap in tables.get("roadmaps", [])
        if roadmap.get("field_id") == field.get("field_id")
    ]
    roadmap = roadmaps[0] if roadmaps else None
    if not roadmap:
        return {"roadmap": [], "sources": [f"{name}" for name in _SQL_FILES]}

    stages = sorted(
        [
            stage
            for stage in tables.get("stages", [])
            if stage.get("roadmap_id") == roadmap.get("roadmap_id")
        ],
        key=lambda stage: int(stage.get("stage_order", 0)),
    )

    completed = {_normalize(course) for course in completed_courses if course}
    start_index = min(_starting_stage_index(level), max(len(stages) - 1, 0))
    roadmap_nodes: list[dict[str, Any]] = []

    for stage in stages[start_index:]:
        stage_id = stage.get("stage_id")
        stage_name = str(stage.get("stage_name", "Stage"))
        stage_skills = sorted(
            [
                skill
                for skill in tables.get("skills", [])
                if skill.get("stage_id") == stage_id
                and not _matches_completed_skill(
                    str(skill.get("skill_name", "")),
                    str(skill.get("description", "")),
                    completed_courses,
                )
            ],
            key=lambda skill: int(skill.get("skill_order", 0)),
        )

        if not stage_skills:
            continue

        course_lines: list[str] = []
        for skill in stage_skills:
            skill_name = str(skill.get("skill_name", "Unnamed Skill"))
            description = str(skill.get("description", "")).strip()

            related_resources = [
                resource
                for resource in tables.get("resources", [])
                if resource.get("skill_id") == skill.get("skill_id")
            ]
            resource = _preferred_resource(related_resources)

            course_line = skill_name
            if description:
                course_line = f"{course_line} - {description}"
            if resource:
                resource_title = str(resource.get("title", "")).strip()
                provider = str(resource.get("provider", "")).strip()
                if resource_title and provider:
                    course_line += f" | Suggested resource: {resource_title} ({provider})"
                elif resource_title:
                    course_line += f" | Suggested resource: {resource_title}"

            course_lines.append(course_line)

        roadmap_nodes.append(
            {
                "semester": f"{field.get('field_name', 'Roadmap')} — {stage_name}",
                "courses": course_lines,
            }
        )

    return {
        "roadmap": roadmap_nodes,
        "sources": [f"{name}" for name in _SQL_FILES],
    }


def build_sql_knowledge_graph(
    career_sector: str,
    department: str = "Computer Science",
) -> dict[str, Any]:
    tables = load_roadmap_catalog()
    field = _select_field(tables, department, [career_sector], career_sector)

    if not field:
        return {"pillars": [], "dependencies": [], "sources": [f"{name}" for name in _SQL_FILES]}

    roadmaps = [
        roadmap
        for roadmap in tables.get("roadmaps", [])
        if roadmap.get("field_id") == field.get("field_id")
    ]
    roadmap = roadmaps[0] if roadmaps else None
    if not roadmap:
        return {"pillars": [], "dependencies": [], "sources": [f"{name}" for name in _SQL_FILES]}

    stages = sorted(
        [
            stage
            for stage in tables.get("stages", [])
            if stage.get("roadmap_id") == roadmap.get("roadmap_id")
        ],
        key=lambda stage: int(stage.get("stage_order", 0)),
    )

    pillars: list[dict[str, Any]] = []
    dependencies: list[dict[str, str]] = []
    previous_pillar_id = ""

    for stage in stages:
        stage_id = stage.get("stage_id")
        stage_name = str(stage.get("stage_name", "Stage"))
        stage_skills = sorted(
            [
                skill
                for skill in tables.get("skills", [])
                if skill.get("stage_id") == stage_id
            ],
            key=lambda skill: int(skill.get("skill_order", 0)),
        )

        courses: list[str] = []
        for skill in stage_skills:
            skill_name = str(skill.get("skill_name", "Unnamed Skill"))
            description = str(skill.get("description", "")).strip()
            related_resources = [
                resource
                for resource in tables.get("resources", [])
                if resource.get("skill_id") == skill.get("skill_id")
            ]
            resource = _preferred_resource(related_resources)

            course_line = skill_name
            if description:
                course_line = f"{course_line} - {description}"
            if resource:
                resource_title = str(resource.get("title", "")).strip()
                provider = str(resource.get("provider", "")).strip()
                if resource_title and provider:
                    course_line += f" | Suggested resource: {resource_title} ({provider})"
                elif resource_title:
                    course_line += f" | Suggested resource: {resource_title}"

            courses.append(course_line)

        pillar_id = f"{_normalize(str(field.get('field_name', 'field'))).replace(' ', '_')}_{_normalize(stage_name).replace(' ', '_')}"
        pillars.append(
            {
                "id": pillar_id,
                "label": stage_name,
                "description": f"Core {stage_name.lower()} skills for {field.get('field_name', 'the field')}.",
                "courses": courses,
            }
        )

        if previous_pillar_id:
            dependencies.append(
                {
                    "from_pillar": previous_pillar_id,
                    "to_pillar": pillar_id,
                }
            )
        previous_pillar_id = pillar_id

    return {
        "pillars": pillars,
        "dependencies": dependencies,
        "sources": [f"{name}" for name in _SQL_FILES],
    }