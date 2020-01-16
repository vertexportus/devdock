import argparse
import git
from git import Repo
from utils import env, GitProgress, ProjectConfigManager
from utils.colors import *
from commands import base_command


class Git(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('git', help="runs a git command for a specific project")
        parser_main.add_argument('git_command', help="git command to run")
        parser_main.add_argument('project',
                                 help="project to run git command in ('all' for all projects, 'base' for base "
                                      "project, 'all+base' for all projects + base project)")
        parser_main.add_argument('params', nargs=argparse.REMAINDER,
                                 help='additional arguments passed directly into git command')

    def process_command(self):
        method_name = f"_{self._args.git_command}_handler"
        if hasattr(self, method_name):
            getattr(self, method_name)()
        else:
            self._default_handler()

    def _clone_handler(self):
        projects = ProjectConfigManager().get_projects()
        if 'all' in self._args.project:
            for project, project_config in projects.items():
                self.__git_clone(project, project_config['repo'])
        else:
            project = self._args.project
            if project in projects.keys():
                self.__git_clone(project, projects[project]['repo'])
            else:
                raise Exception(f"no configuration set for project '{self._args.project}'")

    def _default_handler(self):
        raise Exception(f"command '{self._args.git_command}' not supported")

    @staticmethod
    def __git_clone(project, repo_url):
        print(blue(f"cloning repository for {project}"))
        try:
            Repo.clone_from(repo_url, project, progress=GitProgress())
        except git.exc.GitCommandError as git_error:
            print(red(f"Error cloning '{project}'\n"))
            raise git_error
