
# Standard Library
import logging
import uuid
import pydf

# Third-Party
from django_fsm_log.models import StateLog
from dry_rest_permissions.generics import allow_staff_or_superuser
from dry_rest_permissions.generics import authenticated_users
from model_utils import Choices
from model_utils.models import TimeStampedModel

# Django
from django_fsm import FSMIntegerField
from django_fsm import transition
from django_fsm_log.decorators import fsm_log_by
from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.db.models import Avg, StdDev, Q, Max, Sum


import django_rq
from api.tasks import send_psa_from_panelist
from api.tasks import save_psa_from_panelist
from api.fields import FileUploadPath


log = logging.getLogger(__name__)


class Panelist(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (-5, 'completed', 'Completed',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        help_text="""DO NOT CHANGE MANUALLY unless correcting a mistake.  Use the buttons to change state.""",
        choices=STATUS,
        default=STATUS.active,
    )

    num = models.IntegerField(
        blank=True,
        null=True,
    )

    KIND = Choices(
        (10, 'official', 'Official'),
        (20, 'practice', 'Practice'),
        (30, 'observer', 'Observer'),
    )

    kind = models.IntegerField(
        choices=KIND,
    )

    CATEGORY = Choices(
        (5, 'drcj', 'DRCJ'),
        (10, 'ca', 'CA'),
        (30, 'music', 'Music'),
        (40, 'performance', 'Performance'),
        (50, 'singing', 'Singing'),
    )

    category = models.IntegerField(
        choices=CATEGORY,
        null=True,
        blank=True,
    )

    psa = models.FileField(
        upload_to=FileUploadPath(),
        blank=True,
        default='',
    )

    legacy_num = models.IntegerField(
        null=True,
        blank=True,
    )

    legacy_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    # FKs
    round = models.ForeignKey(
        'Round',
        related_name='panelists',
        on_delete=models.CASCADE,
    )

    person = models.ForeignKey(
        'Person',
        related_name='panelists',
        on_delete=models.CASCADE,
    )

    # Relations
    statelogs = GenericRelation(
        StateLog,
        related_query_name='panelists',
    )

    @cached_property
    def row_class(self):
        if self.category == self.CATEGORY.music:
            row_class = 'warning'
        elif self.category == self.CATEGORY.performance:
            row_class = 'success'
        elif self.category == self.CATEGORY.singing:
            row_class = 'info'
        else:
            row_class = None
        return row_class


    # Internals
    class Meta:
        unique_together = (
            ('round', 'num',),
            ('round', 'person', 'category',),
        )

    class JSONAPIMeta:
        resource_name = "panelist"

    def __str__(self):
        return "{0} {1}".format(
            self.round,
            self.num,
        )

    def clean(self):
        if self.kind > self.KIND.practice:
            raise ValidationError(
                {'category': 'Panel may only contain Official and Practice'}
            )
        if self.num and self.num > 50 and self.kind == self.KIND.official:
            raise ValidationError(
                {'num': 'Official Num must be less than 50'}
            )
        if self.num and self.num <= 50 and self.kind == self.KIND.practice:
            raise ValidationError(
                {'num': 'Practice Num must be greater than 50'}
            )
        if self.num and self.num and self.category == self.CATEGORY.ca:
            raise ValidationError(
                {'num': 'CAs must not have a num.'}
            )

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.is_round_manager,
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            all([
                self.round.session.convention.assignments.filter(
                    person__user=request.user,
                    status__gt=0,
                    category__lte=10,
                ),
                self.round.status < self.round.STATUS.started,
            ]),
        ])

    def get_psa(self):
        Group = apps.get_model('api.group')
        # Score block
        group_ids = self.round.appearances.exclude(
            # Don't include advancers on SA
            draw__gt=0,
        ).values_list('group__id', flat=True)
        groups = Group.objects.filter(
            id__in=group_ids,
        ).prefetch_related(
            'appearances__songs__scores',
            'appearances__songs__scores__panelist',
            'appearances__round__session',
        ).annotate(
            tot_points=Sum(
                'appearances__songs__scores__points',
                filter=Q(
                    appearances__songs__scores__panelist__kind=Panelist.KIND.official,
                    appearances__round__session=self.round.session,
                ),
            ),
            per_points=Sum(
                'appearances__songs__scores__points',
                filter=Q(
                    appearances__songs__scores__panelist__kind=Panelist.KIND.official,
                    appearances__songs__scores__panelist__category=Panelist.CATEGORY.performance,
                    appearances__round__session=self.round.session,
                ),
            ),
            sng_points=Sum(
                'appearances__songs__scores__points',
                filter=Q(
                    appearances__songs__scores__panelist__kind=Panelist.KIND.official,
                    appearances__songs__scores__panelist__category=Panelist.CATEGORY.singing,
                    appearances__round__session=self.round.session,
                ),
            ),
        ).order_by(
            '-tot_points',
            '-sng_points',
            '-per_points',
        )
        # Monkeypatching
        class_map = {
            Panelist.CATEGORY.music: 'badge badge-warning mono-font',
            Panelist.CATEGORY.performance: 'badge badge-success mono-font',
            Panelist.CATEGORY.singing: 'badge badge-info mono-font',
        }
        for group in groups:
            appearances = group.appearances.filter(
                round__session=self.round.session,
            ).order_by('round__kind')
            for appearance in appearances:
                songs = appearance.songs.order_by(
                    'num',
                ).prefetch_related(
                    'scores',
                    'scores__panelist',
                ).annotate(
                    avg=Avg(
                        'scores__points',
                        filter=Q(
                            scores__panelist__kind=Panelist.KIND.official,
                        ),
                    ),
                    dev=StdDev(
                        'scores__points',
                        filter=Q(
                            scores__panelist__kind=Panelist.KIND.official,
                        ),
                    ),
                )
                appearance.songs_patched = songs
                for song in songs:
                    scores = song.scores.select_related(
                        'panelist',
                    ).filter(
                        panelist__kind=Panelist.KIND.official,
                    ).order_by('points')
                    out = []
                    for score in scores:
                        if score.points == 0:
                            score.points = "00"
                        span_class = class_map[score.panelist.category]
                        if score.panelist == self:
                            span_class = "{0} black-font".format(span_class)
                        out.append((score.points, span_class))
                    song.scores_patched = out
            group.appearances_patched = appearances

        context = {
            'panelist': self,
            'groups': groups,
        }
        rendered = render_to_string('reports/psa.html', context)
        file = pydf.generate_pdf(rendered)
        content = ContentFile(file)
        return content

    def queue_save_psa(self):
        queue = django_rq.get_queue('high')
        return queue.enqueue(
            save_psa_from_panelist,
            self,
        )

    def queue_send_psa(self):
        queue = django_rq.get_queue('high')
        return queue.enqueue(
            send_psa_from_panelist,
            self,
        )
