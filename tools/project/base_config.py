class BaseConfig:
    name: str
    _class_type: str
    _original_data: dict

    def __init__(self, name, original_data):
        self.name = name
        self._class_type = type(self).__name__
        self._original_data = original_data

    def validate_get_field(self, field):
        if field not in self._original_data:
            raise Exception(f"validation error: {field} is required in {self._class_type} config {self.name}")
        return self._original_data[field]

    def try_get(self, field, default):
        return self._original_data[field] if field in self._original_data else default
