def dump_attrs(parameters, obj):
    return {
        parameter: getattr(obj, parameter)
        for parameter in parameters
    }
