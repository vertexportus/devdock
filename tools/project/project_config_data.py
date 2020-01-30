import functools

from project.project_repo import ProjectRepo


class ProjectConfigData:
    docker: dict
    projects: dict
    services: dict
    devdock: ProjectRepo

    def __str__(self):
        projects = functools.reduce(lambda a, b: f"{a}\n{b}", [f" -- {k}: {v}" for k, v in self.projects.items()])
        services = functools.reduce(lambda a, b: f"{a}\n{b}", [f" -- {k}: {v}" for k, v in self.services.items()])
        return (f"projects: {len(self.projects)}\n{projects}"
                f"\n\nservices: {len(self.services)}\n{services}")

    def get_service_by_path(self, database):
        raise Exception("not implemented")
