"""
SentinelAI Deep Learning Models — CNN1D, LSTM, Autoencoder
===========================================================

Serialization contracts
-----------------------
PyTorch models (CNN1DModel, LSTMModel, AutoencoderModel):
  * save(filepath)  — writes a .pt artifact via torch.save() containing:
        {
          "model_name":    str,
          "model_type":    "DeepLearning",
          "architecture":  str,          # CNN1D | LSTM | Autoencoder
          "input_dim":     int,
          "num_classes":   int,          # 0 for Autoencoder (unsupervised)
          "hidden_dim":    int,          # LSTM only
          "state_dict":    OrderedDict,
          "torch_version": str,
          "feature_schema_version": "schema-v1.0",
        }
  * load(filepath)  — reads the .pt artifact, reconstructs the network from
        stored architecture metadata, then calls load_state_dict().

Classical/sklearn fallback (when torch is absent):
  * save/load delegate to joblib (inherited from BaseSentinelModel via self.model).

PredictService artifact filename mapping:
  "1D-CNN"      -> "cnn_1d.pt"
  "LSTM"        -> "lstm.pt"
  "Autoencoder" -> "autoencoder.pt"

Autoencoder probabilities
  predict_proba() returns None — reconstruction-error anomaly detection does
  not produce calibrated class probabilities.
"""

import numpy as np
from typing import Optional, Dict, Any
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import IsolationForest
from ml.models.base_model import BaseSentinelModel

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


# ---------------------------------------------------------------------------
# PyTorch Network Architectures
# ---------------------------------------------------------------------------

class CNN1DNet(nn.Module if HAS_TORCH else object):
    """1D Convolutional Neural Network Architecture for spatial flow feature extraction."""
    def __init__(self, input_dim: int, num_classes: int):
        if not HAS_TORCH:
            return
        super().__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(0.3)
        self.fc1 = nn.Linear(64 * (input_dim // 2), 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.relu(self.conv1(x))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.dropout(x)
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        return self.fc2(x)


class LSTMNet(nn.Module if HAS_TORCH else object):
    """Recurrent LSTM Architecture for sequence-based packet flow analysis."""
    def __init__(self, input_dim: int, num_classes: int, hidden_dim: int = 64):
        if not HAS_TORCH:
            return
        super().__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(input_size=input_dim, hidden_size=hidden_dim, num_layers=2,
                            batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        x = x.unsqueeze(1)
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out


class AutoencoderNet(nn.Module if HAS_TORCH else object):
    """Deep Autoencoder for Unsupervised Zero-Day Anomaly Detection."""
    def __init__(self, input_dim: int):
        if not HAS_TORCH:
            return
        super().__init__()
        self.input_dim = input_dim
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim)
        )

    def forward(self, x):
        encoded = self.encoder(x)
        return self.decoder(encoded)


# ---------------------------------------------------------------------------
# PyTorch serialization helpers
# ---------------------------------------------------------------------------

def _save_pytorch_artifact(net, filepath: str, architecture: str,
                           input_dim: int, num_classes: int, hidden_dim: int = 0) -> None:
    """Save a trained PyTorch network to a .pt file with full architecture metadata."""
    payload = {
        "model_name":            architecture,
        "model_type":            "DeepLearning",
        "architecture":          architecture,   # CNN1D | LSTM | Autoencoder
        "input_dim":             input_dim,
        "num_classes":           num_classes,    # 0 for Autoencoder
        "hidden_dim":            hidden_dim,     # LSTM only; ignored otherwise
        "state_dict":            net.state_dict(),
        "torch_version":         torch.__version__,
        "feature_schema_version": "schema-v1.0",
    }
    torch.save(payload, filepath)


def _load_pytorch_artifact(filepath: str):
    """
    Load a .pt artifact, reconstruct the network from stored metadata, and
    restore state_dict.  Returns (net, payload_dict).
    """
    payload = torch.load(filepath, map_location="cpu", weights_only=False)
    arch = payload["architecture"]
    input_dim = payload["input_dim"]
    num_classes = payload["num_classes"]
    hidden_dim = payload.get("hidden_dim", 64)

    if arch == "CNN1D":
        net = CNN1DNet(input_dim=input_dim, num_classes=num_classes)
    elif arch == "LSTM":
        net = LSTMNet(input_dim=input_dim, num_classes=num_classes, hidden_dim=hidden_dim)
    elif arch == "Autoencoder":
        net = AutoencoderNet(input_dim=input_dim)
    else:
        raise ValueError(f"Unknown DeepLearning architecture in artifact: '{arch}'")

    net.load_state_dict(payload["state_dict"])
    net.eval()
    return net, payload


# ---------------------------------------------------------------------------
# Model wrappers
# ---------------------------------------------------------------------------

class CNN1DModel(BaseSentinelModel):
    """
    1D-CNN classifier.  Serialized as .pt (PyTorch) when torch is available,
    otherwise falls back to sklearn MLPClassifier + joblib.
    """

    def __init__(self, epochs: int = 5, batch_size: int = 64):
        super().__init__(model_name="1D-CNN", model_type="DeepLearning")
        self.epochs = epochs
        self.batch_size = batch_size
        self._input_dim: int = 0
        self._num_classes: int = 0
        if HAS_TORCH:
            self.net = None
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if HAS_TORCH:
            self._num_classes = int(len(np.unique(y)))
            self._input_dim = int(X.shape[1])
            self.net = CNN1DNet(self._input_dim, self._num_classes).to(self.device)
            dataset = TensorDataset(torch.tensor(X, dtype=torch.float32),
                                    torch.tensor(y, dtype=torch.long))
            loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(self.net.parameters(), lr=0.001)
            self.net.train()
            for epoch in range(self.epochs):
                for batch_x, batch_y in loader:
                    batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                    optimizer.zero_grad()
                    outputs = self.net(batch_x)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
        else:
            self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if HAS_TORCH:
            probs = self.predict_proba(X)
            return np.argmax(probs, axis=1)
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if HAS_TORCH:
            self.net.eval()
            with torch.no_grad():
                x_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
                outputs = self.net(x_tensor)
                probs = torch.softmax(outputs, dim=1).cpu().numpy()
            return probs
        return self.model.predict_proba(X)

    # ------------------------------------------------------------------
    # Serialization — override base class for PyTorch path
    # ------------------------------------------------------------------

    def save(self, filepath: str) -> None:
        """
        Save CNN1DModel artifact.
        PyTorch path: writes .pt file via torch.save() with state_dict +
                      architecture metadata.
        Fallback path: joblib.dump(self.model) for sklearn MLPClassifier.
        """
        if HAS_TORCH and self.net is not None:
            _save_pytorch_artifact(
                self.net, filepath,
                architecture="CNN1D",
                input_dim=self._input_dim,
                num_classes=self._num_classes,
            )
        else:
            import joblib
            joblib.dump(self.model, filepath)

    def load(self, filepath: str) -> None:
        """
        Load CNN1DModel artifact.
        PyTorch path: reconstructs CNN1DNet from stored architecture metadata
                      and restores state_dict.
        Fallback path: joblib.load() for sklearn MLPClassifier.
        """
        if HAS_TORCH:
            self.net, payload = _load_pytorch_artifact(filepath)
            self.net = self.net.to(self.device)
            self._input_dim = payload["input_dim"]
            self._num_classes = payload["num_classes"]
        else:
            import joblib
            self.model = joblib.load(filepath)
        self.is_trained = True


class LSTMModel(BaseSentinelModel):
    """
    LSTM sequence classifier.  Serialized as .pt (PyTorch) when available,
    otherwise falls back to sklearn MLPClassifier + joblib.
    """

    def __init__(self, epochs: int = 5, batch_size: int = 64, hidden_dim: int = 64):
        super().__init__(model_name="LSTM", model_type="DeepLearning")
        self.epochs = epochs
        self.batch_size = batch_size
        self.hidden_dim = hidden_dim
        self._input_dim: int = 0
        self._num_classes: int = 0
        if HAS_TORCH:
            self.net = None
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.model = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=200, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if HAS_TORCH:
            self._num_classes = int(len(np.unique(y)))
            self._input_dim = int(X.shape[1])
            self.net = LSTMNet(self._input_dim, self._num_classes,
                               self.hidden_dim).to(self.device)
            dataset = TensorDataset(torch.tensor(X, dtype=torch.float32),
                                    torch.tensor(y, dtype=torch.long))
            loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(self.net.parameters(), lr=0.001)
            self.net.train()
            for epoch in range(self.epochs):
                for batch_x, batch_y in loader:
                    batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                    optimizer.zero_grad()
                    outputs = self.net(batch_x)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
        else:
            self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if HAS_TORCH:
            probs = self.predict_proba(X)
            return np.argmax(probs, axis=1)
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if HAS_TORCH:
            self.net.eval()
            with torch.no_grad():
                x_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
                outputs = self.net(x_tensor)
                probs = torch.softmax(outputs, dim=1).cpu().numpy()
            return probs
        return self.model.predict_proba(X)

    def save(self, filepath: str) -> None:
        if HAS_TORCH and self.net is not None:
            _save_pytorch_artifact(
                self.net, filepath,
                architecture="LSTM",
                input_dim=self._input_dim,
                num_classes=self._num_classes,
                hidden_dim=self.hidden_dim,
            )
        else:
            import joblib
            joblib.dump(self.model, filepath)

    def load(self, filepath: str) -> None:
        if HAS_TORCH:
            self.net, payload = _load_pytorch_artifact(filepath)
            self.net = self.net.to(self.device)
            self._input_dim = payload["input_dim"]
            self._num_classes = payload["num_classes"]
            self.hidden_dim = payload.get("hidden_dim", 64)
        else:
            import joblib
            self.model = joblib.load(filepath)
        self.is_trained = True


class AutoencoderModel(BaseSentinelModel):
    """
    Autoencoder-based anomaly detector.
    * predict_proba() returns None — reconstruction-error detection does NOT
      produce calibrated class probabilities.
    * Serialized as .pt (PyTorch) or IsolationForest + joblib fallback.
    """

    def __init__(self, epochs: int = 5, batch_size: int = 64, threshold: float = 0.05):
        super().__init__(model_name="Autoencoder", model_type="DeepLearning")
        self.epochs = epochs
        self.batch_size = batch_size
        # threshold=0.05 is an anomaly-detection policy constant, not a model metric
        self.threshold = threshold
        self.num_classes = 0
        self._input_dim: int = 0
        if HAS_TORCH:
            self.net = None
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.model = IsolationForest(contamination=0.1, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.num_classes = int(len(np.unique(y)))
        if HAS_TORCH:
            self._input_dim = int(X.shape[1])
            self.net = AutoencoderNet(self._input_dim).to(self.device)
            dataset = TensorDataset(torch.tensor(X, dtype=torch.float32))
            loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
            criterion = nn.MSELoss()
            optimizer = optim.Adam(self.net.parameters(), lr=0.001)
            self.net.train()
            for epoch in range(self.epochs):
                for (batch_x,) in loader:
                    batch_x = batch_x.to(self.device)
                    optimizer.zero_grad()
                    reconstructed = self.net(batch_x)
                    loss = criterion(reconstructed, batch_x)
                    loss.backward()
                    optimizer.step()
        else:
            self.model.fit(X)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if HAS_TORCH:
            self.net.eval()
            with torch.no_grad():
                x_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
                reconstructed = self.net(x_tensor)
                mse = torch.mean((reconstructed - x_tensor) ** 2, dim=1).cpu().numpy()
            return (mse > self.threshold).astype(int)
        preds = self.model.predict(X)
        return np.where(preds == -1, 1, 0)

    def predict_proba(self, X: np.ndarray) -> Optional[np.ndarray]:
        """
        Reconstruction-error anomaly detection does not produce calibrated class
        probabilities.  Returns None — never fabricated.
        """
        return None

    def save(self, filepath: str) -> None:
        if HAS_TORCH and self.net is not None:
            _save_pytorch_artifact(
                self.net, filepath,
                architecture="Autoencoder",
                input_dim=self._input_dim,
                num_classes=0,  # unsupervised — no class count
            )
        else:
            import joblib
            joblib.dump(self.model, filepath)

    def load(self, filepath: str) -> None:
        if HAS_TORCH:
            self.net, payload = _load_pytorch_artifact(filepath)
            self.net = self.net.to(self.device)
            self._input_dim = payload["input_dim"]
        else:
            import joblib
            self.model = joblib.load(filepath)
        self.is_trained = True
