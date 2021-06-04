import re

from dmoj.contrib.default import ContribModule as DefaultContribModule
from dmoj.error import InternalError
from dmoj.result import CheckerResult


class ContribModule(DefaultContribModule):
    name = 'cms'
    repartial = re.compile(r'^([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)', re.M)
    standard_outputs = {
        'translate:success': 'Output is correct',
        'translate:wrong': 'Output isn\'t correct',
        'translate:partial': 'Output is partially correct',
    }

    @classmethod
    def get_checker_args_format_string(cls):
        return '{input_file} {answer_file} {output_file}'

    @classmethod
    def parse_return_code(cls, proc, executor, point_value, time_limit, memory_limit, feedback, extended_feedback, name, stderr):
        # Translate output of the checker in the extended_feedback to feedback
        translate_feedback = None
        for std_output, translate in cls.standard_outputs.items():
            if extended_feedback.find(std_output) != -1:
                translate_feedback = translate
                extended_feedback = extended_feedback.replace(std_output, '')
        
        # Now if the extended_feedback has nothing left then we set it to None 
        # so that the client will not display it
        if len(extended_feedback.strip()) == 0:
            extended_feedback = None

        if proc.returncode == cls.AC:
            match = cls.repartial.search(feedback)
            if not match:
                raise InternalError('Invalid stderr for partial points: %r' % feedback)
            percentage = float(match.group(1))
            if not 0.0 <= percentage <= 1.0:
                raise InternalError('Invalid partial points: %f, must be between [0; 1]' % percentage)
            points = percentage * point_value
            return CheckerResult(percentage != 0, points, feedback=translate_feedback, extended_feedback=extended_feedback)
        else:
            return CheckerResult(False, 0, feedback="Checker exitcode %d" % proc.returncode, extended_feedback=extended_feedback)
