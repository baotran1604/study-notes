from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("notes", "0001_initial")]
    operations = [
        migrations.RenameModel(old_name="SignIn", new_name="SessionEvent"),
        migrations.AddField(
            model_name="sessionevent",
            name="kind",
            field=models.CharField(
                choices=[("login", "Signed in"), ("logout", "Signed out")],
                default="login",
                max_length=10,
            ),
        ),
    ]
