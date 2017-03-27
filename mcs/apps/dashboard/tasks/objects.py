# from calplus import provider as calplus_provider
# from calplus.client import Client

import django_rq
from django_rq import job


SCHEDULER = django_rq.get_scheduler('default')


def get_available_replica(filepath, number_of_replicas):
    # TODO:
    # _count = 1
    # while number_of_replicas >= _count:
    #     replica_id = hashlib.md5(filepath + '_' + str(_count))
    #     replica = models.Replica.objects.get(identifier=replica_id)
    #     # Check its status, if OK get it.
    #     if replica.status == 'AVAILABLE':
    #         break
    #         return replica
    #     _count += 1
    # return None
    pass


@job()
def upload_object(file, file_path):
    """Upload object to cloudnode"""
    # TODO:
    # import hashlib
    #
    # file_id = hashlib.md5(file_path).hexdigest()
    # # Find succecssor - find the node will store the file
    # # Should return instance of CloudNode.
    # cloud_node = find_successor(file_id)
    #
    # _provider = calplus_provider.Provider(cloud_node.type, dict(json.loads(provider.config)))
    # cal_client = Client(version='1.0.0',
    #                     resource='object_storage',
    #                     provider=_provider)
    # # Check if container named 'files' exists
    # if not cal_client.stat_container('files'):
    #     cal_client.create_container('files')
    # # Upload file content
    # # Convert all response to the same format
    # result = []
    # _count = 1
    # while number_of_replicas >= _count:
    #     replica_id = hashlib.md5(filepath + '_' + str(_count))
    #     result.append(convert_format(cal_client.upload_object('files', replica_id, contents=file.chunks())))
    # return result
    pass


def download_object(filepath, number_of_replicas):
    """Download object from Cloudnode"""
    # TODO:
    # # With filepath get all its replica
    # # Then check their status.
    # replica = get_available_replica(filepath, number_of_replicas=number_of_replicas)
    # # If don't find any available replica. Raise exception.
    # # Or may be easier if block download request before. If ObjectMetadata status
    # # is NOT_AVAILABLE (it means all replicas of this object are NOT_AVAILABLE.
    # if not replica:
    #     raise ObjectNotAvailableException()
    # replica_id = replica.id
    # cloud_node = find_successor(replica_id)
    # _provider = calplus_provider.Provider(cloud_node.type, dict(json.loads(provider.config)))
    # cal_client = Client(version='1.0.0',
    #                     resource='object_storage',
    #                     provider=_provider)
    # # Convert all response to the same format
    # result = conver_format(cal_client.download_object('files', replica_id))
    # return result
    pass
