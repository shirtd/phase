from phase.data import parse_file, get_bounds
from phase.util import format_float, pmap

from tqdm import tqdm
import numpy as np
import sys, os, time


class Data:
    module, args = None, []
    def __init__(self, data, bounds, *args, **kwargs):
        self.data, self.bounds = data, bounds
        self.prefix = self.get_prefix(*args, **kwargs)
        self.name = self.get_name(*args, **kwargs)
        self.title = self.get_title(*args, **kwargs)
    def __iter__(self):
        yield from self.data
    def __repr__(self):
        return self.title
    def __getitem__(self, i):
        return self.data[i]
    def __len__(self):
        return len(self.data)

# class InputDataBase:
#     args = ['directory', 'dataset', 'file']
#     @classmethod
#     def get_prefix(cls, directory, dataset, file, *args, **kwargs):
#         return os.path.splitext(file)[0]
#     @classmethod
#     def get_name(cls, directory, dataset, file, *args, **kwargs):
#         prefix = cls.get_prefix(directory, dataset, file)
#         return '%s-%s' % (dataset, prefix)
#     @classmethod
#     def get_title(cls, directory, dataset, file, *args, **kwargs):
#         prefix = cls.get_prefix(directory, dataset, file, frames)
#         return '%s, %s' % (dataset, prefix)

class MetricData(Data):
    def __init__(self, data, bounds, *args, **kwargs):
        self.shape, self.dim = data.shape, data.shape[-1]
        Data.__init__(self, data, bounds, *args, **kwargs)

# class InputData(MetricData, InputDataBase):
#     module = 'input'
#     @classmethod
#     def get_name(cls, directory, dataset, file, frames):
#         name = InputDataBase.get_name(cls, directory, dataset, file)
#         if frames is not None:
#             return '%s_%d-%d' % (name, frames[0], frames[1])
#         return name
#     @classmethod
#     def get_title(cls, directory, dataset, file, frames):
#         prefix = cls.get_prefix(directory, dataset, file, frames)
#         title = InputDataBase.get_title(cls, directory, dataset, file)
#         if frames is not None:
#             return '%s frames %d-%d' % (title, frames[0], frames[1])
#         return title
#     def __init__(self, directory, dataset, file, frames):
#         self.directory, self.dataset, self.file = directory, dataset, file
#         self.path = os.path.join(directory, dataset, file)
#         print('[ Loading %s' % self.path)
#         input_data = parse_file(self.path, frames)
#         frames = frames if frames is not None else (0, len(input_data))
#         data = np.stack([np.array(d['points']) for d in input_data])
#         bounds = get_bounds(input_data, dataset)
#         MetricData.__init__(self, data, bounds, directory, dataset, file, frames)

class InputData(MetricData):
    module = 'input'
    args = ['directory', 'dataset', 'file', 'frames']
    @classmethod
    def get_prefix(cls, directory, dataset, file, frames):
        return os.path.splitext(file)[0]
    @classmethod
    def get_name(cls, directory, dataset, file, frames):
        prefix = cls.get_prefix(directory, dataset, file, frames)
        name = '%s-%s' % (dataset, prefix)
        if frames is not None:
            return '%s_%d-%d' % (name, frames[0], frames[1])
        return name
    @classmethod
    def get_title(cls, directory, dataset, file, frames):
        prefix = cls.get_prefix(directory, dataset, file, frames)
        title = '%s, %s' % (dataset, prefix)
        if frames is not None:
            return '%s frames %d-%d' % (title, frames[0], frames[1])
        return title
    def __init__(self, directory, dataset, file, frames):
        self.directory, self.dataset, self.file = directory, dataset, file
        self.path = os.path.join(directory, dataset, file)
        print('[ Loading %s' % self.path)
        input_data = parse_file(self.path, frames)
        frames = frames if frames is not None else (0, len(input_data))
        data = np.stack([np.array(d['points']) for d in input_data])
        bounds = get_bounds(input_data, dataset)
        MetricData.__init__(self, data, bounds, directory, dataset, file, frames)

class DataTransformation(Data):
    args = ['parallel', 'verbose']
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        pass
    @classmethod
    def get_name(cls, input_data, *args, **kwargs):
        return cls.make_name(input_data.name, *args, **kwargs)
    @classmethod
    def get_title(cls, input_data, *args, **kwargs):
        return cls.make_title(input_data.title, *args, **kwargs)
    def __init__(self, input_data, parallel, verbose, *args, **kwargs):
        self.limits = input_data.bounds.min(0)
        data = self.run(input_data, parallel, verbose, *args, **kwargs)
        Data.__init__(self, data, input_data.bounds, input_data, *args, **kwargs)
    def run(self, input_data, parallel, verbose, *args, **kwargs):
        sstr = '[ %s %s' % (self.get_prefix(input_data, *args, **kwargs), self.module)
        if not verbose:
            input_data = tqdm(input_data, total=len(input_data), desc=sstr)
        if parallel:
            return pmap(self, input_data, verbose=verbose)
        return [self(d, verbose) for d in input_data]

# class CachedDataTransformation(DataTransformation):
#     args = ['frames', 'cache'] + DataTransformation.args
#     def __init__(self, input_data, frames, cache, parallel, verbose, *args, **kwargs):
#         DataTransformation.__init__(self, input_data, parallel, verbose, frames, cache, *args, **kwargs)
#     def run(self, input_data, parallel, verbose, frames, cache, *args, **kwargs):
#
#         pass
