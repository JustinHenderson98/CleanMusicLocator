"""
Definitions of all exception classes raised by the code in this package.

Exception class :class:`FFprobeError` is the abstract base class of
all exception classes in this package.
It contains no attributes and should never be instantiated directly.
It's simply intended as a useful catch-all for lazy exception handling.

Every derived class overloads magic method ``__str__`` to return a useful
descriptive error message string that includes the attributes specific to
that derived class.
"""

# Base class of exception classes used by this `ffprobe3` package.
class FFprobeError(Exception):
    """The abstract base class of all exception classes in this package.

    It contains no attributes and should never be instantiated directly.
    It's simply intended as a useful catch-all for lazy exception handling.

    Every derived class overloads magic method ``__str__`` to return a useful
    descriptive error message string that includes the attributes specific to
    that derived class.
    """
    pass


class FFprobeInvalidArgumentError(FFprobeError):
    """A caller-supplied function argument received an invalid value.

    Args:
        arg_name (str): name of the argument that received an invalid value
        problem (str): description of the problem
        value: the invalid value
    """
    def __init__(self, arg_name, problem, value):
        self.arg_name = arg_name
        self.problem = problem
        self.value = value

    def __str__(self):
        return "Argument '%s' received invalid value '%s': %s" % \
                (self.arg_name, self.value, self.problem)


class FFprobeOverrideFileError(FFprobeError):
    """The caller-specified ffprobe command override file does not exist.

    Note that if you specify an ffprobe command override file, you must
    specify the full file-path to the command (either absolute or relative
    to the current directory) to an executable file to call.

    Args:
        file_path (str): the caller specified file-path that does not exist
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return "Command override file-path does not exist: %s" % \
                self.file_path


class FFprobeExecutableError(FFprobeError):
    """This ffprobe command executable was not found by ``subprocess.Popen``,
    ``subprocess.call``, or ``subprocess.check_call``.

    This means that this ffprobe command executable was not found in `$PATH`.
    This might mean that the ffprobe command is not installed on your system.

    Args:
        cmd (str): the ffprobe command executable filename that was not found
    """
    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        return "Command executable was not found in path: %s" % \
                self.cmd


class FFprobeMediaFileError(FFprobeError):
    """The caller-specified media file does not exist locally.

    Args:
        file_path (str): the caller-specified file-path that does not exist
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return "Media file does not exist locally: %s" % \
                self.file_path


class FFprobePopenError(FFprobeError):
    """This wraps an exception that was raised by function ``subprocess.Popen``.

    Args:
        exc (caught exception): the exception instance that was raised
        caught_type_name (str): the type-name of the exception that was raised
    """
    def __init__(self, exc, caught_type_name):
        self.exc = exc
        self.caught_type_name = caught_type_name

    def __str__(self):
        return "Function 'subprocess.Popen' raised exception %s (caught as %s): %s" % \
                (_get_full_qualname(self.exc), self.caught_type_name, str(self.exc))


class FFprobeJsonParseError(FFprobeError):
    """This wraps an exception that was raised by function ``json.loads``.

    Args:
        exc (caught exception): the exception instance that was raised
        caught_type_name (str): the type-name of the exception that was raised
    """
    def __init__(self, exc, caught_type_name):
        self.exc = exc
        self.caught_type_name = caught_type_name

    def __str__(self):
        return "Function 'json.loads' raised exception %s (caught as %s): %s" % \
                (_get_full_qualname(self.exc), self.caught_type_name, str(self.exc))


class FFprobeSubprocessError(FFprobeError):
    """The ffprobe subprocess returned a non-zero exit status.

    Args:
        split_cmdline (list of strings): the command-line that was executed
        exit_status (int): the non-zero exit status
        stderr (file, optional): the message printed to stderr
    """
    def __init__(self, split_cmdline, exit_status, stderr=None):
        self.split_cmdline = split_cmdline
        self.exit_status = exit_status
        self.stderr = stderr

    def __str__(self):
        return "Subprocess %s returned non-zero exit status %s: %s" % \
                (self.split_cmdline, self.exit_status, self.stderr)


class FFprobeStreamSubclassError(FFprobeError):
    """The wrong stream subclass has been constructed for a codec type.

    Args:
        class_name (str): the type-name of the class that was constructed
        received_codec_type (str): the name of the codec-type received
        required_codec_type (str): the codec-type for the class constructed
    """
    def __init__(self, class_name, received_codec_type, required_codec_type):
        self.class_name = class_name
        self.received_codec_type = received_codec_type
        self.required_codec_type = required_codec_type

    def __str__(self):
        return "%s is wrong stream subclass for received codec type '%s' (required codec type is '%s')" % \
                (self.class_name, self.received_codec_type, self.required_codec_type)


def _get_full_qualname(obj):
    """Get the fully-qualified name of the type of object `obj`.

    PEP 3155 ("Qualified name for classes and functions") [1] describes
    a "qualified name" as:

        For top-level functions and classes, the `__qualname__` attribute
        is equal to the `__name__` attribute.  For nested classes, methods,
        and nested functions, the `__qualname__` attribute contains a
        dotted path leading to the object from the module top-level.

    and:

        As __name__, __qualname__ doesn’t include the module name.

    Thus, a "qualified name" differs from a "fully-qualified name":

        It is not a "full name" or "fully qualified name" since it
        (deliberately) does not include the module name. Calling it
        a "path" would risk confusion with filesystem paths and the
        `__file__` attribute.

    [1] PEP 3155: https://peps.python.org/pep-3155/

    This function attempts to construct fully-qualified names,
    based upon code in these three helpful StackOverflow answers:

     - https://stackoverflow.com/a/2020083
     - https://stackoverflow.com/a/13653312
     - https://stackoverflow.com/a/58045927

    Note: This function will exclude the module name if builtin or `None`,
    to avoid results like `__builtin__.str`.

    Examples of fully-qualified names returned by this function:
    - `json.decoder.JSONDecodeError`
    - `subprocess.SubprocessError`
    - `ValueError`
    - `str`
    """
    module = obj.__class__.__module__
    # Note: `__module__` can be `None` (according to the docs),
    # and also for a type like `str` it can be `__builtin__`
    #  -- https://stackoverflow.com/a/13653312
    if module is None or module == str.__class__.__module__:
        # Exclude the module name if builtin or `None`,
        # to avoid results like `__builtin__.str`.
        return obj.__class__.__qualname__
    return "%s.%s" % (module, obj.__class__.__qualname__)