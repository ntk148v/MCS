fake_data = {
    "path": "/rfolder",
    "type": "folder",
    "name": "rfolder",
    "children": [
        {
            "path": "/rfolder/object1.png",
            "type": "file",
            "name": "object1.png"
        },
        {
            "path": "/rfolder/object1.jpg",
            "type": "file",
            "name": "object1.jpg"
        },
        {
            "path": "/rfolder/folder4",
            "type": "folder",
            "name": "folder4",
            "children": [
                {
                    "path": "/rfolder/folder4/object4.docx",
                    "type": "file",
                    "name": "object4.docx"
                },
                {
                    "path": "/rfolder/folder4/object4.doc",
                    "type": "file",
                    "name": "object4.doc"
                }
            ]
        },
        {
            "path": "/rfolder/folder1",
            "type": "folder",
            "name": "folder1",
            "children": [
                {
                    "path": "/rfolder/folder1/folder2",
                    "type": "folder",
                    "name": "folder2",
                    "children": [
                        {
                            "path": "/rfolder/folder1/folder2//object3.py",
                            "type": "file",
                            "name": "object3.py"
                        }
                    ]
                },
                {
                    "path": "/rfolder/folder1/object2.txt",
                    "type": "file",
                    "name": "object2.txt"
                },
                {
                    "path": "/rfolder/folder1/object2.jpg",
                    "type": "file",
                    "name": "object2.jpg"
                }
            ]
        },
        {
            "path": "/rfolder/object1.txt",
            "type": "file",
            "name": "object1.txt"
        }
    ]
}


def get_by_path(jsondata, path, result):
    if isinstance(jsondata, dict):
        if jsondata['path'] == path.strip():
            result.append(jsondata)
        else:
            if jsondata['type'] == 'folder':
                get_by_path(jsondata['children'], path, result)
    elif isinstance(jsondata, list):
        for item in jsondata:
            get_by_path(item, path, result)


result = []
get_by_path(fake_data, '/rfolder/folder4', result)
print result
