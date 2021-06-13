# Generated by Django 3.1 on 2021-06-10 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ZohoImportContactsFieldsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Import Contact Fields',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ZohoImportContactsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Import Contacts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ZohoImportLeadsFieldsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Import Lead Fields',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ZohoImportLeadsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Import Leads',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ZohoContactsSyncSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contacts_incremental_sync_last_run', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Regular Sync Last Update')),
                ('contacts_incremental_sync_last_run_count', models.IntegerField(blank=True, editable=False, null=True, verbose_name='Regular Sync Last Update Count')),
                ('contacts_delete_sync_last_run', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Delete Sync Last Update')),
                ('contacts_delete_sync_last_run_count', models.IntegerField(blank=True, editable=False, null=True, verbose_name='Delete Sync Last Update Count')),
                ('contacts_full_sync_last_run', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Full Sync Last Update')),
                ('contacts_full_sync_last_run_count', models.IntegerField(blank=True, editable=False, null=True, verbose_name='Full Sync Last Update')),
            ],
            options={
                'verbose_name': 'Contacts Sync Information',
                'verbose_name_plural': 'Contacts Sync Information',
                'db_table': '',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ZohoLeadsSyncSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leads_incremental_sync_last_run', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Regular Sync Last Update')),
                ('leads_incremental_sync_last_run_count', models.IntegerField(blank=True, editable=False, null=True, verbose_name='Regular Sync Last Update Count')),
                ('leads_delete_sync_last_run', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Delete Sync Last Update')),
                ('leads_delete_sync_last_run_count', models.IntegerField(blank=True, editable=False, null=True, verbose_name='Delete Sync Last Update Count')),
                ('leads_full_sync_last_run', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Full Sync Last Update')),
                ('leads_full_sync_last_run_count', models.IntegerField(blank=True, editable=False, null=True, verbose_name='Full Sync Last Update')),
            ],
            options={
                'verbose_name': 'Leads Sync Information',
                'verbose_name_plural': 'Leads Sync Information',
                'db_table': '',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ZohoOAuth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refresh_token', models.CharField(max_length=250)),
                ('access_token', models.CharField(max_length=250)),
                ('expiry_time', models.BigIntegerField()),
                ('user_email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='ZohoSyncErrorLogs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('module_type', models.CharField(blank=True, editable=False, max_length=150, null=True, verbose_name='Module')),
                ('added_on', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Date/Time')),
                ('error_code', models.CharField(blank=True, editable=False, max_length=50, null=True, verbose_name='Error Code')),
                ('error_message', models.CharField(blank=True, editable=False, max_length=200, null=True, verbose_name='Error Message')),
                ('error_details', models.TextField(blank=True, editable=False, null=True, verbose_name='Error Details')),
                ('error_content', models.TextField(blank=True, editable=False, null=True, verbose_name='Error Content')),
            ],
            options={
                'verbose_name': 'Sync Error Log',
                'verbose_name_plural': 'Sync Error Logs',
                'db_table': '',
                'managed': True,
            },
        ),
    ]