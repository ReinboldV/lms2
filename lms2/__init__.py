"""data, model and results processing"""

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

__all__ = ['lms2.core.models',
           'lms2.economic.cost',
           'lms2.environment.ghg',
           'lms2.logical.sequencial',
           'lms2.mechanic.gears',
           'lms2.thermal.dipoles']

from lms2.base.block import *
from lms2.core.models import *
from lms2.economic.cost import *
from lms2.electric.sources import *
from lms2.electric.batteries import *
from lms2.environment.ghg import *
from lms2.mechanic.gears import *
from lms2.logical.sequencial import *
from lms2.thermal.dipoles import *
