import json
import os

from fairness.utils import load_yaml


class Config:
    def __init__(self, working_dir=None):
        self.set_working_dir(working_dir)

        self.input_config = None
        self.dataset_config = None
        self.metric_config = None
        self.mitigation_config = None

    def set_working_dir(self, working_dir):
        if working_dir:
            self.working_dir = working_dir
        else:
            self.working_dir = os.path.join(
                os.path.dirname(os.path.abspath(os.path.dirname(__file__))), 'working_dir'
            )
        if not os.path.exists(self.working_dir):
            raise f"'working_dir' is not Exists.: {self.working_dir}"

    def set_input_config(self, file_path='./config/input.yaml'):
        self.input_config = load_yaml(file_path)

    def set_dataset_config(self, file_path='./config/dataset.yaml'):
        dataset_config = load_yaml(file_path)

        def _privileged_classes(privileged_classes):
            if isinstance(privileged_classes, str):
                if privileged_classes.startswith('eval:'):
                    return eval(f'lambda x: {privileged_classes.split(":")[-1]}')
            if not isinstance(privileged_classes, list):
                return [privileged_classes]
            else:
                return privileged_classes

        def _convert_to_list(to_list_config):
            if isinstance(to_list_config, list):
                return to_list_config
            elif not to_list_config:
                return []
            else:
                return [to_list_config]

        def _custom_preprocessing():
            exec(dataset_config['custom_preprocessing'], globals())
            if 'custom_preprocessing' in globals():
                return globals()['custom_preprocessing']
            else:
                return None

        self.dataset_config = {
            'label_name': dataset_config['label']['name'],
            'favorable_classes': dataset_config['label']['favorable_classes'],
            'protected_attribute_names': [attr['name'] for attr in dataset_config['protected_attributes']],
            'privileged_classes': [_privileged_classes(attr['privileged_classes']) for attr in dataset_config['protected_attributes']],
            'categorical_features': _convert_to_list(dataset_config['categorical_features']),
            'features_to_keep': _convert_to_list(dataset_config['features_to_keep']),
            'features_to_drop': _convert_to_list(dataset_config['features_to_drop']),
            'custom_preprocessing': _custom_preprocessing()
        }

    def set_metric_config(self, file_path='./config/metric.yaml'):
        self.metric_config = load_yaml(file_path)

    def set_mitigation_config(self, file_path='./config/mitigation.yaml'):
        self.mitigation_config = load_yaml(file_path)

        if not self.metric_config:
            raise '"metric_config" must be defined first.'
        self.mitigation_config['unprivileged_groups'] = self.metric_config['unprivileged_groups']
        self.mitigation_config['privileged_groups'] = self.metric_config['privileged_groups']
