import os
import sys
import argparse
import collections
import time

import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

sys.path.insert(1, os.path.join(sys.path[0], '../..'))
from logger import get_logger
from mains import Cross_Valid
import models.loss as module_loss
import models.metric as module_metric
from models.metric import MetricTracker
from parse_config import ConfigParser
from utils import ensure_dir, prepare_device, get_by_path, msg_box, consuming_time
from utils.bootstrap import bootstrapping

# fix random seeds for reproducibility
SEED = 123
torch.manual_seed(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
np.random.seed(SEED)


def main():
    # setup GPU device if available, move model into configured device
    device, device_ids = prepare_device(config['n_gpu'])

    # datasets
    test_datasets = dict()
    keys = ['datasets', 'test']
    for name in get_by_path(config, keys):
        test_datasets[name] = config.init_obj([*keys, name], 'data_loaders')

    results = pd.DataFrame()
    Cross_Valid.create_CV(k_fold)
    start = time.time()
    for k in range(k_fold):
        # data_loaders
        test_data_loaders = dict()
        keys = ['data_loaders', 'test']
        for name in get_by_path(config, keys):
            dataset = test_datasets[name]
            loaders = config.init_obj([*keys, name], 'data_loaders', dataset)
            test_data_loaders[name] = loaders.test_loader

        # models
        if k_fold > 1:
            fold_prefix = f'fold_{k}_'
            dirname = os.path.dirname(config.resume)
            basename = os.path.basename(config.resume)
            resume = os.path.join(dirname, fold_prefix + basename)
        else:
            resume = config.resume
        logger.info(f"Loading model: {resume} ...")
        checkpoint = torch.load(resume)
        models = dict()
        logger_model = get_logger('model', verbosity=0)
        for name in config['models']:
            model = config.init_obj(['models', name], 'models')
            logger_model.info(model)
            state_dict = checkpoint['models'][name]
            if config['n_gpu'] > 1:
                model = torch.nn.DataParallel(model)
            model.load_state_dict(state_dict)
            model = model.to(device)
            model.eval()
            models[name] = model
        model = models['model']

        # losses
        loss_fn = config.init_obj(['losses', 'loss'], module_loss)

        # metrics
        metrics_epoch = [getattr(module_metric, met) for met in config['metrics']['per_epoch']]
        keys_epoch = [m.__name__ for m in metrics_epoch]
        test_metrics = MetricTracker([], keys_epoch)
        if 'pick_threshold' in config['metrics']:
            threshold = checkpoint['threshold']
            setattr(module_metric, 'THRESHOLD', threshold)
            logger.info(f"threshold: {threshold}")

        with torch.no_grad():
            print("testing...")
            test_loader = test_data_loaders['data']

            if len(metrics_epoch) > 0:
                outputs = torch.FloatTensor().to(device)
                targets = torch.FloatTensor().to(device)
            for batch_idx, (data, target) in enumerate(test_loader):
                data, target = data.to(device), target.to(device)

                output = model(data)
                if len(metrics_epoch) > 0:
                    outputs = torch.cat((outputs, output))
                    targets = torch.cat((targets, target))

                #
                # save sample images, or do something with output here
                #

            for met in metrics_epoch:
                test_metrics.epoch_update(met.__name__, met(targets, outputs))

        test_log = test_metrics.result()
        test_log = test_log['mean'].rename(k)
        results = pd.concat((results, test_log), axis=1)
        logger.info(test_log)

        # cross validation
        if k_fold > 1:
            Cross_Valid.next_fold()

    msg = msg_box("result")

    end = time.time()
    total_time = consuming_time(start, end)
    msg += f"\nConsuming time: {total_time}."

    result = pd.DataFrame()
    result['mean'] = results.mean(axis=1)
    result['std'] = results.std(axis=1)
    msg += f"\n{result}"

    logger.info(msg)

    # bootstrap
    if config.test_args.bootstrapping:
        assert k_fold == 1, "k-fold ensemble and bootstrap are mutually exclusive."
        N = config.test_args.bootstrap_times
        bootstrapping(targets, outputs, metrics_epoch, test_metrics, repeat=N)


if __name__ == '__main__':
    args = argparse.ArgumentParser(description='testing')
    run_args = args.add_argument_group('run_args')
    run_args.add_argument('-c', '--config', default="configs/examples/mnist.json", type=str)
    run_args.add_argument('--resume', default=None, type=str)
    run_args.add_argument('--mode', default='test', type=str)
    run_args.add_argument('--run_id', default=None, type=str)
    run_args.add_argument('--log_name', default=None, type=str)

    # custom cli options to modify configuration from default values given in json file.
    mod_args = args.add_argument_group('mod_args')
    CustomArgs = collections.namedtuple('CustomArgs', "flags type target")
    options = [
        CustomArgs(['--name'], type=str, target="name"),
    ]
    for opt in options:
        mod_args.add_argument(*opt.flags, type=opt.type)

    # config.test_args: additional arguments for testing
    test_args = args.add_argument_group('test_args')
    test_args.add_argument('--bootstrapping', action='store_true')
    test_args.add_argument('--bootstrap_times', default=1000, type=int)
    test_args.add_argument('--output_path', default=None, type=str)

    config = ConfigParser.from_args(args, options)
    logger = get_logger('test')
    msg = msg_box("TEST")
    logger.debug(msg)
    k_fold = config['k_fold']

    main()
