import numpy as np
from typing import Optional, Dict, Any, List
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


class CNN1DNet(nn.Module if HAS_TORCH else object):
    """1D Convolutional Neural Network Architecture for spatial flow feature extraction."""
    def __init__(self, input_dim: int, num_classes: int):
        if not HAS_TORCH:
            return
        super().__init__()
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
        self.lstm = nn.LSTM(input_size=input_dim, hidden_size=hidden_dim, num_layers=2, batch_first=True, dropout=0.2)
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


class CNN1DModel(BaseSentinelModel):
    def __init__(self, epochs: int = 5, batch_size: int = 64):
        super().__init__(model_name="1D-CNN", model_type="DeepLearning")
        self.epochs = epochs
        self.batch_size = batch_size
        if HAS_TORCH:
            self.net = None
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if HAS_TORCH:
            num_classes = len(np.unique(y))
            input_dim = X.shape[1]
            self.net = CNN1DNet(input_dim, num_classes).to(self.device)
            dataset = TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long))
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


class LSTMModel(BaseSentinelModel):
    def __init__(self, epochs: int = 5, batch_size: int = 64):
        super().__init__(model_name="LSTM", model_type="DeepLearning")
        self.epochs = epochs
        self.batch_size = batch_size
        if HAS_TORCH:
            self.net = None
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.model = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=200, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if HAS_TORCH:
            num_classes = len(np.unique(y))
            input_dim = X.shape[1]
            self.net = LSTMNet(input_dim, num_classes).to(self.device)
            dataset = TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long))
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


class AutoencoderModel(BaseSentinelModel):
    def __init__(self, epochs: int = 5, batch_size: int = 64, threshold: float = 0.05):
        super().__init__(model_name="Autoencoder", model_type="DeepLearning")
        self.epochs = epochs
        self.batch_size = batch_size
        self.threshold = threshold
        self.num_classes = 15
        if HAS_TORCH:
            self.net = None
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.model = IsolationForest(contamination=0.1, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.num_classes = len(np.unique(y))
        if HAS_TORCH:
            input_dim = X.shape[1]
            self.net = AutoencoderNet(input_dim).to(self.device)
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
        An Autoencoder based on reconstruction error does not naturally output calibrated class probabilities.
        Returns None to ensure no fake/fabricated probability estimation is returned.
        """
        return None
