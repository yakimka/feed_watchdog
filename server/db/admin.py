import json
from functools import partial

from better_json_widget.widgets import BetterJsonWidget
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.forms import ChoiceField, ModelForm
from django.utils.translation import ngettext

from db import models

admin.site.site_header = "Feed WatchDog"
admin.site.unregister(Group)


@admin.action(description="Resave objects")
def make_published(modeladmin, request, queryset):
    _i = 0
    for _i, item in enumerate(queryset, start=1):
        item.save()

    modeladmin.message_user(
        request,
        ngettext(
            "{} object was successfully resaved.",  # noqa P103
            "{} objects were successfully resaved.",  # noqa P103
            _i,
        ).format(_i),
        messages.SUCCESS,
    )


def load_configuration() -> dict:
    with open(settings.SHARED_CONFIG_PATH) as fp:
        return json.load(fp)


def get_choices(type) -> list[tuple[str, str]]:  # noqa: PLW0622
    config = load_configuration()
    return [(item["type"], item["type"]) for item in config["handlers"][type]]


def fields_config(type) -> dict:  # noqa: PLW0622
    config = load_configuration()
    return {item["type"]: item["options"] for item in config["handlers"][type]}


def message_template_help_text() -> str:
    config = load_configuration()
    fields_mapping = {}

    for item in config["handlers"]["parsers"]:
        if fields := item.get("return_fields_schema"):
            fields_mapping[item["type"]] = list(fields)
    parts = ["Available fields:"]
    parts.extend(
        f"<b>{key}:</b> {', '.join(fields)}"
        for key, fields in fields_mapping.items()
    )

    return "<br>".join(parts)


class SourceAdminForm(ModelForm):
    fetcher_type = ChoiceField(choices=partial(get_choices, "fetchers"))
    parser_type = ChoiceField(choices=partial(get_choices, "parsers"))

    class Meta:
        model = models.Source
        fields = "__all__"
        widgets = {
            "fetcher_options": BetterJsonWidget(
                follow_field="fetcher_type",
                schema_mapping=partial(fields_config, "fetchers"),
            ),
            "parser_options": BetterJsonWidget(
                follow_field="parser_type",
                schema_mapping=partial(fields_config, "parsers"),
            ),
        }


class StreamInlineAdmin(admin.TabularInline):
    model = models.Stream
    extra = 0


@admin.register(models.Source)
class SourceAdmin(admin.ModelAdmin):
    search_fields = ("name", "tags")
    list_display = ("name", "fetcher_type", "parser_type", "tags")
    ordering = ("name",)
    form = SourceAdminForm
    prepopulated_fields = {"slug": ("name",)}
    inlines = (StreamInlineAdmin,)


class ReceiverAdminForm(ModelForm):
    type = ChoiceField(choices=partial(get_choices, "receivers"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message_template"].help_text = message_template_help_text()

    class Meta:
        model = models.Receiver
        fields = "__all__"
        widgets = {
            "options": BetterJsonWidget(
                follow_field="type",
                schema_mapping=partial(fields_config, "receivers"),
            ),
        }


@admin.register(models.Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "type")
    ordering = ("name",)
    form = ReceiverAdminForm
    prepopulated_fields = {"slug": ("name",)}
    inlines = (StreamInlineAdmin,)


class FilterInlineAdmin(admin.TabularInline):
    model = models.StreamFilter
    extra = 0


@admin.register(models.Stream)
class StreamAdmin(admin.ModelAdmin):
    search_fields = ("source__name", "receiver__name", "uid")
    list_display = (
        "__str__",
        "source",
        "receiver",
        "active",
    )
    list_editable = (
        "receiver",
        "active",
    )
    ordering = ("source", "receiver")
    list_select_related = ("source", "receiver")
    inlines = (FilterInlineAdmin,)
    actions = (make_published,)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields[
            "message_template"
        ].help_text = message_template_help_text()
        return form


class FilterAdminForm(ModelForm):
    type = ChoiceField(choices=partial(get_choices, "filters"))

    class Meta:
        model = models.Source
        fields = "__all__"
        widgets = {
            "options": BetterJsonWidget(
                follow_field="type",
                schema_mapping=partial(fields_config, "filters"),
            ),
        }


@admin.register(models.Filter)
class FilterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
    )
    ordering = ("name",)
    form = FilterAdminForm


@admin.register(models.Interval)
class IntervalAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "cron",
        "default",
    )
    ordering = ("name",)
