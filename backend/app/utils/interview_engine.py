"""Rule-based NLP interview engine.

Generates role-relevant interview questions from a candidate's skill profile
and evaluates free-text answers using TF-IDF similarity against per-skill
reference keywords (mirrors the ATS matching approach used elsewhere).
"""
# Curated question templates + evaluation keywords for common skills.
# Keys are lowercase skill names; values are (display name, reference keywords).
SKILL_TOPICS = {
    "python": (
        "Python",
        [
            "python", "list", "dict", "loop", "function", "class", "exception",
            "decorator", "generator", "pip", "pandas", "oop", "duck typing",
        ],
    ),
    "django": (
        "Django",
        [
            "django", "model", "view", "template", "migration", "orm", "queryset",
            "middleware", "rest framework", "urls", "form",
        ],
    ),
    "fastapi": (
        "FastAPI",
        [
            "fastapi", "async", "endpoint", "pydantic", "dependency injection",
            "rest", "openapi", "router", "websocket", "status code",
        ],
    ),
    "react": (
        "React",
        [
            "react", "component", "hook", "state", "props", "jsx", "reducer",
            "useeffect", "context", "virtual dom", "key", "memo",
        ],
    ),
    "javascript": (
        "JavaScript",
        [
            "javascript", "closure", "promise", "async", "event loop", "prototype",
            "arrow function", "dom", "json", "callback",
        ],
    ),
    "typescript": (
        "TypeScript",
        [
            "typescript", "type", "interface", "enum", "generic", "any", "union",
            "strict", "compile", "module",
        ],
    ),
    "java": (
        "Java",
        [
            "java", "jvm", "thread", "collection", "interface", "inheritance",
            "garbage collection", "spring", "maven", "exception",
        ],
    ),
    "sql": (
        "SQL",
        [
            "sql", "select", "join", "index", "query", "group by", "transaction",
            "normalization", "foreign key", "primary key", "aggregate",
        ],
    ),
    "postgresql": (
        "PostgreSQL",
        [
            "postgresql", "postgres", "query", "index", "json", "transaction",
            "constraint", "vacuum", "explain", "schema", "partition",
        ],
    ),
    "docker": (
        "Docker",
        [
            "docker", "container", "image", "dockerfile", "volume", "compose",
            "registry", "layer", "orchestration", "mount",
        ],
    ),
    "kubernetes": (
        "Kubernetes",
        [
            "kubernetes", "pod", "service", "deployment", "namespace", "container",
            "helm", "ingress", "configmap", "scale",
        ],
    ),
    "aws": (
        "AWS",
        [
            "aws", "ec2", "s3", "lambda", "iam", "cloudformation", "vpc",
            "cloud", "serverless", "autoscaling", "terraform",
        ],
    ),
    "azure": (
        "Azure",
        [
            "azure", "cloud", "function", "storage", "active directory", "virtual machine",
            "resource group", "devops", "app service",
        ],
    ),
    "machine learning": (
        "Machine Learning",
        [
            "machine learning", "model", "training", "overfitting", "feature",
            "dataset", "supervised", "accuracy", "precision", "recall", "pipeline",
        ],
    ),
    "deep learning": (
        "Deep Learning",
        [
            "deep learning", "neural network", "backpropagation", "layer",
            "activation", "dropout", "cuda", "tensorflow", "pytorch", "gradient",
        ],
    ),
    "git": (
        "Git",
        [
            "git", "commit", "branch", "merge", "rebase", "pull request", "stash",
            "conflict", "remote", "log",
        ],
    ),
    "node.js": (
        "Node.js",
        [
            "node", "npm", "event loop", "callback", "express", "module", "async",
            "buffer", "stream", "cluster",
        ],
    ),
    "express": (
        "Express.js",
        [
            "express", "middleware", "route", "request", "response", "crud",
            "rest", "body parser", "session", "error handler",
        ],
    ),
    "html": (
        "HTML",
        [
            "html", "semantic", "tag", "attribute", "form", "accessibility",
            "doctype", "meta", "canvas", "svg",
        ],
    ),
    "css": (
        "CSS",
        [
            "css", "flexbox", "grid", "selector", "media query", "position",
            "animation", "spacing", "responsive", "preprocessor",
        ],
    ),
    "mongodb": (
        "MongoDB",
        [
            "mongodb", "document", "collection", "aggregation", "index",
            "nosql", "objectid", "shard", "replica", "schema",
        ],
    ),
    "redis": (
        "Redis",
        [
            "redis", "cache", "key", "in-memory", "pub/sub", "ttl", "sorted set",
            "message queue", "session store", "latency",
        ],
    ),
    "c++": (
        "C++",
        [
            "c++", "pointer", "memory", "template", "class", "smart pointer",
            "stl", "copy", "move", "polymorphism",
        ],
    ),
    "c": (
        "C",
        [
            "c", "pointer", "struct", "memory", "memset", "stack", "heap",
            "macro", "compile", "array",
        ],
    ),
    "go": (
        "Go",
        [
            "golang", "goroutine", "channel", "interface", "defer", "struct",
            "concurrency", "error", "package", "garbage collection",
        ],
    ),
    "rust": (
        "Rust",
        [
            "rust", "ownership", "borrow", "lifetime", "trait", "memory safety",
            "pattern", "cargo", "crate", "concurrency",
        ],
    ),
    "tensorflow": (
        "TensorFlow",
        [
            "tensorflow", "tensor", "keras", "model", "layer", "gradient",
            "loss", "optimizer", "graph", "training",
        ],
    ),
    "pytorch": (
        "PyTorch",
        [
            "pytorch", "tensor", "autograd", "model", "dataloader", "loss",
            "optimizer", "gpu", "backprop", "training",
        ],
    ),
    "flask": (
        "Flask",
        [
            "flask", "route", "app", "blueprint", "jinja", "request", "rest",
            "session", "decorator", "wsgi",
        ],
    ),
    "spring": (
        "Spring",
        [
            "spring", "bean", "dependency injection", "autowired", "repository",
            "service", "controller", "spring boot", "jpa", "aop",
        ],
    ),
    "kotlin": (
        "Kotlin",
        [
            "kotlin", "coroutine", "data class", "null safety", "extension",
            "lambda", "flow", "suspend", "jvm", "sealed class",
        ],
    ),
    "rest api": (
        "REST API",
        [
            "rest", "api", "http", "status code", "resource", "json",
            "authentication", "idempotent", "rate limiting", "versioning",
        ],
    ),
}

# Fallback template used when a skill is not in the curated topics map.
GENERIC_TEMPLATES = [
    "Explain what {skill} is and when you would choose it in a project.",
    "Walk us through a past project where you used {skill}. What was your role?",
    "What are common pitfalls with {skill} and how do you avoid them?",
]

# Reference keywords for the STAR / behavioral questions.
BEHAVIORAL_QUESTIONS = [
    {
        "question": "Tell us about a challenging project you worked on. What made it difficult and how did you overcome it?",
        "category": "behavioral",
        "target_skill": "problem solving",
        "keywords": [
            "challenging", "project", "difficult", "overcome", "problem", "solution",
            "team", "deadline", "pressure", "learn", "result", "priority",
        ],
    },
    {
        "question": "Describe a time you had to learn a new technology quickly to complete a task.",
        "category": "behavioral",
        "target_skill": "learning agility",
        "keywords": [
            "learn", "new", "technology", "quickly", "task", "documentation",
            "tutorial", "practice", "shipped", "deadline", "curious", "knowledge",
        ],
    },
]


def _normalize_skill(skill: str) -> str:
    return skill.strip().lower().replace(" ", " ")


def _topic_key_for(skill: str):
    key = _normalize_skill(skill)
    # direct match first
    if key in SKILL_TOPICS:
        return key
    # suffix match e.g. "backend python" -> "python"
    for part in key.split():
        if part in SKILL_TOPICS:
            return part
    return None


def generate_interview_questions(
    skills: list[str],
    job_skills: list[str] | None = None,
    total: int = 8,
) -> list[dict]:
    """Builds a balanced set of technical + behavioral interview questions."""
    questions = []

    # Prefer the role's required skills, fall back to the candidate's own skills.
    topic_sources = job_skills or skills or []
    seen = set()
    technical_topics = []
    for skill in topic_sources:
        key = _topic_key_for(skill)
        norm = _normalize_skill(skill)
        if norm in seen:
            continue
        seen.add(norm)
        technical_topics.append((key, norm))

    if not technical_topics:
        technical_topics = [("rest api", "REST API")]

    tech_questions = min(len(technical_topics), max(total - 2, 3))
    behavior_questions = BEHAVIORAL_QUESTIONS[: max(total - tech_questions, 2)]

    for idx, (key, raw_skill) in enumerate(technical_topics[:tech_questions]):
        qid = f"q{idx + 1}"
        display_name = SKILL_TOPICS[key][0] if key else raw_skill.title()
        keywords = SKILL_TOPICS[key][1] if key else [raw_skill.lower()]

        if key:
            question = (
                f"Explain how you have used {display_name} in a real project. "
                f"What are the core concepts every developer should know about {display_name}?"
            )
        else:
            question = GENERIC_TEMPLATES[0].format(skill=raw_skill)

        questions.append({
            "id": qid,
            "question": question,
            "category": "technical",
            "target_skill": display_name,
            "keywords": keywords,
        })

    for q in behavior_questions:
        questions.append({
            "id": f"b{len(questions) + 1}",
            "question": q["question"],
            "category": "behavioral",
            "target_skill": q["target_skill"],
            "keywords": q["keywords"],
        })

    return questions[:total]


def _text_similarity(text_a: str, text_b: str) -> float:
    """Returns 0-100 cosine similarity between two text snippets."""
    try:
        # Imported here rather than at module scope: scikit-learn takes several
        # seconds to import, so it stays off the API's startup path.
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([text_a, text_b])
        value = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(float(value) * 100, 2)
    except Exception:
        return 0.0


def _evaluate_single_answer(answer: str, keywords: list[str]) -> dict:
    if not answer or not answer.strip():
        return {"score": 0.0, "feedback": "No answer provided."}

    kw_text = " ".join(keywords)
    similarity = _text_similarity(answer, kw_text)
    word_count = len(answer.split())
    completeness = min(word_count / 25.0, 1.0) * 100.0

    score = round(similarity * 0.6 + completeness * 0.4, 2)

    if score >= 70:
        feedback = "Strong, well-structured answer covering key points."
    elif score >= 50:
        feedback = "Reasonable answer; consider going deeper and naming concrete tools or techniques."
    else:
        feedback = "Answer is thin on core concepts; review the fundamentals and add specifics or examples."
    return {"score": score, "feedback": feedback}


def evaluate_interview_answers(responses: list[dict]) -> dict:
    """Evaluates a list of {id, question, category, target_skill, keywords, answer}."""
    per_question = []
    scores = []
    for r in responses:
        score_info = _evaluate_single_answer(r.get("answer", ""), r.get("keywords") or [])
        per_question.append({
            "id": r.get("id"),
            "question": r.get("question"),
            "category": r.get("category", "technical"),
            "target_skill": r.get("target_skill", ""),
            "score": score_info["score"],
            "feedback": score_info["feedback"],
        })
        scores.append(score_info["score"])

    overall = round(sum(scores) / len(scores), 2) if scores else 0.0

    strengths = []
    improvements = []
    for item in per_question:
        if item["score"] >= 70:
            strengths.append(
                f"Strong answer on {item['target_skill'] or item['category']} "
                f"({item['score']}/100)."
            )
        elif item["score"] < 55:
            area = item["target_skill"] or item["category"]
            improvements.append(
                f"Improve {area}: revise fundamentals and practice with concrete examples "
                f"({item['score']}/100)."
            )

    if not strengths:
        strengths.append("Be more specific — include project context and concrete terminology next time.")
    if not improvements:
        improvements.append("Keep practicing; answers were consistently solid.")

    feedback_lines = [
        f"You scored {overall}/100 across {len(per_question)} questions.",
        "Review the per-question scores below and focus practice on the lowest areas.",
    ]
    feedback = " ".join(feedback_lines)

    return {
        "overall_score": overall,
        "feedback": feedback,
        "strengths": "; ".join(strengths),
        "improvements": "; ".join(improvements),
        "per_question": per_question,
    }