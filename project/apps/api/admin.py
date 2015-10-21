from django.contrib import admin

from django_object_actions import (
    DjangoObjectActions,
    takes_instance_or_queryset,
)

from .models import (
    Convention,
    Contest,
    Contestant,
    Group,
    District,
    Song,
    Person,
    Performance,
    Score,
    Judge,
    Singer,
    Director,
    Session,
    Award,
    Appearance,
    User,
)

from grappelli.forms import GrappelliSortableHiddenMixin


class AppearancesInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    fields = (
        'contestant',
        'session',
        'position',
        'draw',
        'start',
    )
    sortable_field_name = "position"
    show_change_link = True

    model = Appearance
    extra = 0
    raw_id_fields = (
        'contestant',
    )
    autocomplete_lookup_fields = {
        'fk': [
            'contestant',
        ]
    }
    can_delete = True
    readonly_fields = (
        'draw',
    )
    classes = ('grp-collapse grp-open',)


class AwardsInline(admin.TabularInline):
    model = Award
    fields = (
        'name',
    )
    extra = 0
    can_delete = True
    show_change_link = True
    classes = ('grp-collapse grp-closed',)


class ContestantsInline(admin.TabularInline):
    fields = (
        'contest',
        'group',
        'district',
        # 'seed',
        # 'prelim',
        # 'place',
        # 'total_score',
        'men',
    )
    ordering = (
        'place',
        'seed',
        'group',
    )
    show_change_link = True

    model = Contestant
    extra = 0
    raw_id_fields = (
        # 'contest',
        'group',
    )
    autocomplete_lookup_fields = {
        'fk': [
            # 'contest',
            'group',
        ]
    }
    can_delete = True
    classes = ('grp-collapse grp-closed',)


class DirectorsInline(admin.TabularInline):
    fields = (
        'contestant',
        'person',
        'part',
    )
    ordering = (
        'part',
        'contestant',
    )
    model = Director
    extra = 0
    raw_id_fields = (
        'person',
        'contestant',
    )
    autocomplete_lookup_fields = {
        'fk': [
            'person',
            'contestant',
        ]
    }
    can_delete = True
    classes = ('grp-collapse grp-closed',)


class JudgesInline(admin.TabularInline):
    model = Judge
    fields = (
        'contest',
        'person',
        'district',
        'category',
        'slot',
        # 'is_practice',
    )
    ordering = (
        'category',
        'slot',
    )
    extra = 0
    raw_id_fields = (
        'person',
    )
    autocomplete_lookup_fields = {
        'fk': [
            'person',
        ]
    }
    can_delete = True
    show_change_link = True
    classes = ('grp-collapse grp-closed',)


class PerformancesInline(admin.TabularInline):
    fields = (
        'appearance',
        'order',
        'song',
        'mus_points',
        'prs_points',
        'sng_points',
    )
    ordering = (
        'appearance',
        'order',
    )
    model = Performance
    extra = 0
    raw_id_fields = (
        'appearance',
        'song',
    )
    autocomplete_lookup_fields = {
        'fk': [
            'appearance',
            'song',
        ]
    }

    can_delete = True
    show_change_link = True


class ScoresInline(admin.TabularInline):
    model = Score
    fields = (
        'performance',
        'judge',
        'category',
        'points',
    )
    ordering = (
        'judge',
    )
    extra = 0
    raw_id_fields = (
        'judge',
    )
    autocomplete_lookup_fields = {
        'fk': [
            'judge',
        ]
    }
    can_delete = True
    show_change_link = True


class SessionsInline(admin.StackedInline):
    fields = (
        'contest',
        'kind',
        'start',
    )
    ordering = (
        'contest',
        'kind',
    )
    show_change_link = True

    model = Session
    extra = 0
    # raw_id_fields = (
    #     'contest',
    # )
    # autocomplete_lookup_fields = {
    #     'fk': [
    #         'contest',
    #     ]
    # }
    can_delete = True
    classes = ('grp-collapse grp-closed',)


class SingersInline(admin.TabularInline):
    model = Singer
    fields = (
        'contestant',
        'person',
        'part',
    )
    ordering = (
        'part',
        'contestant',
    )
    extra = 0
    raw_id_fields = (
        'person',
        # 'contestant',
    )
    autocomplete_lookup_fields = {
        'fk': [
            'person',
            # 'contestant',
        ]
    }
    can_delete = True
    show_change_link = True
    classes = ('grp-collapse grp-closed',)


@admin.register(Appearance)
class Appearance(admin.ModelAdmin):
    save_on_top = True
    change_list_template = "admin/change_list_filter_sidebar.html"

    # inlines = [
    #     PerformancesInline,
    # ]
    list_display = [
        'name',
        'draw',
        'start',
    ]
    list_filter = [
        'status',
        'session',
        'contestant__contest__level',
        'contestant__contest__kind',
        'contestant__contest__year',
    ]

    fields = [
        'name',
        ('status', 'status_monitor',),
        'contest',
        'session',
        'contestant',
        ('draw', 'start',),
        ('mus_points', 'prs_points', 'sng_points', 'total_points',),
        ('mus_score', 'prs_score', 'sng_score', 'total_score',),
    ]

    readonly_fields = [
        'name',
        'mus_points',
        'prs_points',
        'sng_points',
        'total_points',
        'mus_score',
        'prs_score',
        'sng_score',
        'total_score',
        'draw',
    ]

    raw_id_fields = (
        'contestant',
        'contest',
        'session',
    )
    autocomplete_lookup_fields = {
        'fk': [
            'contestant',
            'contest',
            'session',
        ]
    }


@admin.register(Contest)
class ContestAdmin(DjangoObjectActions, admin.ModelAdmin):
    @takes_instance_or_queryset
    def import_legacy(self, request, queryset):
        for obj in queryset:
            obj.import_legacy()
    import_legacy.label = 'Import Legacy'

    change_list_template = "admin/change_list_filter_sidebar.html"
    # change_list_filter_template = "admin/filter_listing.html"
    save_on_top = True
    objectactions = [
        'import_legacy',
    ]

    inlines = [
        ContestantsInline,
        JudgesInline,
        SessionsInline,
    ]

    search_fields = (
        'name',
    )

    list_filter = (
        'status',
        'goal',
        'level',
        'kind',
        'year',
        'district',
    )

    list_display = (
        'name',
        'status',
        'rep',
        'admin',
        'goal',
        'rounds',
        'panel',
    )

    fields = (
        'name',
        ('status', 'status_monitor',),
        'level',
        'kind',
        'goal',
        'year',
        'district',
        ('rounds', 'panel',),
        ('rep', 'admin',),
    )

    raw_id_fields = (
        'rep',
        'admin',
    )

    autocomplete_lookup_fields = {
        'fk': [
            'rep',
            'admin',
        ]
    }
    readonly_fields = (
        'name',
        'status_monitor',
    )

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "convention":
    #         try:
    #             parent_obj_id = request.resolver_match.args[0]
    #             obj = Contest.objects.get(pk=parent_obj_id)
    #             kwargs["queryset"] = Convention.objects.filter(year=obj.year)
    #         except IndexError:
    #             pass
    #     return super(ContestAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Contestant)
class ContestantAdmin(admin.ModelAdmin):
    @takes_instance_or_queryset
    def update_contestants(self, request, queryset):
        for obj in queryset:
            obj.save()
    update_contestants.label = 'Update Contestants'

    change_list_template = "admin/change_list_filter_sidebar.html"

    objectactions = [
        'update_contestants',
    ]

    inlines = [
        SingersInline,
        DirectorsInline,
        AwardsInline,
    ]

    list_display = (
        'name',
        'status',
        'seed',
        'prelim',
        'mus_score',
        'prs_score',
        'sng_score',
        'total_score',
        'men',
        'place',
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'status',
        'contest__level',
        'contest__kind',
        'contest__year',
    )

    raw_id_fields = (
        'contest',
        'group',
    )

    autocomplete_lookup_fields = {
        'fk': [
            'contest',
            'group',
        ]
    }
    fields = (
        'name',
        ('status', 'status_monitor',),
        'contest',
        'group',
        'district',
        ('seed', 'prelim',),
        ('place', 'men',),
        ('mus_points', 'prs_points', 'sng_points', 'total_points',),
        ('mus_score', 'prs_score', 'sng_score', 'total_score',),
    )

    readonly_fields = (
        'name',
        'mus_points',
        'prs_points',
        'sng_points',
        'total_points',
        'mus_score',
        'prs_score',
        'sng_score',
        'total_score',
    )

    save_on_top = True


@admin.register(Convention)
class ConventionAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )

    list_display = (
        'name',
        'status',
        'status_monitor',
        'location',
        'dates',
        'kind',
        'year',
        'district',
    )

    fields = (
        'name',
        ('status', 'status_monitor',),
        ('location', 'timezone',),
        'dates',
        'district',
        'kind',
        'year',
    )

    list_filter = (
        'status',
        'kind',
        'year',
        'district',
    )

    readonly_fields = (
        'name',
        'status_monitor',
    )
    save_on_top = True


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )

    list_display = (
        'name',
        'location',
        'website',
        'facebook',
        'twitter',
        'email',
        'phone',
        'picture',
        'long_name',
        'kind',
    )

    fields = (
        'name',
        'long_name',
        'kind',
        ('start', 'end',),
        'location',
        'website',
        'facebook',
        'twitter',
        'email',
        'phone',
        'picture',
        'description',
        'notes',
    )

    list_filter = (
        'kind',
    )

    save_on_top = True


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )

    list_display = (
        'name',
        'location',
        'website',
        'facebook',
        'twitter',
        'email',
        'phone',
        'chapter_name',
        'chapter_code',
        'picture',
    )

    fields = (
        'name',
        'kind',
        ('start', 'end',),
        'location',
        'website',
        'facebook',
        'twitter',
        'email',
        'phone',
        'picture',
        'description',
        ('chapter_name', 'chapter_code',),
        'notes',
    )

    list_filter = (
        'kind',
    )

    save_on_top = True


@admin.register(Judge)
class Judge(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    save_on_top = True
    fields = [
        'name',
        'status',
        'contest',
        'person',
        'district',
        ('category', 'slot',),
    ]

    list_display = [
        'name',
        'person',
        'district',
    ]

    list_filter = (
        'status',
        'contest__level',
        'contest__kind',
        'contest__year',
    )

    raw_id_fields = (
        'contest',
        'person',
    )

    autocomplete_lookup_fields = {
        'fk': [
            'contest',
            'person',
        ]
    }

    readonly_fields = [
        'name',
    ]


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
        'name',
        'status',
        'song',
        'mus_points',
        'prs_points',
        'sng_points',
        'total_points'
    )

    search_fields = (
        'name',
    )

    fields = [
        'name',
        ('status', 'status_monitor',),
        ('order', 'song',),
        ('mus_points', 'prs_points', 'sng_points', 'total_points',),
        ('mus_score', 'prs_score', 'sng_score', 'total_score',),
    ]

    inlines = [
        ScoresInline,
    ]

    list_filter = (
        'status',
        'appearance__contestant__contest__level',
        'appearance__contestant__contest__kind',
        'appearance__contestant__contest__year',
    )

    readonly_fields = (
        'name',
        'total_points',
        'mus_score',
        'prs_score',
        'sng_score',
        'total_score',
    )
    raw_id_fields = (
        'appearance',
        'song',
    )
    autocomplete_lookup_fields = {
        'fk': [
            'appearance',
            'song',
        ]
    }


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )

    save_on_top = True
    list_display = (
        'name',
        'location',
        'website',
        'facebook',
        'twitter',
        'email',
        'phone',
        'picture',
    )

    fields = (
        'name',
        'kind',
        ('start', 'end',),
        'location',
        'website',
        'facebook',
        'twitter',
        'email',
        'phone',
        'picture',
        'description',
        'notes',
    )

    inlines = [
        DirectorsInline,
        SingersInline,
        JudgesInline,
    ]


@admin.register(Score)
class Score(admin.ModelAdmin):
    save_on_top = True


@admin.register(Session)
class Session(admin.ModelAdmin):
    save_on_top = True
    list_display = [
        'name',
        'status',
        'start',
    ]
    fields = [
        'name',
        ('status', 'status_monitor',),
        'contest',
        ('kind', 'start',),
    ]

    readonly_fields = [
        'name',
        'status_monitor',
    ]

    list_filter = (
        'status',
        'contest__level',
        'contest__kind',
        'contest__year',
    )

    raw_id_fields = (
        'contest',
    )

    autocomplete_lookup_fields = {
        'fk': [
            'contest',
        ]
    }

    inlines = [
        AppearancesInline,
    ]


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    save_on_top = True
    fields = (
        'name',
    )

    search_fields = (
        'name',
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    save_on_top = True
