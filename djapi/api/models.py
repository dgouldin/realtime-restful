from __future__ import absolute_import
from uuid import uuid4

from django_pg import models

class Todo(models.Model):
    id = models.UUIDField(primary_key=True)
    text = models.TextField(blank=True)
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid4()
        super(Todo, self).save(*args, **kwargs)
