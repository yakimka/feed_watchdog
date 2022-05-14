import random

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from domain import models as domain_models


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_("name"), max_length=100)
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return str(self.username)

    def clean(self):
        super().clean()
        self.email = type(self).objects.normalize_email(self.email)


class Source(models.Model):
    name = models.CharField(max_length=1024)
    slug = models.SlugField()
    url = models.URLField()
    parser_type = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    encoding = models.CharField(max_length=16, blank=True)
    tags = models.TextField(blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return str(self.name)

    def to_domain(self) -> domain_models.Source:
        return domain_models.Source(
            slug=self.slug,
            name=self.name,
            description=self.description,
            url=self.url,
            encoding=self.encoding,
            parser_type=self.parser_type,
            tags=[tag.strip() for tag in self.tags.split(";") if tag.strip()],
        )


class Receiver(models.Model):
    name = models.CharField(max_length=1024)
    slug = models.SlugField()
    type = models.CharField(max_length=32)
    recipient = models.CharField(max_length=1024)
    message_template = models.TextField()

    def __str__(self):
        return str(self.name)

    def to_domain(self) -> domain_models.Receiver:
        return domain_models.Receiver(
            name=self.name,
            slug=self.slug,
            type=self.type,
            recipient=self.recipient,
            message_template=self.message_template,
        )


def generate_uid(length=12):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(
        random.choice(chars) for _ in range(length)  # noqa: S311, DUO102
    )


class Stream(models.Model):
    uid = models.CharField(max_length=12, default=generate_uid, unique=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, db_index=True)
    receiver = models.ForeignKey(
        Receiver, on_delete=models.CASCADE, db_index=True
    )
    active = models.BooleanField(default=True)
    has_message_template = models.BooleanField(default=False)
    message_template = models.TextField(blank=True)

    def __str__(self):
        return f"{self.source} -> {self.receiver}"

    def to_domain(self) -> domain_models.Stream:
        return domain_models.Stream(
            uid=self.uid,
            source=self.source.to_domain(),
            receiver=self.receiver.to_domain(),
            message_template=self.message_template
            if self.has_message_template
            else "",
        )
