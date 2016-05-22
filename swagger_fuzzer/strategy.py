""" Hypothesis custom strategy
"""
from hypothesis.searchstrategy import SearchStrategy
from hypothesis.control import _current_build_context
from hypothesis.errors import InvalidArgument
from hypothesis.control import note


def data():
    """This isn't really a normal strategy, but instead gives you an object
    which can be used to draw data interactively from other strategies.

    It can only be used within @given, not find. This is because the lifetime
    of the object cannot outlast the test body.

    See the rest of the documentation for more complete information.

    """
    class DataObject(object):

        def __init__(self, data):
            self.count = 0
            self.data = data
            context = _current_build_context.value
            context.request = {}

        def __repr__(self):
            return 'request(...)'

        def draw(self, strategy, name=None):
            result = self.data.draw(strategy)
            return result

    class DataStrategy(SearchStrategy):
        supports_find = False

        def do_draw(self, data):
            if not hasattr(data, 'hypothesis_shared_data_strategy'):
                data.hypothesis_shared_data_strategy = DataObject(data)
            return data.hypothesis_shared_data_strategy

        def __repr__(self):
            return 'data()'

        def map(self, f):
            self.__not_a_first_class_strategy('map')

        def filter(self, f):
            self.__not_a_first_class_strategy('filter')

        def flatmap(self, f):
            self.__not_a_first_class_strategy('flatmap')

        def example(self):
            self.__not_a_first_class_strategy('example')

        def __not_a_first_class_strategy(self, name):
            raise InvalidArgument((
                'Cannot call %s on a DataStrategy. You should probably be '
                "using @composite for whatever it is you're trying to do."
            ) % (name,))
    return DataStrategy()
