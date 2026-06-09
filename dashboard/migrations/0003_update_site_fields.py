from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0002_alter_site_name'),   # Adjust if your last migration is different
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='postcode',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='site',
            name='industry_type',
            field=models.CharField(choices=[('MANUFACTURING', 'Manufacturing'), ('FOOD_PROCESSING', 'Food Processing'), ('RETAIL', 'Retail / Supermarket'), ('WAREHOUSE', 'Warehouse / Logistics'), ('OTHER', 'Other')], default='OTHER', max_length=50),
        ),
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
