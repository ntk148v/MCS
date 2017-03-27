from django_rq import job


@job()
def upload_object(file, file_path):
    """Upload object to cloudnode"""
    # TODO:
    # from calplus import provider as calplus_provider
    # from calplus.client import Client
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
    # result = convert_format(cal_client.upload_object('files', file_path, contents=file.chunks()))
    # return result
    pass
