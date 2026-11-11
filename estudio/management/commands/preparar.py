from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Prepara la base para un despliegue: aplica migraciones y carga el plan."

    def handle(self, *args, **options):
        call_command("migrate", interactive=False)
        call_command("cargar_plan")
