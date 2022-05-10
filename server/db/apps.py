from django.apps import AppConfig


class DbConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "db"

    def ready(self):
        from container import wire_container  # noqa PLC0415

        wire_container()  # type: ignore
