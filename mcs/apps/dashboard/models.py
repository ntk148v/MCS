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

    STATE = {
        'full': 'FULL',
        'ok': 'OK',
        'corrupt': 'CORRPUT',
    }

    # Hash from ip_address
    identifier = models.CharField(max_length=50)
    config = models.TextField()
    type = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    state = models.CharField(max_length=1, choices=STATE)
    ring = models.ForeignKey('CloudRing', on_delete=models.CASCADE)

    USERNAME_FIELD = 'identifier'

    def init_finger_table(self):
        pass

    def init_successor_list(self):
        pass

    def update_successor_list(self):
        pass

    # called periodically. n asks the successor
    # about its predecessor, verifies if n's immediate
    # successor is consistent, and tells the successor about n
    def stabilize(self):
        pass

    # called periodically. refreshes finger table entries.
    # next stores the index of the finger to fix
    def fix_fingers(self):
        pass

    # ask node n to find the successor of id
    def find_successor(self, object_id):
        pass

    # called periodically. checks whether predecessor has failed.
    def check_predecessor(self):
        pass

    # search the local table for the highest predecessor of id
    def closest_preceding_node(self, object_id):
        pass

    def create(self):
        pass

    # join a Chord ring containing node n'.
    def join(self, node_id):
        pass


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
    path = models.CharField('path', null=True, max_length=255)
    # TODO: Change upload_to folder to /tmp/<user_id>/%Y/%m/%d
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

    def contains_file(self, folder_name):
        try:
            self.children.get(name=folder_name)
            return True
        except File.DoesNotExist:
            return False
