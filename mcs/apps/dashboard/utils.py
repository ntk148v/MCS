def handle_uploaded_file(file):
    #
    # TODO:
    # choose CloudNode by Chord
    # cloud_node = models.CloudNode.objects.get(identifier=tmp)
    # _provider = calplus_provider.Provider(cloud_node.type,
    #                                      cloud_node.config)
    # _client = Client(version='1.0.0',
    #                  resource='object_storage',
    #                  provider=_provider)
    # _client.upload_object('files_container',
    #                       file['data'].name,
    #                       file['data'].content,)
    #
    pass


def get_folder_by_path(jsondata, path, result):
    """Get folder data from json data, with given path"""
    if isinstance(jsondata, dict):
        if jsondata['path'] == path.strip():
            result.append(jsondata)
        else:
            if jsondata['type'] == 'folder':
                get_folder_by_path(jsondata['children'], path, result)
    elif isinstance(jsondata, list):
        for item in jsondata:
            get_folder_by_path(item, path, result)
