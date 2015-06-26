from __future__ import division

import logging
log = logging.getLogger(__name__)

import uuid

import csv
import os
import datetime
from django.db import (
    models,
    transaction,
)

from django.conf import settings
from autoslug import AutoSlugField

from django.core.validators import (
    RegexValidator,
)

from django.core.exceptions import (
    ValidationError,
)

# from django.core.urlresolvers import reverse

from timezone_field import TimeZoneField

from phonenumber_field.modelfields import PhoneNumberField

from nameparser import HumanName

from .utils import place_round


def generate_image_filename(instance, filename):
    f, ext = os.path.splitext(filename)
    return '{0}{1}'.format(instance.id, ext)


class Common(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        help_text="""
            The name of the resource.  Must be unique.  If there are singer name conflicts, please add middle initial, nickname, or other identifying information.""",
        max_length=200,
        unique=True,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
    )

    location = models.CharField(
        help_text="""
            The geographical location of the resource.""",
        max_length=200,
        blank=True,
    )

    website = models.URLField(
        help_text="""
            The website URL of the resource.""",
        blank=True,
    )

    facebook = models.URLField(
        help_text="""
            The facebook URL of the resource.""",
        blank=True,
    )

    twitter = models.CharField(
        help_text="""
            The twitter handle (in form @twitter_handle) of the resource.""",
        blank=True,
        max_length=16,
        validators=[
            RegexValidator(
                regex=r'@([A-Za-z0-9_]+)',
                message="""
                    Must be a single Twitter handle
                    in the form `@twitter_handle`.
                """,
            ),
        ],
    )

    email = models.EmailField(
        help_text="""
            The contact email of the resource.""",
        blank=True,
        null=True,
    )

    phone = PhoneNumberField(
        help_text="""
            The phone number of the resource.  Include country code.""",
        blank=True,
        null=True,
    )

    picture = models.ImageField(
        upload_to=generate_image_filename,
        help_text="""
            The picture/logo of the resource.""",
        blank=True,
        null=True,
    )

    description = models.TextField(
        help_text="""
            A description/bio of the resource.  Max 1000 characters.""",
        blank=True,
        max_length=1000,
    )

    notes = models.TextField(
        help_text="""
            Notes (for internal use only).""",
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True


class Singer(Common):

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def first_name(self):
        if self.name:
            name = HumanName(self.name)
            return name.first
        else:
            return None

    @property
    def last_name(self):
        if self.name:
            name = HumanName(self.name)
            return name.last
        else:
            return None


class Director(Common):

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def first_name(self):
        if self.name:
            name = HumanName(self.name)
            return name.first
        else:
            return None

    @property
    def last_name(self):
        if self.name:
            name = HumanName(self.name)
            return name.last
        else:
            return None


class Judge(Common):

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def first_name(self):
        if self.name:
            name = HumanName(self.name)
            return name.first
        else:
            return None

    @property
    def last_name(self):
        if self.name:
            name = HumanName(self.name)
            return name.last
        else:
            return None


class Group(Common):

    QUARTET = 1
    CHORUS = 2

    KIND_CHOICES = (
        (QUARTET, "Quartet"),
        (CHORUS, "Chorus"),
    )

    awards = models.ManyToManyField(
        'Award',
        through='GroupAward',
        related_name='groups',
    )

    kind = models.IntegerField(
        choices=KIND_CHOICES,
        default=QUARTET,
    )

    director = models.ForeignKey(
        'Director',
        related_name='groups',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    lead = models.ForeignKey(
        'Singer',
        related_name='groups_lead',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    tenor = models.ForeignKey(
        'Singer',
        related_name='groups_tenor',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    baritone = models.ForeignKey(
        'Singer',
        related_name='groups_baritone',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    bass = models.ForeignKey(
        'Singer',
        related_name='groups_bass',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    chapter_name = models.CharField(
        help_text="""
            The name of the director(s) of the chorus.""",
        max_length=200,
        blank=True,
        null=True,
    )

    chapter_code = models.CharField(
        help_text="""
            The code of the director(s) of the chorus.""",
        max_length=200,
        blank=True,
    )

    bsmdb_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=False,
    )

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            self.director = self.contestants.order_by('contest__year').last().director
        except AttributeError:
            self.director = None
        try:
            self.tenor = self.contestants.order_by('contest__year').last().tenor
        except AttributeError:
            self.tenor = None
        try:
            self.lead = self.contestants.order_by('contest__year').last().lead
        except AttributeError:
            self.lead = None
        try:
            self.baritone = self.contestants.order_by('contest__year').last().baritone
        except AttributeError:
            self.baritone = None
        try:
            self.bass = self.contestants.order_by('contest__year').last().bass
        except AttributeError:
            self.bass = None
        super(Group, self).save(*args, **kwargs)

    @property
    def bsmdb(self):
        if self.bsmdb_id:
            if self.kind == self.CHORUS:
                return 'http://www.bsmdb.com/Chorus.php?ChorusID={0}'.format(
                    self.bsmdb_id,
                )
            else:
                return 'http://www.bsmdb.com/Quartet.php?QuartetID={0}'.format(
                    self.bsmdb_id,
                )
        else:
            return None

    class Meta:
        ordering = (
            'name',
        )


class District(Common):
    BHS = 0
    DISTRICT = 1
    AFFILIATE = 2

    KIND_CHOICES = (
        (BHS, "BHS"),
        (DISTRICT, "District"),
        (AFFILIATE, "Affiliate"),
    )

    long_name = models.CharField(
        null=True,
        blank=True,
        max_length=200,
    )

    kind = models.IntegerField(
        choices=KIND_CHOICES,
        default=BHS,
    )

    class Meta:
        ordering = [
            'kind',
            'name',
        ]

    def __unicode__(self):
        return self.name


class Convention(models.Model):
    YEAR_CHOICES = []
    for r in reversed(range(1939, (datetime.datetime.now().year + 1))):
        YEAR_CHOICES.append((r, r))

    INTERNATIONAL = 1
    MIDWINTER = 2
    FALL = 3
    SPRING = 4
    PACIFIC = 5

    KIND_CHOICES = (
        (INTERNATIONAL, 'International',),
        (MIDWINTER, 'Midwinter',),
        (FALL, 'Fall',),
        (SPRING, 'Spring',),
        (PACIFIC, 'Pacific',),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        help_text="""
            The name of the convention.""",
        max_length=200,
        unique=True,
    )

    kind = models.IntegerField(
        choices=KIND_CHOICES,
        null=True,
        blank=True,
    )

    year = models.IntegerField(
        choices=YEAR_CHOICES,
        default=datetime.datetime.now().year,
        null=True,
        blank=True,
    )

    district = models.ForeignKey(
        'District',
        null=True,
        blank=True,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
    )

    dates = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    timezone = TimeZoneField(
        default='US/Pacific',
    )

    is_active = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = [
            'district',
            '-year',
        ]

        unique_together = (
            ('district', 'kind', 'year',),
        )

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.kind in [
            self.INTERNATIONAL,
            self.MIDWINTER,
            self.PACIFIC,
        ]:
            self.name = "{0} {1}".format(
                self.get_kind_display(),
                self.get_year_display(),
            )
        else:
            self.name = "{0} {1} {2}".format(
                self.district,
                self.get_kind_display(),
                self.get_year_display(),
            )
        super(Convention, self).save(*args, **kwargs)


class Contest(models.Model):

    YEAR_CHOICES = []
    for r in reversed(range(1939, (datetime.datetime.now().year + 1))):
        YEAR_CHOICES.append((r, r))

    QUARTET = 1
    CHORUS = 2
    SENIOR = 3
    COLLEGIATE = 4

    KIND_CHOICES = (
        (QUARTET, 'Quartet',),
        (CHORUS, 'Chorus',),
        (SENIOR, 'Senior',),
        (COLLEGIATE, 'Collegiate',),
    )

    INTERNATIONAL = 1
    DISTRICT = 2
    REGIONAL = 3
    PRELIMS = 4

    LEVEL_CHOICES = (
        (INTERNATIONAL, "International"),
        (DISTRICT, "District"),
        (REGIONAL, "Regional"),
        (PRELIMS, "Prelims"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
    )

    name = models.CharField(
        max_length=200,
        unique=True,
    )

    level = models.IntegerField(
        choices=LEVEL_CHOICES,
        default=INTERNATIONAL,
    )

    kind = models.IntegerField(
        choices=KIND_CHOICES,
        default=QUARTET,
    )

    year = models.IntegerField(
        choices=YEAR_CHOICES,
        default=datetime.datetime.now().year,
    )

    district = models.ForeignKey(
        'District',
        null=True,
        blank=True,
    )

    convention = models.ForeignKey(
        'Convention',
        related_name='contests',
        null=True,
        blank=True,
    )

    panel = models.IntegerField(
        help_text="""
            Size of the judging panel (typically
            three or five.)""",
        default=5,
    )

    scoresheet_pdf = models.FileField(
        upload_to=generate_image_filename,
        blank=True,
        null=True,
    )

    scoresheet_csv = models.FileField(
        upload_to=generate_image_filename,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=False,
    )

    is_complete = models.BooleanField(
        default=False,
    )

    class Meta:
        unique_together = (
            ('level', 'kind', 'year', 'district',),
        )
        ordering = (
            'level',
            'kind',
            '-year',
        )

    def clean(self):
            if self.level == self.INTERNATIONAL and self.district is not None:
                raise ValidationError('International does not have a district.')
            if self.level != self.INTERNATIONAL and self.district is None:
                raise ValidationError('You must provide a district.')
            if self.year != self.convention.year:
                raise ValidationError("The contest should be the same year as the convention.")

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.level == self.INTERNATIONAL:
            self.name = "{0} {1} {2}".format(
                self.get_level_display(),
                self.get_kind_display(),
                self.get_year_display(),
            )
        elif self.level == self.PRELIMS:
            self.name = "{0} {1} {2}".format(
                self.district,
                self.get_level_display(),
                self.get_year_display(),
            )
        else:
            self.name = "{0} {1} {2}".format(
                self.district,
                self.get_kind_display(),
                self.get_year_display(),
            )
        super(Contest, self).save(*args, **kwargs)

    def create_group_from_historical(self, name, chapter_name=None, district_name=None):
        # TODO  This probably belongs on the manager.
        if district_name:
            if district_name == 'AAMBS':
                district_name = 'BHA'
            elif district_name == 'NZABS':
                district_name = 'BHNZ'
            district = District.objects.get(name=district_name)
        else:
            district = None
        if self.kind == self.CHORUS:
            kind = 2
        else:
            kind = 1
        group = Group.objects.create(
            name=name,
            district=district,
            chapter_name=chapter_name,
            kind=kind,
        )
        log.info("Created: {0}".format(group))
        return

    def import_historical(self):
        reader = csv.reader(self.scoresheet_csv)
        next(reader)
        data = [row for row in reader]

        # Create Group if non-existant
        for row in data:
            try:
                Group.objects.get(name=row[2])
            except Group.DoesNotExist:
                self.create_group_from_historical(
                    name=row[2],
                    chapter_name=row[3],
                    district_name=row[4],
                )

        performance = {}

        with transaction.atomic():
            for row in data:
                performance['contestant'], created = Contestant.objects.get_or_create(
                    contest=self,
                    group=Group.objects.get(
                        name=row[2],
                    ),
                )
                performance['round'] = row[0]
                performance['place'] = row[1]
                performance['song1'] = row[5]
                performance['mus1'] = int(row[6])
                performance['prs1'] = int(row[7])
                performance['sng1'] = int(row[8])
                performance['song2'] = row[9]
                performance['mus2'] = int(row[10])
                performance['prs2'] = int(row[11])
                performance['sng2'] = int(row[12])
                performance['men'] = row[13]
                Performance.objects.create(**performance)

    def rank(self):
        if self.kind == self.QUARTET:
            performances = Performance.objects.filter(
                contestant__contest=self,
            )
            quarters = performances.filter(
                round=3
            ).order_by(
                '-points',
            )
            place_round(quarters)
            semis = performances.filter(
                round=2
            ).order_by(
                '-points',
            )
            place_round(semis)
            finals = performances.filter(
                round=1
            ).order_by(
                '-points',
            )
            place_round(finals)
        contestants = self.contestants.all()
        place_round(contestants)
        return


class Contestant(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    contest = models.ForeignKey(
        'Contest',
        related_name='contestants',
    )

    group = models.ForeignKey(
        'Group',
        related_name='contestants',
    )

    district = models.ForeignKey(
        'District',
        related_name='contestants',
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    director = models.ForeignKey(
        'Director',
        related_name='contestants',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    lead = models.ForeignKey(
        'Singer',
        related_name='contestants_lead',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    tenor = models.ForeignKey(
        'Singer',
        related_name='contestants_tenor',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    baritone = models.ForeignKey(
        'Singer',
        related_name='contestants_baritone',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    bass = models.ForeignKey(
        'Singer',
        related_name='contestants_bass',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    seed = models.IntegerField(
        null=True,
        blank=True,
    )

    prelim = models.FloatField(
        null=True,
        blank=True,
    )

    place = models.IntegerField(
        null=True,
        blank=True,
    )

    score = models.FloatField(
        null=True,
        blank=True,
    )

    stagetime = models.DateTimeField(
        null=True,
        blank=True,
    )

    queue = models.IntegerField(
        null=True,
        blank=True,
    )

    quarters_place = models.IntegerField(
        null=True,
        blank=True,
    )

    quarters_score = models.FloatField(
        null=True,
        blank=True,
    )

    semis_place = models.IntegerField(
        null=True,
        blank=True,
    )

    semis_score = models.FloatField(
        null=True,
        blank=True,
    )

    finals_place = models.IntegerField(
        null=True,
        blank=True,
    )

    finals_score = models.FloatField(
        null=True,
        blank=True,
    )

    points = models.IntegerField(
        null=True,
        blank=True,
    )

    men = models.IntegerField(
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        self.name = "{0} {1}".format(
            self.contest,
            self.group,
        )
        try:
            self.stagetime = self.performances.latest(
                'stagetime'
            ).stagetime
        except Performance.DoesNotExist:
            self.stagetime = None
        try:
            self.queue = self.performances.latest(
                'stagetime'
            ).queue
        except Performance.DoesNotExist:
            self.queue = None
        try:
            self.quarters_place = self.performances.get(round=3).place
        except Performance.DoesNotExist:
            self.quarters_place = None
        try:
            self.quarters_score = self.performances.get(round=3).score
        except Performance.DoesNotExist:
            self.quarters_score = None
        try:
            self.semis_place = self.performances.get(round=2).place
        except Performance.DoesNotExist:
            self.semis_place = None
        try:
            self.semis_score = self.performances.get(round=2).score
        except Performance.DoesNotExist:
            self.semis_score = None
        try:
            self.finals_place = self.performances.get(round=1).place
        except Performance.DoesNotExist:
            self.finals_place = None
        try:
            self.finals_score = self.performances.get(round=1).score
        except Performance.DoesNotExist:
            self.finals_score = None
        # try:
        #     self.points = self.performances.aggregate(
        #         sum=models.Sum('points')
        #     )['sum']
        # except Performance.DoesNotExist:
        #     self.points = None
        # try:
        #     cnt = self.performances.count()
        #     self.score = round(
        #         self.points / (cnt * self.contest.panel * 6),
        #         1
        #     )
        # except Performance.DoesNotExist:
        #     self.score = None
        # # TODO Need to think about the race condition here.
        # except TypeError:
        #     self.score = None
        super(Contestant, self).save(*args, **kwargs)

    def clean(self):
            if self.group.kind == Group.QUARTET and self.director is not None:
                raise ValidationError('Quartets do not have directors.')
            if self.group.kind == Group.CHORUS and (
                self.lead is not None or
                self.tenor is not None or
                self.baritone is not None or
                self.bass is not None
            ):
                raise ValidationError('Choruses do not have parts.')
            if self.group.kind == Group.QUARTET and self.contest.kind == Contest.CHORUS:
                raise ValidationError("Group and Contest types must match.")
            if self.group.kind == Group.CHORUS and self.contest.kind != Contest.CHORUS:
                raise ValidationError("Group and Contest types must match.")

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = (
            '-contest__year',
            'place',
            '-score',
        )
        unique_together = (
            ('group', 'contest',),
        )


class Performance(models.Model):
    FINALS = 1
    SEMIS = 2
    QUARTERS = 3

    ROUND_CHOICES = (
        (FINALS, 'Finals',),
        (SEMIS, 'Semis',),
        (QUARTERS, 'Quarters',),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    contestant = models.ForeignKey(
        'Contestant',
        related_name='performances',
        null=True,
        blank=True,
    )

    round = models.IntegerField(
        choices=ROUND_CHOICES,
        default=FINALS,
    )

    queue = models.IntegerField(
        null=True,
        blank=True,
    )

    session = models.IntegerField(
        choices=(
            (1, 1),
            (2, 2)
        ),
        null=True,
        blank=True,
    )

    stagetime = models.DateTimeField(
        help_text="""
            The title of the first song of the performance.""",
        blank=True,
        null=True,
    )

    place = models.IntegerField(
        null=True,
        blank=True,
    )

    song1 = models.CharField(
        help_text="""
            The title of the first song of the performance.""",
        blank=True,
        max_length=200,
    )

    mus1 = models.IntegerField(
        help_text="""
            The raw music score of the first song.""",
        blank=True,
        null=True,
    )

    prs1 = models.IntegerField(
        help_text="""
            The raw presentation score of the first song.""",
        blank=True,
        null=True,
    )

    sng1 = models.IntegerField(
        help_text="""
            The raw singing score of the first song.""",
        blank=True,
        null=True,
    )

    song2 = models.CharField(
        help_text="""
            The title of the second song of the performance.""",
        blank=True,
        max_length=200,
    )

    mus2 = models.IntegerField(
        help_text="""
            The raw music score of the second song.""",
        blank=True,
        null=True,
    )

    prs2 = models.IntegerField(
        help_text="""
            The raw presentation score of the second song.""",
        blank=True,
        null=True,
    )

    sng2 = models.IntegerField(
        help_text="""
            The raw singing score of the second song.""",
        blank=True,
        null=True,
    )

    mus1_score = models.FloatField(
        blank=True,
        null=True,
        editable=False,
    )

    prs1_score = models.FloatField(
        blank=True,
        null=True,
        editable=False,
    )

    sng1_score = models.FloatField(
        blank=True,
        null=True,
        editable=False,
    )

    song1_points = models.IntegerField(
        blank=True,
        null=True,
        editable=False,
    )

    song1_score = models.FloatField(
        blank=True,
        null=True,
        editable=False,
    )

    mus2_score = models.FloatField(
        blank=True,
        null=True,
        editable=False,
    )

    prs2_score = models.FloatField(
        blank=True,
        null=True,
        editable=False,
    )

    sng2_score = models.FloatField(
        blank=True,
        null=True,
        editable=False,
    )

    song2_points = models.IntegerField(
        blank=True,
        null=True,
        editable=False,
    )

    song2_score = models.FloatField(
        blank=True,
        null=True,
        editable=False,
    )

    points = models.IntegerField(
        blank=True,
        null=True,
        editable=False,
    )

    score = models.FloatField(
        blank=True,
        null=True,
        editable=False,
    )

    title1 = models.ForeignKey(
        'Song',
        related_name='performances_song1',
        null=True,
        blank=True,
    )

    title2 = models.ForeignKey(
        'Song',
        related_name='performances_song2',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            'contestant',
            'round',
            'queue',
            'stagetime',
        ]
        unique_together = (
            ('contestant', 'round',),
        )

    def __unicode__(self):
        return "{0}".format(self.id)

    def save(self, *args, **kwargs):
        if bool(
            self.mus1 and
            self.prs1 and
            self.sng1 and
            self.mus2 and
            self.prs2 and
            self.sng2
        ):
            try:
                panel = self.contestant.contest.panel
                self.song1_points = sum([
                    self.mus1,
                    self.prs1,
                    self.sng1,
                ])
                self.song2_points = sum([
                    self.mus2,
                    self.prs2,
                    self.sng2,
                ])
                self.points = sum([
                    self.song1_points,
                    self.song2_points,
                ])
                self.mus1_score = round(self.mus1 / panel, 1)
                self.prs1_score = round(self.prs1 / panel, 1)
                self.sng1_score = round(self.sng1 / panel, 1)
                self.song1_score = round(self.song1_points / (panel * 3), 1)
                self.mus2_score = round(self.mus2 / panel, 1)
                self.prs2_score = round(self.prs2 / panel, 1)
                self.sng2_score = round(self.sng2 / panel, 1)
                self.song2_score = round(self.song2_points / (panel * 3), 1)
                self.score = round(self.points / (panel * 6), 1)
            except TypeError:
                log.error("Check scores for performance {0}".format(self))
        super(Performance, self).save(*args, **kwargs)


class Award(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        help_text="""
            The name of the award.  Must be unique.""",
        max_length=200,
        unique=True,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
    )

    description = models.CharField(
        null=True,
        blank=True,
        max_length=200,
    )

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse(
    #         'website:award-detail',
    #         args=[self.slug],
    #     )


class GroupAward(models.Model):
    """Awards and placement"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    group = models.ForeignKey(
        'Group',
    )

    contest = models.ForeignKey(
        'Contest',
    )

    award = models.ForeignKey(
        'Award',
    )

    def __unicode__(self):
        return self.name


class Note(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    performance = models.ForeignKey(
        'Performance',
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notes',
    )

    text = models.TextField(
    )

    def __unicode__(self):
        return self.id

    class Meta:
        unique_together = (
            ('performance', 'user'),
        )


class Song(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=200,
        unique=True,
    )

    is_medley = models.BooleanField(
        default=False,
    )

    is_parody = models.BooleanField(
        default=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        # unique=True,
        null=True,
        blank=True,
        max_length=255,
    )

    def __unicode__(self):
        return self.name
