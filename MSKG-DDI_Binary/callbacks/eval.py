from collections import defaultdict

import numpy as np
from keras.callbacks import Callback
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, average_precision_score,precision_recall_curve, precision_score, recall_score, auc
import sklearn.metrics as m
from utils import write_log
from sklearn.preprocessing import label_binarize

class Metric(Callback):
    def __init__(self, x_train, y_train, x_valid, y_valid,aggregator_type,dataset,K_fold, batch_size):
        self.x_train = x_train
        self.y_train = y_train
        self.x_valid = x_valid
        self.y_valid = y_valid
        self.aggregator_type=aggregator_type
        self.dataset=dataset
        self.k=K_fold
        self.threshold=0.5
        self.batch_size = batch_size
        super(Metric, self).__init__()

    def on_epoch_end(self, epoch, logs=None):
        y_pred = self.model.predict(self.x_valid, batch_size=self.batch_size)
        y_true = self.y_valid

        y_pred = y_pred.flatten()
        y_true = y_true.flatten()
        auc = roc_auc_score(y_true=y_true, y_score=y_pred)
        precision, recall, _thresholds = precision_recall_curve(y_true=y_true, probas_pred=y_pred)
        aupr=m.auc(recall,precision)
        y_pred = [1 if prob >= self.threshold else 0 for prob in y_pred]
        acc = accuracy_score(y_true=y_true, y_pred=y_pred)
        f1 = f1_score(y_true=y_true, y_pred=y_pred)
        recall_s = recall_score(y_true=y_true, y_pred=y_pred)
        precision_s = precision_score(y_true=y_true, y_pred=y_pred)

        logs['val_aupr'] = float(aupr)
        logs['val_auc'] = float(auc)
        logs['val_acc'] = float(acc)
        logs['val_f1'] = float(f1)
        logs['val_rec'] = float(recall_s)
        logs['val_pre'] = float(precision_s)
        
        logs['dataset']=self.dataset
        logs['aggregator_type']=self.aggregator_type
        logs['kfold']=self.k
        logs['epoch_count']=epoch+1
        print(f'Logging Info - epoch: {epoch+1}, val_auc: {auc}, val_aupr: {aupr}, val_acc: {acc}, val_f1: {f1}')
        write_log('log/train_history.txt',logs,mode='a')

    @staticmethod
    def get_user_record(data, is_train):
        user_history_dict = defaultdict(set)
        for interaction in data:
            user = interaction[0]
            item = interaction[1]
            label = interaction[2]
            if is_train or label == 1:
                user_history_dict[user].add(item)
        return user_history_dict

