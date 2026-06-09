from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0003_fix_sessions'),  # Change this to your latest migration name if different
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='site',
            name='flexible_loads',
            field=models.TextField(blank=True, null=True),
        ),
    ]
