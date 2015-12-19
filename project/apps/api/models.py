from __future__ import division

import logging
log = logging.getLogger(__name__)

import uuid

import os
import datetime

from django.db import (
    models,
)

from django.contrib.postgres.fields import (
    DateRangeField,
    DateTimeRangeField,
)

from autoslug import AutoSlugField

from django.core.validators import (
    RegexValidator,
    MaxValueValidator,
    MinValueValidator,
)

from django_fsm import (
    transition,
    # FSMField,
    FSMIntegerField,
)

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

from django.core.exceptions import (
    ValidationError,
)

from model_utils.models import (
    TimeStampedModel,
)

from model_utils.fields import (
    MonitorField,
)

from model_utils import Choices

from model_utils.managers import (
    PassThroughManager,
)

from mptt.models import (
    MPTTModel,
    TreeForeignKey,
)

from timezone_field import TimeZoneField

from phonenumber_field.modelfields import PhoneNumberField

from nameparser import HumanName

from .managers import (
    UserManager,
    PerformerQuerySet,
)

# from .signals import session_post_save

from .validators import (
    validate_trimmed,
    dixon,
    # is_imsessioned,
    # is_scheduled,
    # has_performers,
    # has_contests,
    # round_scheduled,
    # contest_started,
    scores_entered,
    songs_entered,
    # rounds_finished,
    # round_finished,
    performances_finished,
    scores_validated,
    song_entered,
    score_entered,
    preceding_finished,
    # preceding_round_finished,
)


def generate_image_filename(instance, filename):
    f, ext = os.path.splitext(filename)
    return '{0}{1}'.format(instance.id, ext)


class Common(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        help_text="""
            The name of the resource.""",
        max_length=200,
        blank=False,
        unique=True,
        validators=[
            validate_trimmed,
        ],
        error_messages={
            'unique': 'The name must be unique.  Add middle initials, suffixes, years, or other identifiers to make the name unique.',
        }
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
        (20, 'inactive', 'Inactive',),
    )

    sts = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    sts_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='sts',
    )

    start_date = models.DateField(
        help_text="""
            The founding/birth date of the resource.""",
        blank=True,
        null=True,
    )

    end_date = models.DateField(
        help_text="""
            The retirement/deceased date of the resource.""",
        blank=True,
        null=True,
    )

    dates = DateRangeField(
        help_text="""
            The active dates of the resource.""",
        null=True,
        blank=True,
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
    )

    class Meta:
        abstract = True


class Arranger(TimeStampedModel):
    """Chorus relation"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    PART = Choices(
        (1, 'arranger', 'Arranger'),
        (2, 'coarranger', 'Co-Arranger'),
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

    catalog = models.ForeignKey(
        'Catalog',
        related_name='arrangers',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    person = models.ForeignKey(
        'Person',
        related_name='arrangements',
    )

    part = models.IntegerField(
        choices=PART,
        default=PART.arranger,
    )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        self.name = u"{0} {1}".format(
            self.catalog,
            self.person,
        )
        super(Arranger, self).save(*args, **kwargs)

    class Meta:
        unique_together = (
            ('catalog', 'person',),
        )


class Award(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
        (20, 'inactive', 'Inactive',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    organization = TreeForeignKey(
        'Organization',
        related_name='awards',
    )

    KIND = Choices(
        (1, 'quartet', 'Quartet',),
        (2, 'chorus', 'Chorus',),
        (3, 'seniors', 'Seniors Quartet',),
        (4, 'collegiate', 'Collegiate Quartet',),
        (5, 'novice', 'Novice Quartet',),
    )

    kind = models.IntegerField(
        choices=KIND,
        null=True,
        blank=True,
    )

    rounds = models.IntegerField(
    )

    long_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
    )

    stix_num = models.IntegerField(
        null=True,
        blank=True,
    )

    stix_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )

    is_championship = models.BooleanField(
        help_text="""
            Championships are awards with only one winner.""",
        default=True,
    )

    class Meta:
        ordering = (
            'organization',
            'kind',
        )
        unique_together = (
            ('organization', 'long_name', 'kind',),
        )

    def save(self, *args, **kwargs):
        self.name = " ".join(filter(None, [
            u"{0}".format(self.organization),
            u"{0}".format(self.get_kind_display()),
            u"{0}".format(self.long_name),
        ]))
        super(Award, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"{0}".format(self.name)


class Catalog(TimeStampedModel):
    TEMPO = Choices(
        (1, "Ballad"),
        (2, "Uptune"),
        (3, "Mixed"),
    )

    DIFFICULTY = Choices(
        (1, "Very Easy"),
        (2, "Easy"),
        (3, "Medium"),
        (4, "Hard"),
        (5, "Very Hard"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tune = models.ForeignKey(
        'Tune',
        null=True,
        blank=True,
        related_name='catalogs',
        on_delete=models.SET_NULL,
    )

    song_name = models.CharField(
        blank=True,
        max_length=200,
    )

    bhs_id = models.IntegerField(
        null=True,
        blank=True,
    )

    bhs_published = models.DateField(
        null=True,
        blank=True,
    )

    bhs_songname = models.CharField(
        blank=True,
        max_length=200,
    )

    bhs_arranger = models.CharField(
        blank=True,
        max_length=200,
    )

    bhs_fee = models.FloatField(
        null=True,
        blank=True,
    )

    bhs_difficulty = models.IntegerField(
        null=True,
        blank=True,
        choices=DIFFICULTY
    )

    bhs_tempo = models.IntegerField(
        null=True,
        blank=True,
        choices=TEMPO,
    )

    bhs_medley = models.BooleanField(
        default=False,
    )

    is_parody = models.BooleanField(
        default=False,
    )

    is_medley = models.BooleanField(
        default=False,
    )


class Certification(TimeStampedModel):
    """Certification"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New'),
        (1, 'active', 'Active'),
        (2, 'candidate', 'Candidate'),
        (3, 'inactive', 'Inactive'),
    )

    CATEGORY = Choices(
        (0, 'admin', 'Admin'),
        (1, 'music', 'Music'),
        (2, 'presentation', 'Presentation'),
        (3, 'singing', 'Singing'),
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

    person = models.ForeignKey(
        'Person',
        related_name='certifications',
    )

    category = models.IntegerField(
        choices=CATEGORY,
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        self.name = u"{0} {1}".format(
            self.person,
            self.get_category_display(),
        )
        super(Certification, self).save(*args, **kwargs)

    class Meta:
        unique_together = (
            ('category', 'person',),
        )


class Chapter(Common):

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
        (20, 'inactive', 'Inactive',),
        (50, 'dup', 'Duplicate',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    code = models.CharField(
        help_text="""
            The chapter code.""",
        max_length=200,
        blank=True,
        validators=[
            validate_trimmed,
        ],
    )

    organization = TreeForeignKey(
        'Organization',
        related_name='chapters',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    @staticmethod
    def autocomplete_search_fields():
            return ("id__iexact", "name__icontains",)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        ordering = (
            'name',
        )


class Contest(TimeStampedModel):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=200,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'built', 'Built',),
        (20, 'started', 'Started',),
        (25, 'finished', 'Finished',),
        (30, 'final', 'Final',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    session = models.ForeignKey(
        'Session',
        related_name='contests',
    )

    award = models.ForeignKey(
        'Award',
        related_name='contests',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    organization = TreeForeignKey(
        'Organization',
        help_text="""
            The organization that will confer the contest.  Note that this may be different than the organization running the parent session.""",
        related_name='contests',
        null=True,
        blank=True,
    )

    LEVEL = Choices(
        (1, 'international', "International"),
        (2, 'district', "District"),
        (3, 'division', "Division"),
    )

    level = models.IntegerField(
        help_text="""
            The level of the contest.  Note that this may be different than the level of the parent session.""",
        choices=LEVEL,
        null=True,
        blank=True,
    )

    KIND = Choices(
        (1, 'quartet', 'Quartet',),
        (2, 'chorus', 'Chorus',),
        (3, 'seniors', 'Senior',),
        (4, 'collegiate', 'Collegiate',),
        (5, 'novice', 'Novice',),
        (6, 'a', 'Plateau A',),
        (7, 'aa', 'Plateau AA',),
        (8, 'aaa', 'Plateau AAA',),
    )

    kind = models.IntegerField(
        help_text="""
            The kind of the contest.  Note that this may be different than the kind of the parent session.""",
        choices=KIND,
        null=True,
        blank=True,
    )

    GOAL = Choices(
        (1, 'championship', "Championship"),
        (2, 'qualifier', "Qualifier"),
    )

    goal = models.IntegerField(
        help_text="""
            The objective of the contest.""",
        choices=GOAL,
    )

    qual_score = models.FloatField(
        help_text="""
            The objective of the contest.  Note that if the goal is `qualifier` then this must be set.""",
        null=True,
        blank=True,
    )

    YEAR_CHOICES = []
    for r in reversed(range(1939, (datetime.datetime.now().year + 2))):
        YEAR_CHOICES.append((r, r))

    year = models.IntegerField(
        choices=YEAR_CHOICES,
        null=True,
        blank=True,
    )

    ROUNDS_CHOICES = []
    for r in reversed(range(1, 4)):
        ROUNDS_CHOICES.append((r, r))

    rounds = models.IntegerField(
        help_text="""
            The number of rounds that will be used in determining the contest.  Note that this may be fewer than the total number of rounds (rounds) in the parent session.""",
        choices=ROUNDS_CHOICES,
        null=True,
        blank=True,
    )

    HISTORY = Choices(
        (0, 'new', 'New',),
        (10, 'none', 'None',),
        (20, 'pdf', 'PDF',),
        (30, 'places', 'Places',),
        (40, 'incomplete', 'Incomplete',),
        (50, 'complete', 'Complete',),
    )

    history = models.IntegerField(
        help_text="""Used to manage state for historical imports.""",
        choices=HISTORY,
        default=HISTORY.new,
    )

    history_monitor = MonitorField(
        help_text="""History last updated""",
        monitor='history',
    )

    scoresheet_pdf = models.FileField(
        help_text="""
            PDF of the OSS.""",
        upload_to=generate_image_filename,
        blank=True,
        null=True,
    )

    scoresheet_csv = models.FileField(
        help_text="""
            The parsed scoresheet (used for legacy imports).""",
        upload_to=generate_image_filename,
        blank=True,
        null=True,
    )

    subsession_id = models.IntegerField(
        null=True,
        blank=True,
    )

    subsession_text = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )

    class Meta:
        unique_together = (
            ('session', 'award', 'goal',)
        )
        ordering = (
            'session',
            'award',
            'goal',
        )

    @staticmethod
    def autocomplete_search_fields():
            return ("id__iexact", "name__icontains",)

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        self.name = u"{0} {1} {2}".format(
            self.session,
            self.award,
            self.get_goal_display()
        )
        super(Contest, self).save(*args, **kwargs)

    def rank(self):
        contestants = self.contestants.all()
        for contestant in contestants:
            contestant.calculate()
            contestant.save()
        cursor = []
        i = 1
        for contestant in self.contestants.order_by('-total_points'):
            try:
                match = contestant.total_points == cursor[0].total_points
            except IndexError:
                contestant.place = i
                contestant.save()
                cursor.append(contestant)
                continue
            if match:
                contestant.place = i
                i += len(cursor)
                contestant.save()
                cursor.append(contestant)
                continue
            else:
                i += 1
                contestant.place = i
                contestant.save()
                cursor = [contestant]
        return "{0} Ready for Review".format(self)

    @transition(
        field=status,
        source=STATUS.new,
        target=STATUS.built,
    )
    def build(self):
        # Triggered by contest post_save signal if created
        r = 1
        while r <= self.rounds:
            self.rounds.create(
                session=self,
                kind=r,
            )
            r += 1

        # # Create an adminstrator sentinel
        # self.judges.create(
        #     contest=self,
        #     category=0,
        #     slot=1,
        # )

        # # Create sentinels for the session.
        # s = 1
        # while s <= self.session:
        #     self.judges.create(
        #         contest=self,
        #         category=1,
        #         slot=s,
        #     )
        #     self.judges.create(
        #         contest=self,
        #         category=2,
        #         slot=s,
        #     )
        #     self.judges.create(
        #         contest=self,
        #         category=3,
        #         slot=s,
        #     )
        #     s += 1
        # return

    # @transition(
    #     field=status,
    #     source=[
    #         STATUS.built,
    #         STATUS.ready,
    #     ],
    #     target=STATUS.ready,
    #     conditions=[
    #         is_scheduled,
    #         is_imsessioned,
    #         has_performers,
    #     ],
    # )
    # def prep(self):
    #     # Seed performers
    #     marker = []
    #     i = 1
    #     for performer in self.performers.accepted().order_by('-prelim'):
    #         try:
    #             match = performer.prelim == marker[0].prelim
    #         except IndexError:
    #             performer.seed = i
    #             performer.save()
    #             marker.append(performer)
    #             continue
    #         if match:
    #             performer.seed = i
    #             i += len(marker)
    #             performer.save()
    #             marker.append(performer)
    #             continue
    #         else:
    #             i += 1
    #             performer.seed = i
    #             performer.save()
    #             marker = [performer]
    #     return "{0} Ready".format(self)

    # @transition(
    #     field=status,
    #     source=STATUS.built,
    #     target=STATUS.started,
    #     conditions=[
    #         # is_scheduled,
    #         is_imsessioned,
    #         has_performers,
    #         has_contests,
    #     ],
    # )
    # def start(self):
    #     # Triggered in UI
    #     # TODO seed performers?
    #     round = self.rounds.initial()
    #     p = 0
    #     for performer in self.performers.accepted().order_by('?'):
    #         performer.register()
    #         performer.save()
    #         round.performances.create(
    #             round=round,
    #             performer=performer,
    #             position=p,
    #         )
    #         p += 1
    #     return "{0} Started".format(self)

    @transition(
        field=status,
        source=STATUS.started,
        target=STATUS.finished,
        conditions=[
            # rounds_finished,
        ],
    )
    # Check everything is done.
    def finish(self):
        # Denormalize
        ns = Song.objects.filter(
            performance__round__session=self.session,
        )
        for n in ns:
            n.save()
        ps = Performance.objects.filter(
            round__session=self.session,
        )
        for p in ps:
            p.save()
        ts = Performer.objects.filter(
            session=self.session,
        )
        for t in ts:
            t.save()
        rs = Contestant.objects.filter(
            contest=self,
        )
        for r in rs:
            r.save()
        # Rank results
        cursor = []
        i = 1
        for contestant in self.contestants.order_by('-total_points'):
            try:
                match = contestant.total_points == cursor[0].total_points
            except IndexError:
                contestant.place = i
                contestant.save()
                cursor.append(contestant)
                continue
            if match:
                contestant.place = i
                i += len(cursor)
                contestant.save()
                cursor.append(contestant)
                continue
            else:
                i += 1
                contestant.place = i
                contestant.save()
                cursor = [contestant]
        return "{0} Ready for Review".format(self)

    @transition(field=status, source=STATUS.finished, target=STATUS.final)
    def finalize(self):
        # Review logic
        return "{0} Ready".format(self)


class Contestant(TimeStampedModel):
    STATUS = Choices(
        (0, 'new', 'New',),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    performer = models.ForeignKey(
        'Performer',
        related_name='contestants',
    )

    contest = models.ForeignKey(
        'Contest',
        related_name='contestants',
    )

    # Denormalization
    place = models.IntegerField(
        help_text="""
            The final ranking relative to this contest.""",
        null=True,
        blank=True,
        editable=False,
    )

    mus_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    prs_points = models.IntegerField(
        null=True,
        editable=False,
        blank=True,
    )

    sng_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    total_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    mus_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    prs_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    sng_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    total_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        self.name = u"{0} {1}".format(
            self.contest,
            self.performer.group,
        )
        super(Contestant, self).save(*args, **kwargs)

    class Meta:
        unique_together = (
            ('performer', 'contest',),
        )
        ordering = (
            'contest',
            'performer',
        )

    def calculate(self):
        # If there are no performances, skip.
        if self.performer.performances.exists():
            agg = self.performer.performances.filter(
                round__num__lte=self.contest.award.rounds,
            ).filter(
                round__session=self.contest.session,
            ).aggregate(
                mus=models.Sum('mus_points'),
                prs=models.Sum('prs_points'),
                sng=models.Sum('sng_points'),
            )
            self.mus_points = agg['mus']
            self.prs_points = agg['prs']
            self.sng_points = agg['sng']

            # Calculate total points.
            try:
                self.total_points = sum([
                    self.mus_points,
                    self.prs_points,
                    self.sng_points,
                ])
            except TypeError:
                self.total_points = None

            # Calculate percentile
            try:
                possible = self.contest.session.size * 2 * self.performer.performances.count()
                self.mus_score = round(self.mus_points / possible, 1)
                self.prs_score = round(self.prs_points / possible, 1)
                self.sng_score = round(self.sng_points / possible, 1)
                self.total_score = round(self.total_points / (possible * 3), 1)
            except TypeError:
                self.mus_score = None
                self.prs_score = None
                self.sng_score = None


class Convention(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'built', 'Built',),
        (20, 'started', 'Started',),
        (30, 'final', 'Final',),
    )

    status = models.IntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    organization = TreeForeignKey(
        'Organization',
        help_text="""
            The organization hosting the convention.""",
    )

    # orgs = TreeManyToManyField(
    #     'Organization',
    #     help_text="""
    #         The organization hosting the convention.""",
    #     related_name='orgs',
    # )

    stix_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    stix_div = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    KIND = Choices(
        (1, 'international', 'International',),
        (2, 'midwinter', 'Midwinter',),
        (3, 'fall', 'Fall',),
        (4, 'spring', 'Spring',),
        (9, 'video', 'Video',),
    )

    kind = models.IntegerField(
        help_text="""
            The kind of convention.""",
        choices=KIND,
    )

    DIVISION = Choices(
        (200, 'evgd1', "Division I"),
        (210, 'evgd2', "Division II"),
        (220, 'evgd3', "Division III"),
        (230, 'evgd4', "Division IV"),
        (240, 'evgd5', "Division V"),
        (250, 'fwdaz', "Arizona Division"),
        (260, 'fwdnenw', "NE/NW Division"),
        (270, 'fwdsesw', "SE/SW Division"),
        (280, 'lolp1', "Division One/Packerland Division"),
        (290, 'lolnp', "Northern Plains Division"),
        (300, 'lol10sw', "10,000 Lakes and Southwest Division"),
        (310, 'madatl', "Atlantic Division"),
        (320, 'madnw', "Northern and Western Division"),
        (330, 'madsth', "Southern Division"),
        (340, 'nedsun', "Sunrise Division"),
    )

    division = models.IntegerField(
        help_text="""
            This is a division convention of Divisions.""",
        choices=DIVISION,
        null=True,
        blank=True,
    )

    YEAR_CHOICES = []
    for r in reversed(range(1939, (datetime.datetime.now().year + 2))):
        YEAR_CHOICES.append((r, r))

    year = models.IntegerField(
        choices=YEAR_CHOICES,
    )

    dates = models.CharField(
        help_text="""
            The convention dates (will be replaced by start/end).""",
        max_length=200,
        blank=True,
    )

    dates2 = DateRangeField(
        help_text="""
            The convention dates (will be replaced by start/end).""",
        null=True,
        blank=True,
    )

    location = models.CharField(
        help_text="""
            The location of the convention.""",
        max_length=200,
        blank=True,
    )

    timezone = TimeZoneField(
        help_text="""
            The local timezone of the convention.""",
        default='US/Pacific',
    )

    stix_file = models.FileField(
        help_text="""
            The bbstix file.""",
        upload_to=generate_image_filename,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = [
            '-year',
            'organization__name',
        ]

        unique_together = (
            ('organization', 'kind', 'year', 'division',),
        )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        # self.name = u"{0}; {1}; {2}".format(
        #     self.stix_name,
        #     self.location,
        #     self.dates,
        # )
        if self.division:
            self.name = u"{0} {1} {2} {3}".format(
                self.organization,
                self.get_kind_display(),
                self.get_division_display(),
                self.year,
            )
        else:
            self.name = u"{0} {1} {2}".format(
                self.organization,
                self.get_kind_display(),
                self.year,
            )
        super(Convention, self).save(*args, **kwargs)

    # def stix(self):
    #     # models.signals.post_save.disconnect(session_post_save)

    #     # Load data and skip first two header rows
    #     reader = csv.reader(self.stix_file, skipinitialspace=True)
    #     reader.next()
    #     reader.next()
    #     rows = [row for row in reader]

    #     # Determine meta-data
    #     chorus_count = 0
    #     quartet_count = 0
    #     for row in rows:
    #         if row[0].startswith('Subsessions:'):
    #             # Parse session into components
    #             parts = row[0].partition(':')
    #             # Parse session meta-data
    #             session_text = parts[2].strip()
    #             if session_text.startswith('Chorus'):
    #                 chorus_count += 1
    #             elif session_text.startswith('Quartet'):
    #                 quartet_count += 1
    #             else:
    #                 raise RuntimeError("Can't determine session kind")
    #         if row[0].startswith('Judge'):
    #             # TODO Parse from panel meta data
    #             judge_count = int(row[0].partition(":")[2].strip())
    #     # Build Sessions
    #     for row in rows:
    #         if row[0].startswith('Subsessions:'):
    #             # Parse session into components
    #             parts = row[0].partition(':')
    #             # Parse session kind and create
    #             session_text = parts[2]
    #             # Identify session by kind
    #             if 'Chorus' in session_text:
    #                 # Get or create the session for indempodence
    #                 session, created = self.sessions.get_or_create(
    #                     convention=self,
    #                     kind=self.sessions.model.KIND.chorus,
    #                     size=2,   #  WARNING   CONSTANT!! !  HACK
    #                     num_rounds=chorus_count,
    #                 )
    #                 # This is a little hacky, but instantiate the rounds,
    #                 # including increment and kind.
    #                 i = 0
    #                 j = chorus_count
    #                 while i < chorus_count:
    #                     rnd, created = session.rounds.get_or_create(
    #                         num=i,
    #                         kind=j,
    #                     )
    #                     i += 1
    #                     j -= 1

    #                 # build a list of the contests (called subsessions here)
    #                 contest_list = row[1:]
    #                 for c in contest_list:
    #                     # Parse each list item for id, name
    #                     parts = c.partition('=')
    #                     contest_number = int(parts[0].strip())
    #                     contest_text = parts[2]
    #                     # skip if it's a "most improved" award
    #                     if "Most-Improved" in contest_text:
    #                         log.error("Skipping most improved: {0}".format(contest_text))
    #                         continue
    #                     # Determine the organization
    #                     if contest_text.startswith(self.organization.long_name):
    #                         #  If the subsession matches the convention, stop
    #                         organization = self.organization
    #                     else:
    #                         # match according to the related division name, or throw exception
    #                         divisions = self.organization.children.all()
    #                         organization = None
    #                         for div in divisions:
    #                             # TODO might need regex here
    #                             if contest_text.startswith("{0} ".format(div.long_name)):
    #                                 organization = div
    #                                 continue
    #                         if not organization:
    #                             raise RuntimeError("No match on subsession")

    #                     # Determine the parent (if any)
    #                     # # Check for qualifiers from this list
    #                     # qualification_markers = [
    #                     #     'Preliminary',
    #                     # ]
    #                     # if any(substring in contest_text for substring in qualification_markers):
    #                     # Check for prelims
    #                     parent = None
    #                     year = self.year
    #                     if "Preliminary" in contest_text:
    #                         # Find year, based on district
    #                         year = self.year + 1
    #                         try:
    #                             parent = Contest.objects.get(
    #                                 level=Contest.LEVEL.international,
    #                                 kind=Contest.KIND.chorus,
    #                                 organization=self.organization.parent,
    #                                 year=year,
    #                             )
    #                         except Exception as e:
    #                             raise ("Error finding parent: {0} {1}".format(contest_text, e))

    #                     if "Qualification" in contest_text:
    #                         # Find year, based on district
    #                         year = self.year
    #                         try:
    #                             parent = Contest.objects.get(
    #                                 level=Contest.LEVEL.district,
    #                                 kind=Contest.KIND.chorus,
    #                                 organization=self.organization,
    #                                 year=year,
    #                             )
    #                         except Exception as e:
    #                             log.error("Error finding parent: {0}".format(contest_text))
    #                             raise e
    #                     # Determine Level
    #                     # TODO Not sure this adds value...
    #                     level = organization.level + 1

    #                     # Determine Rounds
    #                     # This is assumed to be constant for Chorus comps.
    #                     rounds = 1

    #                     # Determine the Kind
    #                     # TODO Really need a better parser here
    #                     KIND = session.contests.model.KIND
    #                     if 'Plateau A Chorus' in contest_text:
    #                         kind = KIND.a
    #                     elif 'Plateau AA Chorus' in contest_text:
    #                         kind = KIND.aa
    #                     elif 'Plateau AAA Chorus' in contest_text:
    #                         kind = KIND.aaa
    #                     else:
    #                         kind = KIND.chorus
    #                         # raise RuntimeError("parse fail!")
    #                     contest, created = session.contests.get_or_create(
    #                         kind=kind,
    #                         level=level,
    #                         organization=organization,
    #                         year=year,
    #                         rounds=rounds,
    #                         session=session,
    #                         parent=parent,
    #                     )
    #                     contest.subsession_id = contest_number
    #                     contest.save()

    #             # Identify session by kind
    #             if 'Quartet' in session_text:
    #                 # Get or create the session for indempodence
    #                 session, created = self.sessions.get_or_create(
    #                     convention=self,
    #                     kind=self.sessions.model.KIND.quartet,
    #                     size=2,   #  WARNING   CONSTANT!! !  HACK
    #                     num_rounds=quartet_count,
    #                 )
    #                 # This is a little hacky, but instantiate the rounds,
    #                 # including increment and kind.
    #                 i = 0
    #                 j = quartet_count
    #                 while i < quartet_count:
    #                     rnd, created = session.rounds.get_or_create(
    #                         num=i,
    #                         kind=j,
    #                     )
    #                     i += 1
    #                     j -= 1

    #                 # build a list of the contests (called subsessions here)
    #                 contest_list = row[1:]
    #                 for c in contest_list:

    #                     # There's something wrong with who and how is being skipped and defaulted to

    #                     # skip if it's a "most improved" award
    #                     if any([
    #                         "Out of Division" in c,
    #                         "Super Seniors" in c,
    #                     ]):
    #                         log.error("Skipping out of division: {0}".format(contest_text))
    #                         continue
    #                     # Parse each list item for id, name
    #                     parts = c.partition('=')
    #                     log.debug(contest_list)
    #                     log.debug(parts)
    #                     contest_number = int(parts[0].strip())
    #                     contest_text = parts[2]
    #                     # Determine the organization
    #                     if contest_text.startswith(self.organization.long_name):
    #                         #  If the subsession matches the convention, stop
    #                         organization = self.organization
    #                     else:
    #                         # match according to the related division name, or throw exception
    #                         divisions = self.organization.children.all()
    #                         organization = None
    #                         for div in divisions:
    #                             # TODO might need regex here
    #                             if contest_text.startswith("{0} ".format(div.long_name)):
    #                                 organization = div
    #                                 continue
    #                         if not organization:
    #                             raise RuntimeError("No match on subsession")

    #                     # Determine the Kind
    #                     # TODO Really need a better parser here
    #                     KIND = session.contests.model.KIND
    #                     if 'Novice Quartet' in contest_text:
    #                         kind = KIND.novice
    #                     if 'Seniors Quartet' in contest_text:
    #                         kind = KIND.seniors
    #                     else:
    #                         kind = KIND.quartet

    #                     # Determine the parent (if any)
    #                     # # Check for qualifiers from this list
    #                     # qualification_markers = [
    #                     #     'Preliminary',
    #                     # ]
    #                     # if any(substring in contest_text for substring in qualification_markers):
    #                     # Check for prelims
    #                     parent = None
    #                     year = self.year
    #                     if "Qualification" in contest_text:
    #                         # Find year, based on district
    #                         year = self.year
    #                         try:
    #                             parent = Contest.objects.get(
    #                                 level=Contest.LEVEL.district,
    #                                 kind=kind,
    #                                 organization=self.organization,
    #                                 year=year,
    #                             )
    #                         except Exception as e:
    #                             log.error("Error finding parent: {0}".format(contest_text))
    #                             raise e

    #                     # Determine Level
    #                     # TODO Not sure this adds value...
    #                     level = organization.level + 1

    #                     # Determine Rounds
    #                     if "(2 Rounds)" in contest_text:
    #                         rounds = 2
    #                     else:
    #                         rounds = 1

    #                         # raise RuntimeError("parse fail!")
    #                     contest, created = session.contests.get_or_create(
    #                         kind=kind,
    #                         level=level,
    #                         organization=organization,
    #                         year=year,
    #                         rounds=rounds,
    #                         session=session,
    #                         parent=parent,
    #                     )
    #                     contest.subsession_id = contest_number
    #                     contest.save()
    #             else:
    #                 raise RuntimeError("Can't determine session kind")

    #     # Determine Panel
    #     for row in rows:
    #         if row[0].startswith('Panel'):
    #             parts = row[0].partition('-')
    #             # Parse panel kind and create
    #             panel_text = parts[2]
    #             # Identify panel by kind
    #             if 'Chorus' in panel_text:
    #                 kind = self.sessions.model.KIND.chorus
    #             elif 'Quartet' in panel_text:
    #                 kind = self.sessions.model.KIND.quartet
    #             else:
    #                 raise RuntimeError("Can't determine judging panel kind")
    #             session = self.sessions.get(
    #                 convention=self,
    #                 kind=kind,
    #             )
    #             # Create judges from same row
    #             panel_list = row[1:]
    #             mus_slot = 1
    #             prs_slot = 1
    #             sng_slot = 1
    #             for panel in panel_list:
    #                 # Partition into components
    #                 parts = panel.partition('=')
    #                 name = HumanName(parts[2])
    #                 # And sub partition the first partition
    #                 subparts = parts[0].partition('(')
    #                 # Find the panel_id number
    #                 panel_id = int(subparts[0].strip())
    #                 # And the category by abbreviation
    #                 if panel_id < 50:
    #                     kind = session.judges.model.KIND.official
    #                 else:
    #                     kind = session.judges.model.KIND.practice
    #                 category_raw = subparts[2][:3]
    #                 # Get the person
    #                 from .models import Person
    #                 person = Person.objects.get(
    #                     name=str(name),
    #                 )
    #                 # Now create judge by category, incrementing each
    #                 # slot accordingly
    #                 judge_dict = {
    #                     'kind': kind,
    #                     'person': person,
    #                 }
    #                 if category_raw == 'MUS':
    #                     judge_dict['category'] = session.judges.model.CATEGORY.music
    #                     judge_dict['slot'] = mus_slot
    #                     mus_slot += 1
    #                 elif category_raw == 'PRS':
    #                     judge_dict['category'] = session.judges.model.CATEGORY.presentation
    #                     judge_dict['slot'] = prs_slot
    #                     prs_slot += 1
    #                 elif category_raw == 'SNG':
    #                     judge_dict['category'] = session.judges.model.CATEGORY.singing
    #                     judge_dict['slot'] = sng_slot
    #                     sng_slot += 1
    #                 else:
    #                     raise RuntimeError("Unknown category!")
    #                 judge, created = session.judges.get_or_create(
    #                     **judge_dict
    #                 )
    #                 judge.panel_id = panel_id
    #                 judge.save()

    #     # Determine Judge
    #     for row in rows:
    #         if row[0].startswith('Judge'):
    #             pass

    #         # Determine Performances
    #     for row in rows:
    #         if row[0].startswith('Session'):
    #             if 'Chorus' in row[0]:
    #                 session = self.sessions.get(
    #                     kind=self.sessions.model.KIND.chorus,
    #                 )
    #             elif 'Quartet' in row[0]:
    #                 session = self.sessions.get(
    #                     kind=self.sessions.model.KIND.quartet,
    #                 )
    #             else:
    #                 raise RuntimeError("Can't determine session")
    #             group_name = row[1].partition(":")[2].strip()
    #             if session.kind == session.KIND.chorus:
    #                 from .models import Group
    #                 try:
    #                     group = Chapter.objects.get(
    #                         name=group_name,
    #                         status=Chapter.STATUS.active,
    #                     ).groups.first()
    #                 except Chapter.DoesNotExist:
    #                     log.error("No Chapter: {0}".format(group_name))
    #                     continue
    #                 except Chapter.MultipleObjectsReturned:
    #                     log.error("Many Chapters: {0}".format(group_name))
    #                     continue
    #             else:
    #                 from .models import Group
    #                 try:
    #                     group, created = Group.objects.get_or_create(
    #                         name=group_name,
    #                         status=Group.STATUS.active,
    #                     )
    #                 except Group.DoesNotExist:
    #                     log.error("No Group: {0}".format(group_name))
    #                     continue
    #                 except Group.MultipleObjectsReturned:
    #                     log.error("Many Groups: {0}".format(group_name))
    #                     continue
    #                 except UnicodeDecodeError:
    #                     log.error("Unicode {0}".format(group_name))
    #                     continue
    #             performer, created = session.performers.get_or_create(
    #                 group=group,
    #                 session=session,
    #             )
    #             subsessions_list = row[2].partition(":")[2].split(",")
    #             subsessions = [int(s) for s in subsessions_list]
    #             log.debug(session)
    #             log.debug([contest.subsession_id for contest in session.contests.all()])
    #             log.debug(session.contests.get(subsession_id=2))
    #             for subsession in subsessions:
    #                 try:
    #                     contest = session.contests.get(
    #                         subsession_id=subsession,
    #                     )
    #                 except session.contests.model.DoesNotExist:
    #                     pass
    #                 contestant, created = contest.contestants.get_or_create(
    #                     performer=performer,
    #                 )
    #             oa_raw = int(row[3].partition(":")[2].strip())
    #             round = session.rounds.first()
    #             performance, created = performer.performances.get_or_create(
    #                 position=oa_raw - 1,
    #                 round=round,
    #             )
    #             song_order = int(row[4].partition(":")[2].strip())
    #             song_title = row[5].partition(":")[2].strip()
    #             song, created = performance.songs.get_or_create(
    #                 performance=performance,
    #                 title=song_title,
    #                 order=song_order,
    #             )

    #             scores_raw = row[-judge_count:]

    #             judges = session.judges.order_by('panel_id')
    #             i = 0
    #             for judge in judges:
    #                 score, created = song.scores.get_or_create(
    #                     points=int(scores_raw[i]),
    #                     judge=judge,
    #                     category=judge.category,
    #                     kind=judge.kind,
    #                 )
    #                 i += 1

    #             # i = 1
    #             # for in scores_raw:
    #             #     try:
    #             #         judge = performance.round.session.judges.get(panel_id=i)
    #             #     except Exception as e:
    #             #         log.error(panel_id)
    #             #         log.error(performance.round.session.judges.all())
    #             #         raise e
    #             #     score, created = song.scores.get_or_create(
    #             #         points=int(score),
    #             #         judge=judge,
    #             #         category=judge.category,
    #             #         kind=judge.kind,
    #             #     )
    #             #     i += 1

    #     # Denormalize
    #     for session in self.sessions.all():
    #         for performer in session.performers.all():
    #             for performance in performer.performances.all():
    #                 for song in performance.songs.all():
    #                     song.calculate()
    #                     song.save()
    #                 performance.calculate()
    #                 performance.save()
    #             performer.calculate()
    #             performer.save()
    #     for session in self.sessions.all():
    #         for contest in session.contests.all():
    #             contest.rank()
    #             contest.save()
    #     # models.signals.post_save.connect(session_post_save)
    #     return


class Director(TimeStampedModel):
    """Chorus relation"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    PART = Choices(
        (1, 'director', 'Director'),
        (2, 'codirector', 'Co-Director'),
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

    performer = models.ForeignKey(
        'Performer',
        related_name='directors',
    )

    person = models.ForeignKey(
        'Person',
        related_name='choruses',
    )

    part = models.IntegerField(
        choices=PART,
        default=PART.director,
    )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        self.name = u"{0} {1} {2}".format(
            self.performer,
            self.get_part_display(),
            self.person,
        )
        super(Director, self).save(*args, **kwargs)

    def clean(self):
        if self.performer.group.kind == Group.KIND.quartet:
            raise ValidationError('Quartets do not have directors.')

    class Meta:
        unique_together = (
            ('performer', 'person',),
        )


class Group(Common):

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
        (20, 'inactive', 'Inactive',),
        (50, 'dup', 'Duplicate',),
    )

    status = models.IntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    KIND = Choices(
        (1, 'quartet', 'Quartet'),
        (2, 'chorus', 'Chorus'),
    )

    kind = models.IntegerField(
        help_text="""
            The kind of group; choices are Quartet or Chorus.""",
        choices=KIND,
        default=KIND.quartet,
    )

    chapter = models.ForeignKey(
        'Chapter',
        related_name='groups',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    @staticmethod
    def autocomplete_search_fields():
            return ("id__iexact", "name__icontains",)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        ordering = (
            'name',
        )


class Judge(TimeStampedModel):
    """Contest Judge"""

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'scheduled', 'Scheduled',),
        (20, 'confirmed', 'Confirmed',),
        (30, 'final', 'Final',),
    )

    SLOT_CHOICES = []
    for r in range(1, 6):
        SLOT_CHOICES.append((r, r))

    CATEGORY = Choices(
        (0, 'admin', 'Admin'),
        (1, 'music', 'Music'),
        (2, 'presentation', 'Presentation'),
        (3, 'singing', 'Singing'),
    )

    KIND = Choices(
        (10, 'official', 'Official'),
        (20, 'practice', 'Practice'),
        (30, 'composite', 'Composite'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    session = models.ForeignKey(
        'Session',
        related_name='judges',
        null=True,
        blank=True,
    )

    round = models.ForeignKey(
        'Round',
        related_name='judges',
    )

    status = models.IntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    category = models.IntegerField(
        choices=CATEGORY,
    )

    kind = models.IntegerField(
        choices=KIND,
    )

    slot = models.IntegerField(
        choices=SLOT_CHOICES,
    )

    person = models.ForeignKey(
        'Person',
        related_name='sessions',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'is_judge': True},
        # limit_choices_to=models.Q(certifications__isnull=False),
    )

    organization = TreeForeignKey(
        'Organization',
        related_name='judges',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    panel_id = models.IntegerField(
        null=True,
        blank=True,
    )

    @property
    def designation(self):
        return u"{0[0]}{1:1d}".format(
            self.get_category_display(),
            self.slot,
        )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        self.name = u"{0} {1} {2} {3}".format(
            self.round,
            self.get_kind_display(),
            self.get_category_display(),
            self.slot,
        )
        super(Judge, self).save(*args, **kwargs)

    class Meta:
        unique_together = (
            ('round', 'kind', 'category', 'slot'),
        )
        ordering = (
            'round',
            'kind',
            'category',
            'slot',
        )


class Organization(MPTTModel, TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        help_text="""
            The name of the resource.""",
        max_length=200,
        validators=[
            validate_trimmed,
        ],
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        # unique=True,
        max_length=255,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
        (20, 'inactive', 'Inactive',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    LEVEL = Choices(
        (0, 'international', "International"),
        (1, 'district', "District/Affiliates"),
        (2, 'division', "Division"),
    )

    level = models.IntegerField(
        help_text="""
            The level of the contest.  Note that this may be different than the level of the parent session.""",
        choices=LEVEL,
        null=True,
        blank=True,
    )

    KIND = Choices(
        ('International', [
            (0, 'international', "International"),
            (50, 'hi', "Harmony Incorporated"),
        ]),
        ('District', [
            (10, 'district', "District"),
            (20, 'noncomp', "Noncompetitive"),
            (30, 'affiliate', "Affiliate"),
        ]),
        ('Division', [
            (40, 'division', "Division"),
        ]),
    )

    kind = models.IntegerField(
        help_text="""
            The kind of organization.""",
        choices=KIND,
        null=True,
        blank=True,
    )

    start_date = models.DateField(
        help_text="""
            The founding/birth date of the resource.""",
        blank=True,
        null=True,
    )

    end_date = models.DateField(
        help_text="""
            The retirement/deceased date of the resource.""",
        blank=True,
        null=True,
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
    )

    short_name = models.CharField(
        help_text="""
            A short-form name for the resource.""",
        blank=True,
        max_length=200,
    )

    long_name = models.CharField(
        help_text="""
            A long-form name for the resource.""",
        blank=True,
        max_length=200,
    )

    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.SET_NULL,
    )

    class MPTTMeta:
        order_insertion_by = [
            'kind',
            'short_name',
        ]
        # ordering = [
        #     'tree_id',
        # ]

    def __unicode__(self):
        return u"{0}".format(self.name)


class Performance(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        # (10, 'built', 'Built',),
        # (15, 'ready', 'Ready',),
        (20, 'started', 'Started',),
        (25, 'finished', 'Finished',),
        (40, 'confirmed', 'Confirmed',),
        (50, 'final', 'Final',),
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    round = models.ForeignKey(
        'Round',
        related_name='performances',
    )

    performer = models.ForeignKey(
        'Performer',
        related_name='performances',
    )

    position = models.PositiveSmallIntegerField(
        'Position',
    )

    start_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    scheduled = DateTimeRangeField(
        help_text="""
            The scheduled performance window.""",
        null=True,
        blank=True,
    )

    actual = DateTimeRangeField(
        help_text="""
            The actual performance window.""",
        null=True,
        blank=True,
    )

    # Denormalized
    place = models.IntegerField(
        help_text="""
            The final ranking relative to this round.""",
        null=True,
        blank=True,
        editable=False,
    )

    mus_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    prs_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    sng_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    total_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    mus_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    prs_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    sng_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    total_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    @staticmethod
    def autocomplete_search_fields():
            return ("id__iexact", "name__icontains",)

    @property
    def draw(self):
        try:
            return "{0:02d}".format(self.position + 1)
        except TypeError:
            return None

    class Meta:
        ordering = (
            'round',
            'position',
        )
        unique_together = (
            ('round', 'performer',),
        )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        self.name = u"{0} {1}".format(
            self.round,
            self.performer.group,
        )
        super(Performance, self).save(*args, **kwargs)

    def calculate(self):
        if self.songs.exists():
            agg = self.songs.all().aggregate(
                mus=models.Sum('mus_points'),
                prs=models.Sum('prs_points'),
                sng=models.Sum('sng_points'),
            )
            self.mus_points = agg['mus']
            self.prs_points = agg['prs']
            self.sng_points = agg['sng']

            # Calculate total points.
            try:
                self.total_points = sum([
                    self.mus_points,
                    self.prs_points,
                    self.sng_points,
                ])
            except TypeError:
                self.total_points = None

            # Calculate percentile scores
            try:
                possible = self.round.session.size * 2
                self.mus_score = round(self.mus_points / possible, 1)
                self.prs_score = round(self.prs_points / possible, 1)
                self.sng_score = round(self.sng_points / possible, 1)
                self.total_score = round(self.total_points / (possible * 3), 1)
            except TypeError:
                self.mus_score = None
                self.prs_score = None
                self.sng_score = None

    def get_preceding(self):
        try:
            obj = self.__class__.objects.get(
                round=self.round,
                position=self.position - 1,
            )
            return obj
        except self.DoesNotExist:
            return None

    def get_next(self):
        try:
            obj = self.__class__.objects.get(
                round=self.round,
                position=self.position + 1,
            )
            return obj
        except self.DoesNotExist:
            return None

    # @transition(
    #     field=status,
    #     source=STATUS.new,
    #     target=STATUS.built,
    #     conditions=[
    #     ]
    # )
    # def build(self):
    #     return

    # @transition(
    #     field=status,
    #     source=STATUS.built,
    #     target=STATUS.ready,
    # )
    # def prep(self):
    #     return

    @transition(
        field=status,
        source=[
            # STATUS.built,
            STATUS.new,
        ],
        target=STATUS.started,
        conditions=[
            preceding_finished,
        ]
    )
    def start(self):
        # Triggered from UI
        # Creates Song and Score sentinels.
        i = 1
        while i <= 2:
            song = self.songs.create(
                performance=self,
                order=i,
            )
            for judge in self.round.session.judges.scoring():
                song.scores.create(
                    song=song,
                    judge=judge,
                    kind=judge.kind,
                )
            i += 1
        return

    @transition(
        field=status,
        source=STATUS.started,
        target=STATUS.finished,
        conditions=[
            scores_entered,
            songs_entered,
        ]
    )
    def finish(self):
        # Triggered from UI
        dixon(self)  # TODO Should this be somewhere else?  Song perhaps?
        for song in self.songs.all():
            song.confirm()
        return

    @transition(
        field=status,
        source=STATUS.finished,
        target=STATUS.confirmed,
        # conditions=[
        #     round_finished,
        # ]
    )
    def confirm(self):
        return

    @transition(
        field=status,
        source=STATUS.confirmed,
        target=STATUS.final,
        conditions=[
        ]
    )
    def finalize(self):
        return


class Performer(TimeStampedModel):

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'qualified', 'Qualified',),
        (20, 'accepted', 'Accepted',),
        (30, 'declined', 'Declined',),
        (40, 'dropped', 'Dropped',),
        (50, 'official', 'Official',),
        (60, 'finished', 'Finished',),
        (90, 'final', 'Final',),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    session = models.ForeignKey(
        'Session',
        related_name='performers',
    )

    group = models.ForeignKey(
        'Group',
        related_name='performers',
    )

    organization = TreeForeignKey(
        'Organization',
        related_name='performers',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    picture = models.ImageField(
        help_text="""
            The on-stage session picture (as opposed to the "official" photo).""",
        upload_to=generate_image_filename,
        blank=True,
        null=True,
    )

    seed = models.IntegerField(
        help_text="""
            The incoming rank based on prelim score.""",
        null=True,
        blank=True,
    )

    prelim = models.FloatField(
        help_text="""
            The incoming prelim score.""",
        null=True,
        blank=True,
    )

    men = models.IntegerField(
        help_text="""
            The number of men on stage.""",
        default=4,
        null=True,
        blank=True,
    )

    # Denormalized
    place = models.IntegerField(
        help_text="""
            The final placement/rank of the performer for the entire session (ie, not a specific contest).""",
        null=True,
        blank=True,
        editable=False,
    )

    mus_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    prs_points = models.IntegerField(
        null=True,
        editable=False,
        blank=True,
    )

    sng_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    total_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    mus_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    prs_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    sng_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    total_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    @property
    def delta_score(self):
        """ The difference between qualifying score and final score.""",
        try:
            return self.total_score - self.prelim
        except TypeError:
            return None

    @property
    def delta_place(self):
        """ The difference between qualifying rank and final rank.""",
        try:
            return self.seed - self.place
        except TypeError:
            return None

    @staticmethod
    def autocomplete_search_fields():
            return ("id__iexact", "name__icontains",)

    objects = PassThroughManager.for_queryset_class(PerformerQuerySet)()

    def __unicode__(self):
        return u"{0}".format(self.name)

    def clean(self):
        if self.singers.count() > 4:
            raise ValidationError('There can not be more than four persons in a quartet.')

    def save(self, *args, **kwargs):
        self.name = u"{0} {1}".format(
            self.session,
            self.group,
        )
        super(Performer, self).save(*args, **kwargs)

    class Meta:
        ordering = (
            'session',
            'group',
        )
        unique_together = (
            ('group', 'session',),
        )

    def calculate(self):
        # If there are no performances, skip.
        if self.performances.exists():
            agg = self.performances.all().aggregate(
                mus=models.Sum('mus_points'),
                prs=models.Sum('prs_points'),
                sng=models.Sum('sng_points'),
            )
            self.mus_points = agg['mus']
            self.prs_points = agg['prs']
            self.sng_points = agg['sng']

            # Calculate total points.
            try:
                self.total_points = sum([
                    self.mus_points,
                    self.prs_points,
                    self.sng_points,
                ])
            except TypeError:
                self.total_points = None

            # Calculate percentile
            try:
                possible = self.session.size * 2 * self.performances.count()
                self.mus_score = round(self.mus_points / possible, 1)
                self.prs_score = round(self.prs_points / possible, 1)
                self.sng_score = round(self.sng_points / possible, 1)
                self.total_score = round(self.total_points / (possible * 3), 1)
            except TypeError:
                self.mus_score = None
                self.prs_score = None
                self.sng_score = None

    @transition(field=status, source=STATUS.new, target=STATUS.qualified)
    def qualify(self):
        # Send notice?
        return "{0} Qualified".format(self)

    @transition(field=status, source=[STATUS.qualified, STATUS.declined], target=STATUS.accepted)
    def accept(self):
        # Send notice?
        return "{0} Accepted".format(self)

    @transition(field=status, source=[STATUS.qualified, STATUS.accepted], target=STATUS.declined)
    def decline(self):
        # Send notice?
        return "{0} Declined".format(self)

    @transition(
        field=status,
        source=STATUS.accepted,
        target=STATUS.official,
    )
    def register(self):
        # Triggered by contest start
        return "{0} Official".format(self)

    @transition(field=status, source=STATUS.official, target=STATUS.dropped)
    def drop(self):
        # Send notice?
        return "{0} Dropped".format(self)

    @transition(field=status, source=STATUS.official, target=STATUS.finished)
    def finish(self):
        # Send notice?
        return "{0} Finished".format(self)

    @transition(field=status, source=STATUS.finished, target=STATUS.final)
    def finalize(self):
        # Send notice?
        return "{0} Finalized".format(self)


class Person(Common):

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
        (20, 'inactive', 'Inactive',),
        (30, 'retired', 'Retired',),
        (40, 'deceased', 'Deceased',),
        (50, 'stix', 'Stix Issue',),
        (60, 'dup', 'Possible Duplicate',),
    )

    KIND = Choices(
        (1, 'individual', "Individual"),
        (2, 'team', "Team"),
    )

    kind = models.IntegerField(
        help_text="""
            Most persons are individuals; however, they can be grouped into teams for the purpose of multi-arranger songs.""",
        choices=KIND,
        default=KIND.individual,
    )

    status = models.IntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    organization = TreeForeignKey(
        'Organization',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    member = models.IntegerField(
        null=True,
        blank=True,
    )

    # Denormalization for searching
    common_name = models.CharField(
        max_length=255,
        blank=True,
        editable=False,
        default='',
    )

    # Denormalization for searching
    full_name = models.CharField(
        max_length=255,
        blank=True,
        editable=False,
        default='',
    )

    # Denormalization for searching
    formal_name = models.CharField(
        max_length=255,
        blank=True,
        editable=False,
        default='',
    )

    # Denormalization to make autocomplete work
    is_judge = models.BooleanField(
        default=False,
        editable=False,
    )

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u"{0}".format(self.name)

    @staticmethod
    def autocomplete_search_fields():
            return ("id__iexact", "name__icontains",)

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

    @property
    def nick_name(self):
        if self.name:
            name = HumanName(self.name)
            return name.nickname
        else:
            return None

    def save(self, *args, **kwargs):
        self.is_judge = self.certifications.exists()
        name = HumanName(self.name)
        if name.nickname:
            self.common_name = " ".join(filter(None, [
                u"{0}".format(name.nickname),
                u"{0}".format(name.last),
                u"{0}".format(name.suffix),
            ]))
        else:
            self.common_name = u'{0}'.format(self.name)
        self.formal_name = " ".join(filter(None, [
            u'{0}'.format(name.first),
            u'{0}'.format(name.last),
            u'{0}'.format(name.suffix),
        ]))
        super(Person, self).save(*args, **kwargs)


class Score(TimeStampedModel):
    """
        The Score is never released publicly.  These are the actual
        Judge's scores from the contest.
    """
    STATUS = Choices(
        (0, 'new', 'New',),
        (20, 'entered', 'Entered',),
        (30, 'flagged', 'Flagged',),
        (35, 'validated', 'Validated',),
        (40, 'confirmed', 'Confirmed',),
        (50, 'final', 'Final',),
    )

    CATEGORY = Choices(
        (0, 'admin', 'Admin'),
        (1, 'music', 'Music'),
        (2, 'presentation', 'Presentation'),
        (3, 'singing', 'Singing'),
    )

    KIND = Choices(
        (10, 'official', 'Official'),
        (20, 'practice', 'Practice'),
        (30, 'composite', 'Composite'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    song = models.ForeignKey(
        'Song',
        related_name='scores',
    )

    judge = models.ForeignKey(
        'Judge',
        related_name='scores',
    )

    category = models.IntegerField(
        choices=CATEGORY,
    )

    kind = models.IntegerField(
        choices=KIND,
    )

    points = models.IntegerField(
        help_text="""
            The number of points contested (0-100)""",
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(
                100,
                message='Points must be between 0 - 100',
            ),
            MinValueValidator(
                0,
                message='Points must be between 0 - 100',
            ),
        ]
    )

    class Meta:
        ordering = (
            'judge',
            'song',
        )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        self.name = u"{0} {1} {2} {3}".format(
            self.song,
            self.get_kind_display(),
            self.get_category_display(),
            self.judge.slot,
        )
        super(Score, self).save(*args, **kwargs)

    @transition(
        field=status,
        source=STATUS.new,
        target=STATUS.flagged,
        conditions=[
            score_entered,
            # TODO Could be 'performance_finished' here if want to prevent admin UI
        ]
    )
    def flag(self):
        # Triggered from dixon test in performance.finish()
        return

    @transition(
        field=status,
        source=[
            STATUS.new,
            STATUS.flagged,
        ],
        target=STATUS.validated,
        conditions=[
            score_entered,
            # TODO Could be 'performance_finished' here if want to prevent admin UI
        ]
    )
    def validate(self):
        # Triggered from dixon test in performance.finish() or UI
        return

    @transition(
        field=status,
        source=[
            STATUS.validated,
        ],
        target=STATUS.confirmed,
        conditions=[
            # song_entered,
        ]
    )
    def confirm(self):
        return

    @transition(
        field=status,
        source=STATUS.confirmed,
        target=STATUS.final,
    )
    def finalize(self):
        return


class Session(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'built', 'Built',),
        (20, 'started', 'Started',),
        (30, 'final', 'Final',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    convention = models.ForeignKey(
        'Convention',
        related_name='sessions',
    )

    KIND = Choices(
        (1, 'quartet', 'Quartet',),
        (2, 'chorus', 'Chorus',),
        (3, 'seniors', 'Seniors Quartet',),
        (4, 'collegiate', 'Collegiate Quartet',),
        (5, 'novice', 'Novice Quartet',),
    )

    kind = models.IntegerField(
        help_text="""
            The kind of session.  Generally this will be either quartet or chorus, with the exception being International and Midwinter which hold exclusive Collegiate and Senior sessions respectively.""",
        choices=KIND,
    )

    SIZE_CHOICES = []
    for r in reversed(range(1, 6)):
        SIZE_CHOICES.append((r, r))

    size = models.IntegerField(
        help_text="""
            Size of the judging panel (per category).""",
        choices=SIZE_CHOICES,
        null=True,
        blank=True,
    )

    ROUNDS_CHOICES = []
    for r in reversed(range(1, 4)):
        ROUNDS_CHOICES.append((r, r))

    num_rounds = models.IntegerField(
        help_text="""
            Number of rounds (rounds) for the session.""",
        choices=ROUNDS_CHOICES,
        default=1,
        null=True,
        blank=True,
    )

    dates = DateRangeField(
        help_text="""
            The active dates of the session.""",
        null=True,
        blank=True,
    )

    # Denormalized
    organization = TreeForeignKey(
        'Organization',
        help_text="""
            The organization that will confer the contest.  Note that this may be different than the organization running the parent session.""",
        related_name='sessions',
        editable=False,
    )

    # Denormalized
    YEAR_CHOICES = []
    for r in reversed(range(1939, (datetime.datetime.now().year + 2))):
        YEAR_CHOICES.append((r, r))

    year = models.IntegerField(
        choices=YEAR_CHOICES,
        editable=False,
    )

    # Legacy
    HISTORY = Choices(
        (0, 'new', 'New',),
        (10, 'none', 'None',),
        (20, 'pdf', 'PDF',),
        (30, 'places', 'Places',),
        (40, 'incomplete', 'Incomplete',),
        (50, 'complete', 'Complete',),
    )

    history = models.IntegerField(
        help_text="""Used to manage state for historical imports.""",
        choices=HISTORY,
        default=HISTORY.new,
    )

    history_monitor = MonitorField(
        help_text="""History last updated""",
        monitor='history',
    )

    scoresheet_pdf = models.FileField(
        help_text="""
            The historical PDF OSS.""",
        upload_to=generate_image_filename,
        blank=True,
        null=True,
    )

    scoresheet_csv = models.FileField(
        help_text="""
            The parsed scoresheet (used for legacy imports).""",
        upload_to=generate_image_filename,
        blank=True,
        null=True,
    )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        self.year = self.convention.year
        self.organization = self.convention.organization
        self.name = u"{0} {1}".format(
            self.convention,
            self.get_kind_display(),
        )
        super(Session, self).save(*args, **kwargs)

    class Meta:
        unique_together = (
            ('convention', 'kind',),
        )
        ordering = (
            '-year',
            'convention',
            'kind',
        )

    @transition(
        field=status,
        source=STATUS.built,
        target=STATUS.started,
        conditions=[
            # is_scheduled,
            # is_imsessioned,
            # has_performers,
            # has_contests,
        ],
    )
    def start(self):
        # Triggered in UI
        # TODO seed performers?
        round = self.rounds.get(num=1)
        p = 0
        for performer in self.performers.accepted().order_by('?'):
            performer.register()
            performer.save()
            round.performances.create(
                round=round,
                performer=performer,
                position=p,
            )
            p += 1
        return "{0} Started".format(self)


class Round(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'built', 'Built',),
        (15, 'ready', 'Ready',),
        (20, 'started', 'Started',),
        (25, 'finished', 'Finished',),
        (30, 'final', 'Final',),
    )

    KIND = Choices(
        (1, 'finals', 'Finals'),
        (2, 'semis', 'Semi-Finals'),
        (3, 'quarters', 'Quarter-Finals'),
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    session = models.ForeignKey(
        'Session',
        related_name='rounds',
    )

    kind = models.IntegerField(
        choices=KIND,
    )

    num = models.IntegerField(
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    dates = DateRangeField(
        help_text="""
            The active dates of the resource.""",
        null=True,
        blank=True,
    )

    slots = models.IntegerField(
        null=True,
        blank=True,
    )

    stix_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )

    class Meta:
        ordering = (
            'session',
            'kind',
        )
        unique_together = (
            ('session', 'kind',),
        )

    def save(self, *args, **kwargs):
        self.name = u"{0} {1}".format(
            self.session,
            self.get_kind_display(),
        )
        super(Round, self).save(*args, **kwargs)

    @staticmethod
    def autocomplete_search_fields():
            return ("id__iexact", "name__icontains",)

    def __unicode__(self):
        return u"{0}".format(self.name)

    def get_preceding(self):
        try:
            obj = self.__class__.objects.get(
                contest=self.contest,
                kind=self.kind + 1,
            )
            return obj
        except self.DoesNotExist:
            return None

    def get_next(self):
        try:
            obj = self.__class__.objects.get(
                contest=self.contest,
                kind=self.kind - 1,
            )
            return obj
        except self.DoesNotExist:
            return None

    def next_performance(self):
        try:
            return self.performances.filter(
                status=self.performances.model.STATUS.ready,
            ).order_by('position').first()
        except self.performances.model.DoesNotExist:
            return None

    # @transition(
    #     field=status,
    #     source=STATUS.new,
    #     target=STATUS.built,
    # )
    # def build(self):
    #     return

    # @transition(
    #     field=status,
    #     source=STATUS.built,
    #     target=STATUS.ready,
    #     # conditions=[
    #     #     contest_started,
    #     # ]
    # )
    # def prep(self):
    #     p = 0
    #     for performer in self.contest.performers.official().order_by('?'):
    #         self.performances.create(
    #             round=self,
    #             performer=performer,
    #             position=p,
    #         )
    #         p += 1
    #     return

    @transition(
        field=status,
        source=STATUS.new,
        target=STATUS.started,
        conditions=[
            # round_drawn,
            # round_scheduled,
            # contest_started,
            # preceding_round_finished,
        ]
    )
    def start(self):
        # Triggered in UI
        return

    @transition(
        field=status,
        source=STATUS.started,
        target=STATUS.finished,
        conditions=[
            performances_finished,
            scores_validated,
        ]
    )
    def finish(self):
        # TODO Validate performances over
        cursor = []
        i = 1
        for performance in self.performances.order_by('-total_points'):
            try:
                match = performance.total_points == cursor[0].total_points
            except IndexError:
                performance.place = i
                performance.save()
                cursor.append(performance)
                continue
            if match:
                performance.place = i
                i += len(cursor)
                performance.save()
                cursor.append(performance)
                continue
            else:
                i += 1
                performance.place = i
                performance.save()
                cursor = [performance]
        return "Round Ended"

    @transition(field=status, source=STATUS.finished, target=STATUS.final)
    def finalize(self):
        return
        # # TODO Some validation
        # try:
        #     # TODO This is an awful lot to be in a try/except; refactor?
        #     next_round = self.contest.rounds.get(
        #         kind=(self.kind - 1),
        #     )
        #     qualifiers = self.performances.filter(
        #         place__lte=next_round.slots,
        #     ).order_by('?')
        #     p = 0
        #     for qualifier in qualifiers:
        #         l = next_round.performances.create(
        #             performer=qualifier.performer,
        #             position=p,
        #             # start=next_round.start,
        #         )
        #         p += 1
        #         p1 = l.songs.create(performance=l, order=1)
        #         p2 = l.songs.create(performance=l, order=2)
        #         for j in self.contest.judges.scoring():
        #             p1.scores.create(
        #                 song=p1,
        #                 judge=j,
        #             )
        #             p2.scores.create(
        #                 song=p2,
        #                 judge=j,
        #             )
        # except self.DoesNotExist:
        #     pass
        # return 'Round Confirmed'
    # def draw_contest(self):
    #     cs = self.performers.order_by('?')
    #     round = self.rounds.get(kind=self.rounds)
    #     p = 0
    #     for c in cs:
    #         round.performances.create(
    #             performer=c,
    #             position=p,
    #             start=round.start,
    #         )
    #         p += 1
    #     self.status = self.STATUS.ready
    #     self.save()


class Singer(TimeStampedModel):
    """Quartet Relation"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    PART = Choices(
        (1, 'tenor', 'Tenor'),
        (2, 'lead', 'Lead'),
        (3, 'baritone', 'Baritone'),
        (4, 'bass', 'Bass'),
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

    performer = models.ForeignKey(
        'Performer',
        related_name='singers',
    )

    person = models.ForeignKey(
        'Person',
        related_name='quartets',
    )

    part = models.IntegerField(
        choices=PART,
    )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def clean(self):
        # if self.performer.group.kind == Group.CHORUS:
        #     raise ValidationError('Choruses do not have quartet singers.')
        if self.part:
            if [s['part'] for s in self.performer.singers.values(
                'part'
            )].count(self.part) > 1:
                raise ValidationError('There can not be more than one of the same part in a quartet.')

    class Meta:
        unique_together = (
            ('performer', 'person',),
        )
        ordering = (
            '-name',
        )

    def save(self, *args, **kwargs):
        self.name = u"{0} {1} {2}".format(
            self.performer,
            self.get_part_display(),
            self.person,
        )
        super(Singer, self).save(*args, **kwargs)


class Song(TimeStampedModel):
    STATUS = Choices(
        (0, 'new', 'New',),
        # (10, 'built', 'Built',),
        # (20, 'entered', 'Entered',),
        # (30, 'flagged', 'Flagged',),
        # (35, 'validated', 'Validated',),
        (40, 'confirmed', 'Confirmed',),
        (50, 'final', 'Final',),
    )

    ORDER = Choices(
        (1, 'first', 'First'),
        (2, 'second', 'Second'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    status_monitor = MonitorField(
        help_text="""Status last updated""",
        monitor='status',
    )

    performance = models.ForeignKey(
        'Performance',
        related_name='songs',
    )

    order = models.IntegerField(
        choices=ORDER,
    )

    title = models.CharField(
        max_length=255,
        blank=True,
    )

    arranger = models.CharField(
        max_length=255,
        blank=True,
    )

    is_parody = models.BooleanField(
        default=False,
    )

    catalog = models.ForeignKey(
        'Catalog',
        related_name='songs',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    tune = models.ForeignKey(
        'Tune',
        related_name='songs',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # Denormalized values
    mus_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    prs_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    sng_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    total_points = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    mus_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    prs_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    sng_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    total_score = models.FloatField(
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        ordering = [
            'performance',
            'order',
        ]
        unique_together = (
            ('performance', 'order',),
        )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def save(self, *args, **kwargs):
        self.name = u"{0} {1} {2}".format(
            self.performance,
            'Song',
            self.order,
        )
        super(Song, self).save(*args, **kwargs)

    def calculate(self):
        if self.scores.exists():
            # Only use the Scores model when we have scores
            # from a judging panel.  Otherwise, use what's
            # already there (typically imported).
            scores = self.scores.exclude(
                kind=self.scores.model.KIND.practice,
            ).order_by(
                'category',
            ).values(
                'category',
            ).annotate(
                total=models.Sum('points')
            )
            for score in scores:
                if score['category'] == self.scores.model.CATEGORY.music:
                    self.mus_points = score['total']
                if score['category'] == self.scores.model.CATEGORY.presentation:
                    self.prs_points = score['total']
                if score['category'] == self.scores.model.CATEGORY.singing:
                    self.sng_points = score['total']

            # Calculate total points.
            try:
                self.total_points = sum([
                    self.mus_points,
                    self.prs_points,
                    self.sng_points,
                ])
            except TypeError:
                self.total_points = None

            # Calculate percentile scores.
            try:
                possible = self.performance.round.session.size
                self.mus_score = round(self.mus_points / possible, 1)
                self.prs_score = round(self.prs_points / possible, 1)
                self.sng_score = round(self.sng_points / possible, 1)
                self.total_score = round(self.total_points / (possible * 3), 1)
            except TypeError:
                self.mus_score = None
                self.prs_score = None
                self.sng_score = None
    # @transition(
    #     field=status,
    #     source=[
    #         STATUS.new,
    #     ],
    #     target=STATUS.entered,
    #     conditions=[
    #         song_entered,
    #     ]
    # )
    # def enter(self):
    #     # Triggered from form/admin
    #     return

    @transition(
        field=status,
        source=[
            STATUS.new,
        ],
        target=STATUS.confirmed,
        conditions=[
            song_entered,
            # TODO could put `performance_finished` here if want to prevent UI
        ]
    )
    def confirm(self):
        # Triggered from performance.finish()
        return

    @transition(
        field=status,
        source=STATUS.confirmed,
        target=STATUS.final,
    )
    def finalize(self):
        return


class Tune(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=200,
        unique=True,
    )

    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        unique=True,
        max_length=255,
    )

    @staticmethod
    def autocomplete_search_fields():
            return ("id__iexact", "name__icontains",)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u"{0}".format(self.name)


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(
        unique=True,
        help_text="""Your email address will be your username.""",
    )
    name = models.CharField(
        max_length=200,
        help_text="""Your full name.""",
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_staff = models.BooleanField(
        default=False,
    )
    date_joined = models.DateField(
        auto_now_add=True,
    )

    objects = UserManager()

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email
