"""Canonical technical skill ontology, alias definitions, and categorization."""

from typing import Dict, List, Optional, Set
from pydantic import BaseModel


class SkillDefinition(BaseModel):
    """Ontological definition of a canonical skill."""

    canonical_name: str
    category: str  # e.g., "language", "framework", "database", "cloud_devops", "ai_ml", "tool"
    aliases: List[str]
    case_sensitive: bool = False
    is_technical_tool: bool = False
    negative_lookahead: Optional[str] = None
    custom_regex: Optional[str] = None


# Comprehensive Canonical Skill Ontology
CANONICAL_SKILLS: List[SkillDefinition] = [
    # --- Programming Languages ---
    SkillDefinition(
        canonical_name="Python",
        category="language",
        aliases=["python", "python3", "py3"],
    ),
    SkillDefinition(
        canonical_name="JavaScript",
        category="language",
        aliases=["javascript", "js", "ecmascript", "es6", "es2015"],
    ),
    SkillDefinition(
        canonical_name="TypeScript",
        category="language",
        aliases=["typescript", "ts"],
    ),
    SkillDefinition(
        canonical_name="Java",
        category="language",
        aliases=["java", "core java", "j2ee"],
        negative_lookahead=r"(?!script|[\w])",
    ),
    SkillDefinition(
        canonical_name="Go",
        category="language",
        aliases=["golang", "go programming", "go language"],
        custom_regex=r"(?:\bGolang\b|\bGo\s+language\b|\bGo\s+programming\b|(?<=[,\/\|\(])\s*Go\s*(?=[,\/\|\)]))",
    ),
    SkillDefinition(
        canonical_name="C++",
        category="language",
        aliases=["c++", "cpp"],
        custom_regex=r"(?:\bC\+\+(?![\+\w])|\bcpp\b)",
    ),
    SkillDefinition(
        canonical_name="C#",
        category="language",
        aliases=["c#", "csharp", "c-sharp"],
        custom_regex=r"(?:\bC#(?![\#\w])|\bcsharp\b|\bc-sharp\b)",
    ),
    SkillDefinition(
        canonical_name="C",
        category="language",
        aliases=["c programming", "c language"],
        custom_regex=r"(?:\bC\s+programming\b|\bC\s+language\b|(?<=[,\/])\s*C\s*(?=[,\/]))",
    ),
    SkillDefinition(
        canonical_name="Rust",
        category="language",
        aliases=["rust", "rust-lang", "rustlang"],
    ),
    SkillDefinition(
        canonical_name="Ruby",
        category="language",
        aliases=["ruby", "ruby-lang"],
    ),
    SkillDefinition(
        canonical_name="PHP",
        category="language",
        aliases=["php", "php7", "php8"],
    ),
    SkillDefinition(
        canonical_name="Swift",
        category="language",
        aliases=["swift", "swiftui"],
    ),
    SkillDefinition(
        canonical_name="Kotlin",
        category="language",
        aliases=["kotlin"],
    ),
    SkillDefinition(
        canonical_name="SQL",
        category="language",
        aliases=["sql", "t-sql", "pl/sql", "plsql", "structured query language"],
    ),
    SkillDefinition(
        canonical_name="HTML",
        category="language",
        aliases=["html", "html5"],
    ),
    SkillDefinition(
        canonical_name="CSS",
        category="language",
        aliases=["css", "css3", "sass", "scss", "less"],
    ),
    SkillDefinition(
        canonical_name="Bash",
        category="language",
        aliases=["bash", "shell scripting", "sh", "zsh", "powershell"],
    ),
    SkillDefinition(
        canonical_name="Scala",
        category="language",
        aliases=["scala"],
    ),
    SkillDefinition(
        canonical_name="R",
        category="language",
        aliases=["r programming", "r language"],
        custom_regex=r"(?:\bR\s+programming\b|\bR\s+language\b|(?<=[,\/])\s*R\s*(?=[,\/]))",
    ),
    SkillDefinition(
        canonical_name="Dart",
        category="language",
        aliases=["dart"],
    ),

    # --- Frameworks & Libraries ---
    SkillDefinition(
        canonical_name="React",
        category="framework",
        aliases=["react", "react.js", "reactjs", "react-native", "react native"],
    ),
    SkillDefinition(
        canonical_name="Node.js",
        category="framework",
        aliases=["node.js", "nodejs", "node", "node js"],
    ),
    SkillDefinition(
        canonical_name="Next.js",
        category="framework",
        aliases=["next.js", "nextjs", "next js"],
    ),
    SkillDefinition(
        canonical_name="Express.js",
        category="framework",
        aliases=["express", "express.js", "expressjs", "express js"],
    ),
    SkillDefinition(
        canonical_name="Angular",
        category="framework",
        aliases=["angular", "angular.js", "angularjs", "angular 2+"],
    ),
    SkillDefinition(
        canonical_name="Vue.js",
        category="framework",
        aliases=["vue", "vue.js", "vuejs", "vue 3"],
    ),
    SkillDefinition(
        canonical_name="FastAPI",
        category="framework",
        aliases=["fastapi", "fast-api", "fast api"],
    ),
    SkillDefinition(
        canonical_name="Django",
        category="framework",
        aliases=["django", "django rest framework", "drf"],
    ),
    SkillDefinition(
        canonical_name="Flask",
        category="framework",
        aliases=["flask"],
    ),
    SkillDefinition(
        canonical_name="Spring Boot",
        category="framework",
        aliases=["spring boot", "springboot", "spring framework", "spring"],
    ),
    SkillDefinition(
        canonical_name="ASP.NET",
        category="framework",
        aliases=["asp.net", "asp.net core", ".net", ".net core", "dotnet"],
    ),
    SkillDefinition(
        canonical_name="NestJS",
        category="framework",
        aliases=["nestjs", "nest.js", "nest js"],
    ),
    SkillDefinition(
        canonical_name="Ruby on Rails",
        category="framework",
        aliases=["ruby on rails", "rails", "ror"],
    ),
    SkillDefinition(
        canonical_name="Laravel",
        category="framework",
        aliases=["laravel"],
    ),
    SkillDefinition(
        canonical_name="Svelte",
        category="framework",
        aliases=["svelte", "sveltekit"],
    ),

    # --- Databases & Data Stores ---
    SkillDefinition(
        canonical_name="PostgreSQL",
        category="database",
        aliases=["postgresql", "postgres", "psql", "pgsql"],
    ),
    SkillDefinition(
        canonical_name="MongoDB",
        category="database",
        aliases=["mongodb", "mongo", "mongoose"],
    ),
    SkillDefinition(
        canonical_name="MySQL",
        category="database",
        aliases=["mysql"],
    ),
    SkillDefinition(
        canonical_name="Redis",
        category="database",
        aliases=["redis"],
    ),
    SkillDefinition(
        canonical_name="SQLite",
        category="database",
        aliases=["sqlite", "sqlite3"],
    ),
    SkillDefinition(
        canonical_name="Elasticsearch",
        category="database",
        aliases=["elasticsearch", "elastic search", "opensearch", "elk"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="DynamoDB",
        category="database",
        aliases=["dynamodb", "dynamo db", "aws dynamodb"],
    ),
    SkillDefinition(
        canonical_name="Cassandra",
        category="database",
        aliases=["cassandra", "apache cassandra"],
    ),
    SkillDefinition(
        canonical_name="Snowflake",
        category="database",
        aliases=["snowflake"],
    ),
    SkillDefinition(
        canonical_name="Firebase",
        category="database",
        aliases=["firebase", "firestore"],
        is_technical_tool=True,
    ),

    # --- Cloud & DevOps Infrastructure ---
    SkillDefinition(
        canonical_name="AWS",
        category="cloud_devops",
        aliases=["aws", "amazon web services", "amazon ec2", "aws s3", "aws lambda"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Google Cloud Platform",
        category="cloud_devops",
        aliases=["google cloud", "google cloud platform", "gcp"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Microsoft Azure",
        category="cloud_devops",
        aliases=["azure", "microsoft azure", "azure cloud"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Docker",
        category="cloud_devops",
        aliases=["docker", "dockerfile", "docker-compose", "docker compose"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Kubernetes",
        category="cloud_devops",
        aliases=["kubernetes", "k8s", "kube"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Terraform",
        category="cloud_devops",
        aliases=["terraform", "hcl"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Ansible",
        category="cloud_devops",
        aliases=["ansible"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Jenkins",
        category="cloud_devops",
        aliases=["jenkins"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="GitHub Actions",
        category="cloud_devops",
        aliases=["github actions", "gh actions", "github action"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="GitLab CI",
        category="cloud_devops",
        aliases=["gitlab ci", "gitlab-ci", "gitlab ci/cd"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Linux",
        category="cloud_devops",
        aliases=["linux", "ubuntu", "debian", "centos", "redhat", "alpine"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Nginx",
        category="cloud_devops",
        aliases=["nginx"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Prometheus",
        category="cloud_devops",
        aliases=["prometheus"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Grafana",
        category="cloud_devops",
        aliases=["grafana"],
        is_technical_tool=True,
    ),

    # --- AI & Machine Learning ---
    SkillDefinition(
        canonical_name="Machine Learning",
        category="ai_ml",
        aliases=["machine learning", "ml", "statistical learning"],
    ),
    SkillDefinition(
        canonical_name="Deep Learning",
        category="ai_ml",
        aliases=["deep learning", "neural networks", "cnn", "rnn", "lstm"],
    ),
    SkillDefinition(
        canonical_name="PyTorch",
        category="ai_ml",
        aliases=["pytorch", "torch"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="TensorFlow",
        category="ai_ml",
        aliases=["tensorflow", "tf", "keras"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Scikit-Learn",
        category="ai_ml",
        aliases=["scikit-learn", "scikitlearn", "sklearn"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Pandas",
        category="ai_ml",
        aliases=["pandas"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="NumPy",
        category="ai_ml",
        aliases=["numpy"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Natural Language Processing",
        category="ai_ml",
        aliases=["nlp", "natural language processing", "text mining"],
    ),
    SkillDefinition(
        canonical_name="Computer Vision",
        category="ai_ml",
        aliases=["computer vision", "cv", "opencv", "image processing"],
    ),
    SkillDefinition(
        canonical_name="Hugging Face",
        category="ai_ml",
        aliases=["hugging face", "huggingface", "transformers", "sentence-transformers"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="spaCy",
        category="ai_ml",
        aliases=["spacy"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="LangChain",
        category="ai_ml",
        aliases=["langchain", "llamaindex", "rag"],
        is_technical_tool=True,
    ),

    # --- Architecture, Tools & Practices ---
    SkillDefinition(
        canonical_name="REST API",
        category="architecture",
        aliases=["rest", "rest api", "restful", "rest apis", "restful api"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="GraphQL",
        category="architecture",
        aliases=["graphql", "apollo graphql"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Microservices",
        category="architecture",
        aliases=["microservices", "microservice architecture", "distributed systems"],
    ),
    SkillDefinition(
        canonical_name="Git",
        category="tool",
        aliases=["git", "github", "gitlab", "bitbucket"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="CI/CD",
        category="tool",
        aliases=["ci/cd", "cicd", "continuous integration", "continuous deployment"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Kafka",
        category="tool",
        aliases=["kafka", "apache kafka"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="RabbitMQ",
        category="tool",
        aliases=["rabbitmq", "amqp"],
        is_technical_tool=True,
    ),
    SkillDefinition(
        canonical_name="Agile",
        category="tool",
        aliases=["agile", "scrum", "kanban", "sprint"],
    ),
    SkillDefinition(
        canonical_name="Jira",
        category="tool",
        aliases=["jira", "confluence"],
        is_technical_tool=True,
    ),
]


def get_canonical_ontology() -> List[SkillDefinition]:
    """Retrieve the full list of canonical skill definitions."""
    return CANONICAL_SKILLS


def get_canonical_names() -> Set[str]:
    """Retrieve set of unique canonical skill names."""
    return {s.canonical_name for s in CANONICAL_SKILLS}
