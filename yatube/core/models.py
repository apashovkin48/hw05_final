# core/models.py
from django.db import models


class BaseModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        help_text='Дата создания, ставится автоматически'
    )

    class Meta:
        abstract = True
