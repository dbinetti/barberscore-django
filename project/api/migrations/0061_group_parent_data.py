# Generated by Django 2.0.2 on 2018-02-11 02:45

from django.db import migrations


def create_groups_from_organizations(apps, schema_editor):
    Group = apps.get_model('api', 'Group')
    Organization = apps.get_model('api', 'Organization')
    organizations = Organization.objects.filter(
        kind__lte=30,
    )
    for organization in organizations:
        group, created = Group.objects.get_or_create(
            name=organization.name,
            status=organization.status,
            kind=organization.kind,
            code=organization.code,
            start_date=organization.start_date,
            end_date=organization.end_date,
            location=organization.location,
            website=organization.website,
            facebook=organization.facebook,
            twitter=organization.twitter,
            email=organization.email,
            phone=organization.phone,
            description=organization.description,
            notes=organization.notes,
            mem_status=organization.mem_status,
            organization=organization,
        )


def copy_parent_organization(apps, schema_editor):
    Group = apps.get_model('api', 'Group')
    districts = Group.objects.filter(
        kind__in=[11, 12, 13],
    )
    for district in districts:
        parent = Group.objects.get(
            kind=1,
        )
        district.parent = parent
        district.save()
    divisions = Group.objects.filter(
        kind=21,
    )
    for division in divisions:
        organization = division.organization.parent
        parent = Group.objects.get(
            organization=organization,
            kind=11,
        )
        division.parent = parent
        division.save()
    chapters = Group.objects.filter(
        kind=30,
    )
    for chapter in chapters:
        organization = chapter.organization.parent
        parent = Group.objects.get(
            organization=organization,
            kind__in=[11, 21],
        )
        chapter.parent = parent
        chapter.save()
    choruses = Group.objects.filter(
        kind=32,
    )
    for chorus in choruses:
        organization = chorus.organization
        parent = Group.objects.get(
            organization=organization,
            kind__lte=30,
        )
        chorus.parent = parent
        chorus.save()
    quartets = Group.objects.filter(
        kind=41,
    )
    for quartet in quartets:
        organization = quartet.organization.parent
        parent = Group.objects.get(
            organization=organization,
            kind__lte=30,
        )
        quartet.parent = parent
        quartet.save()
    return


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0060_auto_20180210_1912'),
    ]

    operations = [
        migrations.RunPython(create_groups_from_organizations),
        migrations.RunPython(copy_parent_organization),
    ]
