import json
from functools import partial

from better_json_widget.widgets import BetterJsonWidget
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.forms import ChoiceField, ModelForm

from db import models

admin.site.site_header = "Feed WatchDog"
admin.site.unregister(Group)


def load_configuration() -> dict:
    with open(settings.SHARED_CONFIG_PATH) as fp:
        return json.load(fp)


def get_choices(type):  # noqa: PLW0622
    config = load_configuration()
    return [(item["type"], item["type"]) for item in config["handlers"][type]]


def fields_config(type):  # noqa: PLW0622
    config = load_configuration()
    return {item["type"]: item["options"] for item in config["handlers"][type]}


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
    list_display = ("name", "fetcher_type", "parser_type", "tags")
    ordering = ("name",)
    form = SourceAdminForm
    prepopulated_fields = {"slug": ("name",)}
    inlines = (StreamInlineAdmin,)


class ReceiverAdminForm(ModelForm):
    type = ChoiceField(choices=partial(get_choices, "receivers"))

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
    list_display = ("name", "type")
    ordering = ("name",)
    form = ReceiverAdminForm
    prepopulated_fields = {"slug": ("name",)}
    inlines = (StreamInlineAdmin,)


@admin.register(models.Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ("__str__", "source", "receiver", "active")
    ordering = ("source", "receiver")
    list_select_related = ("source", "receiver")
