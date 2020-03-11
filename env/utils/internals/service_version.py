def get_tech_version_from_service(tech, service, defaults):
    if 'version' in service:
        version_attr = service['version']
        if type(version_attr) == str:
            version = version_attr
        elif tech in version_attr:
            version = version_attr[tech]
        else:
            version = '-'
    else:
        version = defaults[tech]['version']
    return str(version)
