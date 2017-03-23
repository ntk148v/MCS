from __future__ import unicode_literals

from django.db import models


class CloudRing(models.Model):

    class Meta:
        db_table = 'cloudring'
        app_label = 'dashboard'

    identifier = models.CharField(max_length=50)
    USERNAME_FIELD = 'identifier'


class CloudNode(models.Model):

    class Meta:
        db_table = 'cloudnode'
        app_label = 'dashboard'

    identifier = models.CharField(max_length=50)
    config = models.TextField()
    type = models.TextField()
    ring = models.ForeignKey('CloudRing', on_delete=models.CASCADE)

    USERNAME_FIELD = 'identifier'


class ObjectData(models.Model):

    class Meta:
        db_table = 'objectdata'
        app_label = 'dashboard'

    data = models.FileField(name='data')
    last_modified = models.DateTimeField(auto_now_add=True)


class FileManager(models.Manager):
    pass


class File(models.Model):

    class Meta:
        db_table = 'file'
        app_label = 'dashboard'

    name = models.CharField('name', max_length=255)
    # owner = models.ForeignKey('User')
    last_modified = models.DateTimeField('last_modified',
                                         auto_now_add=True)
    content = models.FileField('content', null=True)
    is_folder = models.BooleanField('is_folder',
                                    default=True)
    is_root = models.BooleanField('is_root',
                                  default=False)
    size = models.IntegerField('size', null=True,
                               editable=False)
    parent = models.ForeignKey('self', verbose_name=('parent'),
                               null=True, blank=True,
                               related_name='children')

    objects = FileManager()

    def contains_folder(self, folder_name):
        try:
            self.children.get(name=folder_name)
            return True
        except File.DoesNotExist:
            return False
