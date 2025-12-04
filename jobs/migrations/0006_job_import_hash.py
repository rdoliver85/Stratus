from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [('jobs', '0005_jobapplication')]
    operations = [migrations.AddField(model_name='job', name='import_hash', field=models.CharField(blank=True, db_index=True, max_length=32, null=True, unique=True))]
