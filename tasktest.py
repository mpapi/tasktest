'''
A test harness for executable specification tests.
'''

import sys
import unittest
import inspect
import simplejson

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from jinja2 import Environment, FileSystemLoader

class task(object):
    '''
    A decorator for functions that provide an acceptance test for a single
    task/specification item/user story.
    '''

    status = 'pending'
    skip = True

    def __init__(self, **kwargs):
        self.options = kwargs
        self.orig_func = None
        self.name = None

    def __call__(self, func):
        '''
        Set a task attribute on the function that this decorator wraps to this
        object, so we can read data back given only the function later on.
        '''
        setattr(func, 'task', self)
        self.orig_func = func
        self.name = func.__name__
        return func

def build_statuses(*statuses):
    '''
    Programmatically create a other decorator subclasses as shortcuts for other
    statuses.
    '''
    for stat in statuses:
        globals()[stat] = type(stat, (task,), dict(status=stat, skip=False))
build_statuses('started', 'finished')

def load_tasks(module_name, suite):
    '''
    Loads test functions from a module into a unittest TestSuite.
    '''
    module = __import__(module_name) # TODO: from_list
    for _, item in inspect.getmembers(module):
        if hasattr(item, 'task'):
            if item.task.skip:
                test_fn = unittest.skip(item.task.status)(item)
            else:
                test_fn = item
            test_case = unittest.FunctionTestCase(test_fn)
            suite.addTest(test_case)

class TaskReport(object):
    '''
    An aggregator of tasks, test results, and test run statistics for display
    to the user.
    '''

    def __init__(self, test_result, suite):
        self.test_result = test_result
        self.suite = suite
        self.formatter = HtmlFormatter()
        self.lexer = PythonLexer()
        self.tests = []
        self.counts = {}
        self.__build()

    @staticmethod
    def result_item((test, result)):
        '''
        Retrieves the task for a test and returns a mapping from the task name
        to the task and result.
        '''
        _task = test._testFunc.task
        return (_task.name, (_task, result))

    def result_map(self, results):
        '''
        Builds a mapping of tasks names to tasks and results from the test
        results.
        '''
        return dict(self.result_item(item) for item in results)

    @staticmethod
    def generate_counts(tests):
        '''
        Builds a mapping of test result statuses to their counts (and the
        total).
        '''
        counts = {}
        counts['failed'] = len([test for test in tests if test.is_failed])
        counts['skipped'] = len([test for test in tests if test.is_skipped])
        counts['passed'] = len([test for test in tests if test.is_passed])
        counts['total'] = sum([count for _, count in counts.items()])
        return counts

    def __build(self):
        '''
        Builds a list of TaskResults and counts for rendering.
        '''
        highlighter = lambda text: highlight(text, self.lexer, self.formatter)

        failures = self.result_map(self.test_result.failures)
        errors = self.result_map(self.test_result.errors)
        skipped = self.result_map(self.test_result.skipped)

        results = []
        for case in self.suite._tests:
            _task = case._testFunc.task
            if _task.name in failures or _task.name in errors:
                status = 'failed'
                if _task.name in failures:
                    _, traceback = failures.get(_task.name)
                else:
                    _, traceback = errors.get(_task.name)
            elif _task.name in skipped:
                status = 'skipped'
                traceback = None
            else:
                status = 'passed'
                traceback = None
            results.append(TaskResult(_task, status, traceback, highlighter))
        self.tests = results
        self.counts = self.generate_counts(results)

    @property
    def style(self):
        '''
        Return the CSS for syntax highlighting.
        '''
        return self.formatter.get_style_defs()

    @property
    def sorted_tests(self):
        '''
        Return tests sorted by their status first and run order second.
        '''
        sort = sorted(enumerate(self.tests), key=lambda (i, t): (t.status, i))
        return (test for _, test in sort)


    @property
    def counts_json(self):
        '''
        Return a JSON string of status counts.
        '''
        return simplejson.dumps(self.counts)

class TaskResult(object):
    '''
    Stores data about a task and the result of running its associated test.
    '''

    def __init__(self, _task, status, traceback, highlighter):
        self.task = _task
        self.status = status
        self.traceback = traceback
        self.highlighter = highlighter

    @property
    def is_failed(self):
        '''
        True if the test failed or had an error.
        '''
        return self.status == 'failed'

    @property
    def is_skipped(self):
        '''
        True if the test was skipped because the task wasn't started.
        '''
        return self.status == 'skipped'

    @property
    def is_passed(self):
        '''
        True if the test passed.
        '''
        return self.status == 'passed'

    @property
    def doc(self):
        '''
        The docstring associated with the task.
        '''
        return inspect.getdoc(self.task.orig_func)

    @property
    def source(self):
        '''
        The (raw) Python source for the task definition.
        '''
        return inspect.getsource(self.task.orig_func)

    @property
    def decorated_source(self):
        '''
        The highlighted Python source for the task definition.
        '''
        return self.highlighter(self.source)

    @property
    def source_file(self):
        '''
        The name of the source file where the task was defined.
        '''
        return inspect.getsourcefile(self.task.orig_func)

def generate(output_file, task_report):
    '''
    Generates an HTML file in output_file from a TaskReport.
    '''
    template_env = Environment(loader=FileSystemLoader('templates'))
    template = template_env.get_template('overview.html')
    with open(output_file, 'w') as handle:
        handle.write(template.render(report=task_report))

def main():
    '''
    Runs the harness on each module given as a command-line argument and
    generates an HTML report.
    '''
    suite = unittest.TestSuite()
    for arg in sys.argv[1:]:
        load_tasks(arg, suite)
    test_result = unittest.TextTestRunner(verbosity=2).run(suite)
    task_report = TaskReport(test_result, suite)
    generate('overview.html', task_report)

if __name__ == '__main__':
    main()
