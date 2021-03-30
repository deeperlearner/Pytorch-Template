# This script run train and test for examples
# bash run_examples.sh

# MNIST_LeNet
python3 train.py -c config/examples/MNIST_LeNet.json --run_id 0
python3 test.py -c config/examples/MNIST_LeNet.json --resume saved/MNIST_LeNet/0/model/model_best.pth

# MNIST_cv_LeNet
python3 train.py -c config/examples/MNIST_cv_LeNet.json --run_id 0
python3 test.py -c config/examples/MNIST_cv_LeNet.json --resume saved/MNIST_cv_LeNet/0/model/model_best.pth

# ImageNet_VGG16
#python3 train.py -c config/examples/ImageNet_VGG16.json --run_id 0
#python3 test.py -c config/examples/ImageNet_VGG16.json --resume saved/ImageNet_VGG16/0/model/model_best.pth

# Adult_logistic
#python3 train.py -c config/examples/Adult_logistic.json --run_id bce_loss
#python3 test.py -c config/examples/Adult_logistic.json --resume saved/Adult_logistic/bce_loss/model/model_best.pth --run_id bce_loss
#python3 train.py -c config/examples/Adult_logistic.json --run_id weighted_bce_loss
#python3 test.py -c config/examples/Adult_logistic.json --resume saved/Adult_logistic/weighted_bce_loss/model/model_best.pth --run_id weighted_bce_loss
python3 train.py -c config/examples/Adult_logistic.json --run_id binary_focal_loss
python3 test.py -c config/examples/Adult_logistic.json --resume saved/Adult_logistic/binary_focal_loss/model/model_best.pth --run_id binary_focal_loss

# Adult_logistic multithreading of cross validation
#python3 train.py -c config/examples/Adult_logistic.json --run_id binary_focal_loss --log_name fold_1.log --fold_idx 1
#python3 train.py -c config/examples/Adult_logistic.json --run_id binary_focal_loss --log_name fold_2.log --fold_idx 2
#python3 train.py -c config/examples/Adult_logistic.json --run_id binary_focal_loss --log_name fold_3.log --fold_idx 3
#python3 train.py -c config/examples/Adult_logistic.json --run_id binary_focal_loss --log_name fold_4.log --fold_idx 4
#python3 train.py -c config/examples/Adult_logistic.json --run_id binary_focal_loss --log_name fold_5.log --fold_idx 5
