import torch
import torch.nn as nn
from torch.utils.data import Dataset

from torchmetrics import Metric
from torchmetrics.classification import BinaryAccuracy, BinaryPrecision, BinaryRecall

from pyroml.model import PyroModel, Step
from pyroml.utils import Stage

from regression import DummyRegressionDataset


class DummyClassificationDataset(Dataset):
    def __init__(self, size=1024):
        self.ds = DummyRegressionDataset(size, 1)

    def __len__(self):
        return len(self.ds)

    def __getitem__(self, idx):
        x, y = self.ds[idx]
        y = torch.where(y > 0, 1, 0)
        return x, y


class DummyClassificationModel(PyroModel):
    def __init__(self, mid_dim=16):
        super().__init__()
        self.seq = nn.Sequential(
            nn.Linear(1, mid_dim),
            nn.LeakyReLU(),
            nn.Linear(mid_dim, 1),
            nn.Sigmoid(),
        )

    def configure_metrics(self) -> dict[Metric]:
        return {
            "acc": BinaryAccuracy(),
            "pre": BinaryPrecision(),
            "rec": BinaryRecall(),
        }

    def forward(self, x):
        return self.seq(x)

    def step(self, batch, stage: Stage):
        x, y = batch
        pred = self(x)
        return {Step.PRED: pred, Step.METRIC_PRED: torch.round(pred), Step.TARGET: y}
