import logging
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine

logger = logging.getLogger("FestiveAI.Migration")

def auto_migrate_db(engine: Engine):
    """
    Lightweight, safe migration utility for SQLite / PostgreSQL to ensure
    newly added columns are automatically created without dropping tables.
    """
    # Column definitions to ensure exist: table_name -> list of (col_name, col_sql_type)
    expected_columns = {
        "style_profiles": [
            ("persona_type", "VARCHAR(100) DEFAULT 'Tech Founder & Innovator'"),
            ("industry_niche", "VARCHAR(150) DEFAULT 'Technology & Software Engineering'"),
            ("target_audience", "VARCHAR(255) DEFAULT 'Developers, Founders, and Tech Decision-Makers'"),
            ("content_pillars", "TEXT DEFAULT '{\"thought_leadership\": 35.0, \"product_showcase\": 25.0, \"behind_the_scenes\": 15.0, \"educational\": 15.0, \"festive_greeting\": 10.0}'"),
            ("post_types", "TEXT DEFAULT '[]'"),
            ("signature_hooks", "TEXT DEFAULT '[]'"),
            ("visual_archetype", "VARCHAR(50) DEFAULT 'tech_innovator'")
        ],
        "historical_posts": [
            ("post_pillar", "VARCHAR(50) DEFAULT 'thought_leadership'"),
            ("post_archetype", "VARCHAR(100) DEFAULT 'Industry Insight'")
        ],
        "publishing_campaigns": [
            ("post_pillar", "VARCHAR(50) DEFAULT 'festive_greeting'")
        ],
        "generated_creatives": [
            ("post_pillar", "VARCHAR(50) DEFAULT 'festive_greeting'")
        ]
    }

    with engine.begin() as conn:
        inspector = inspect(conn)
        existing_tables = inspector.get_table_names()

        for table_name, columns in expected_columns.items():
            if table_name not in existing_tables:
                continue
            existing_cols = {col["name"] for col in inspector.get_columns(table_name)}
            for col_name, col_def in columns:
                if col_name not in existing_cols:
                    logger.info(f"Adding missing column '{col_name}' to table '{table_name}'")
                    try:
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"))
                    except Exception as e:
                        logger.warning(f"Could not add column {col_name} to {table_name}: {e}")
