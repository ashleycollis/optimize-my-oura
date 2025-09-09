from django.db.backends.postgresql.base import DatabaseWrapper as PGDatabaseWrapper


class DatabaseWrapper(PGDatabaseWrapper):
    def _configure_timezone(self, connection):
        # Override to avoid executing SET TIME ZONE which fails on some PG setups
        return None


