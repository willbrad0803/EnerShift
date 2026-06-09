from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('postcode', models.CharField(max_length=20)),
                ('industry_type', models.CharField(choices=[('MANUFACTURING', 'Manufacturing'), ('FOOD_PROCESSING', 'Food Processing'), ('RETAIL', 'Retail / Supermarket'), ('WAREHOUSE', 'Warehouse / Logistics'), ('OTHER', 'Other')], default='OTHER', max_length=50)),
                ('address', models.TextField(blank=True, null=True)),
                ('flexible_loads', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sites', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
