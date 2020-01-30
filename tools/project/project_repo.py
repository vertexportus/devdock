from utils import env


class ProjectRepo:
    base_urls = {
        'github': {'ssh': 'git@github.com:', 'http': 'https://github.com/'}
    }
    url: str

    def __init__(self, project, data):
        if 'github' in data:
            self._set_url('github', data['github'])
        elif 'repo' in data:
            self._set_url('repo', data['repo'])
        else:
            raise Exception(f"No repository configured on project '{project.name if project else 'devdock'}'")

    def _set_url(self, url_type, url):
        self.url = f"{self.base_urls[url_type]['ssh' if env.git_use_ssh() else 'http']}{url}" \
            if url_type in self.base_urls else url
