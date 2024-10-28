import os
from typing import Any

import psycopg2
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creating a database for a project"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Создание базы данных для проекта"""
        db_name = os.getenv("DATABASE_NAME", default="mailing_meneger")

        conn = psycopg2.connect(
            dbname="postgres",
            host=os.getenv("DATABASE_HOST", "localhost"),
            port=os.getenv("DATABASE_PORT", "5432"),
            user=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "secret"),
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
        cur.execute(f"CREATE DATABASE {db_name}")
        cur.close()
        conn.close()

        self.stdout.write(self.style.SUCCESS(f"The «{db_name}» database has been created"))
