import hypothesis.strategies as st
from hypothesis.extra.datetime import datetimes

SWAGGER_FORMAT_MAPPING = {
    'int64': st.integers(),
    'string': st.text(),
    'integer': st.integers(),
    'int32': st.integers(),
    'date-time': datetimes(),
    'boolean': st.booleans(),
}


def _is_swagger_parameter(dict):
    return dict.get('type') or dict.get('schema') or dict.get('$ref')


class CustomTransformation(object):

    def __init__(self, get_ref):
        self.get_ref = get_ref

    def transform(self, obj):
        """
        """
        obj = self._recursive_transform(obj)
        if isinstance(obj, (list, tuple)):
            return self._transform_array(obj)
        if isinstance(obj, dict):
            return self._transform_dict(obj)
        else:
            return self._transform_obj(obj)

    def _transform_array(self, obj):
        new_array = []
        for index, value in enumerate(obj):
            new_array.append(self.transform(value))

        return new_array

    def _transform_dict(self, obj):
        new_dict = {}
        for key, value in obj.items():
            new_dict[key] = self.transform(value)

        return new_dict

    def _transform_obj(self, obj):
        return self.default(obj)

    def _recursive_transform(self, obj):
        old_obj = None

        while old_obj is not obj:
            old_obj = obj
            obj = self.default(obj)

        return obj

    def default(self, obj):
        """
        """
        if isinstance(obj, dict) and _is_swagger_parameter(obj):
            parameter_type = obj.get('format', obj.get('type'))
            parameter_schema = obj.get('schema')
            parameter_ref = obj.get('$ref')

            if parameter_type in SWAGGER_FORMAT_MAPPING:
                return SWAGGER_FORMAT_MAPPING[parameter_type]
            elif parameter_ref:
                return self.transform(self.get_ref(parameter_ref))
            elif parameter_type == 'array':
                if obj['items'].get('enum'):
                    return st.lists(elements=st.sampled_from(obj['items']['enum']))
                elif obj['items'].get('type'):
                    return st.lists(elements=SWAGGER_FORMAT_MAPPING[obj['items']['type']])
                elif obj['items'].get('$ref'):
                    schema = self.get_ref(obj['items']['$ref'])
                    return st.lists(elements=self.transform(schema))
                raise Exception('array', obj)
            elif parameter_type == 'object':
                properties = {}
                for property_name, property_ in obj['properties'].items():
                    properties[property_name] = self.transform(property_)
                return st.fixed_dictionaries(properties)
            elif parameter_schema:
                if parameter_schema.get('type') == 'array':
                    schema = self.get_ref(parameter_schema['items']['$ref'])
                    return st.lists(elements=self.transform(schema))
                else:
                    schema = self.get_ref(parameter_schema['$ref'])
                    transformed = self.transform(schema)
                    return transformed
            else:
                raise Exception("Invalid", obj, parameter_type)

        return obj
