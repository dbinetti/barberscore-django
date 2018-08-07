from django.db.models import Manager
from django.apps import apps
from django_fsm_log.models import StateLog
import django_rq
from django.db.models import Q
from django.utils.timezone import localdate

class HumanManager(Manager):
    def update_persons(self, cursor=None):
        # Get base
        humans = self.all()
        # Filter if cursored
        if cursor:
            humans = humans.filter(
                modified__gt=cursor,
            )
        # Return as objects
        humans = humans.values_list(
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'nick_name',
            'email',
            'birth_date',
            'phone',
            'cell_phone',
            'work_phone',
            'bhs_id',
            'sex',
            'primary_voice_part',
            'is_deceased',
        )

        # Creating/Update Persons
        Person = apps.get_model('api.person')
        for human in humans:
            django_rq.enqueue(
                Person.objects.update_or_create_from_human,
                human,
                is_object=True,
            )
        t = humans.count()
        return t

    def delete_orphans(self):
        # Get base
        humans = self.all()
        humans = list(humans.values_list('id', flat=True))
        # Delete Orphans
        Person = apps.get_model('api.person')
        orphans = Person.objects.filter(
            mc_pk__isnull=False,
        ).exclude(
            mc_pk__in=humans,
        )
        t = orphans.count()
        orphans.delete()
        return t


class StructureManager(Manager):
    def update_groups(self, cursor=None):
        # Get base
        structures = self.all()
        if cursor:
            # Filter if cursored
            structures = structures.filter(
                modified__gt=cursor,
            )
        else:
            # Else clear logs
            ss = StateLog.objects.filter(
                content_type__model='group',
                structures__mc_pk__isnull=False,
            )
            ss.delete()
        # Return as objects
        structures = structures.select_related(
            'status',
        ).values_list(
            'id',
            'name',
            'preferred_name',
            'chorus_name',
            'status__name',
            'kind',
            'established_date',
            'email',
            'phone',
            'website',
            'facebook',
            'twitter',
            'bhs_id',
            'parent__id',
            'chapter_code',
        )
        # Creating/Update Groups
        Group = apps.get_model('api.group')
        for structure in structures:
            django_rq.enqueue(
                Group.objects.update_or_create_from_structure,
                structure,
                is_object=True,
            )
        return structures.count()

    def delete_orphans(self):
        # Get base
        structures = self.all()
        structures = list(structures.values_list('id', flat=True))
        # Delete Orphans
        Group = apps.get_model('api.group')
        orphans = Group.objects.filter(
            mc_pk__isnull=False,
        ).exclude(
            mc_pk__in=structures,
        )
        t = orphans.count()
        orphans.delete()
        return t


class RoleManager(Manager):
    def update_officers(self, cursor=None):
        # Get the cursor
        Officer = apps.get_model('api.officer')

        # Get base
        roles = self.select_related(
            'structure',
            'human',
        )
        # Will rebuild without a cursor
        if cursor:
            roles = roles.filter(
                modified__gt=cursor,
            )
        else:
            # Else clear logs
            ss = StateLog.objects.filter(
                content_type__model='officer',
                officers__mc_pk__isnull=False,
            )
            ss.delete()
        # Order and Return as objects
        roles = roles.order_by(
            'modified',
            'created',
        ).values_list(
            'id',
            'name',
            'structure',
            'human',
            'start_date',
            'end_date',
        )

        # Creating/Update Officers
        Officer = apps.get_model('api.officer')
        for role in roles:
            django_rq.enqueue(
                Officer.objects.update_from_role,
                role,
                is_object=True,
            )
        return roles.count()


class JoinManager(Manager):
    # def update_members(self, cursor=None):
    #     Member = apps.get_model('api.member')
    #     # Get base
    #     joins = self.select_related(
    #         'structure',
    #         'subscription',
    #         'subscription__human',
    #         'membership',
    #         'membership__status',
    #     )
    #     if cursor:
    #         joins = joins.filter(
    #             modified__gt=cursor,
    #         )
    #     else:
    #         # Else clear logs
    #         ss = StateLog.objects.filter(
    #             content_type__model='member',
    #             members__mc_pk__isnull=False,
    #         )
    #         ss.delete()
    #     # Order and Return as objects
    #     joins = joins.order_by(
    #         'modified',
    #         'created',
    #     ).values_list(
    #         'id',
    #         'structure__id',
    #         'subscription__human__id',
    #         'inactive_date',
    #         'inactive_reason',
    #         'vocal_part',
    #         'subscription__status',
    #         'subscription__current_through',
    #         'established_date',
    #         'membership__code',
    #         'membership__status__name',
    #         'paid',
    #     )

    #     # Creating/Update Persons
    #     for join in joins:
    #         django_rq.enqueue(
    #             Member.objects.update_from_join,
    #             join,
    #             is_object=True,
    #         )
    #     return joins.count()

    def update_members2(self, cursor=None):
        Member = apps.get_model('api.member')
        # Get base
        joins = self.select_related(
            'structure',
            'subscription__human',
        ).exclude(paid=0)
        if cursor:
            joins = joins.filter(
                modified__gt=cursor,
            )
        # Return unique rows
        joins = joins.values_list(
            'structure__id',
            'subscription__human__id',
        ).distinct()

        joins = [list(x) for x in joins]

        # Creating/Update Member
        for join in joins:
            join.append(bool(self.filter(
                Q(inactive_date=None) |
                Q(
                    inactive_date__gt=localdate(),
                    subscription__status='active',
                ),
                structure__id=join[0],
                subscription__human__id=join[1],
            ).exclude(paid=0)))
            django_rq.enqueue(
                Member.objects.update_from_join2,
                join,
            )
        return len(joins)


class SubscriptionManager(Manager):
    def update_persons(self, cursor=None):
        # Get base
        subscriptions = self.select_related(
            'human',
        ).filter(
            items_editable=True,
        )
        if cursor:
            subscriptions = subscriptions.filter(
                modified__gt=cursor,
            )
        else:
            # Else clear logs
            ss = StateLog.objects.filter(
                content_type__model='person',
                persons__mc_pk__isnull=False,
            )
            ss.delete()
        # Order and Return as objects
        subscriptions = subscriptions.order_by(
            'modified',
            'created',
        ).values_list(
            'id',
            'human__id',
            'current_through',
            'status',
        )

        # Creating/Update Persons
        Person = apps.get_model('api.person')
        for subscription in subscriptions:
            django_rq.enqueue(
                Person.objects.update_from_subscription,
                subscription,
                is_object=True,
            )
        return subscriptions.count()
