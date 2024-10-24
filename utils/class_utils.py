def get_all_subclasses(cls):
    # get all subclasses of a class. used for Demand and StepHandleFunction
    subclasses = cls.__subclasses__()
    for subclass in subclasses:
        subclasses += get_all_subclasses(subclass)
    return list(set(subclasses))