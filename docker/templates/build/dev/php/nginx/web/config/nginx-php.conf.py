from project.generation.parsing import parse_vars

template = """
upstream php-upstream {
    server %(siblings.php.fullname):9000;
}
"""


def generate(mapping: dict) -> str:
    return parse_vars(template, mapping)
