import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Load dataset from CSV file
def load_data(csv_file):
    df = pd.read_csv(csv_file)
    X = df.drop(columns=["cortisol"])
    y = df["cortisol"]
    return X, y

# Load dataset
csv_file = "sensor_data.csv"  # Change this to your actual file
X, y = load_data(csv_file)

# Check for missing values
if X.isnull().sum().sum() > 0:
    X.fillna(X.mean(), inplace=True)  # Replace NaNs with mean values

# Standardize data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, "scaler.pkl")

# Convert to PyTorch tensors
X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
y_tensor = torch.tensor(y.values, dtype=torch.float32).view(-1, 1)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=42)

# Use DataLoader for mini-batch training
train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define an advanced deep learning model
class AdvancedCortisolPredictor(nn.Module):
    def __init__(self, input_dim):
        super(AdvancedCortisolPredictor, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.bn1 = nn.BatchNorm1d(128)
        self.fc2 = nn.Linear(128, 64)
        self.bn2 = nn.BatchNorm1d(64)
        self.fc3 = nn.Linear(64, 32)
        self.bn3 = nn.BatchNorm1d(32)
        self.fc4 = nn.Linear(32, 16)
        self.fc5 = nn.Linear(16, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)  # Prevents overfitting

    def forward(self, x):
        x = self.relu(self.bn1(self.fc1(x)))
        x = self.dropout(x)
        x = self.relu(self.bn2(self.fc2(x)))
        x = self.dropout(x)
        x = self.relu(self.bn3(self.fc3(x)))
        x = self.dropout(x)
        x = self.relu(self.fc4(x))
        x = self.fc5(x)  # No activation for regression
        return x

# Initialize model, loss, and optimizer
model = AdvancedCortisolPredictor(X_train.shape[1]).to(device)
criterion = nn.MSELoss()
optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-5)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=5, verbose=True)

# Training function with early stopping
def train_model(epochs=100, patience=10):
    best_loss = float("inf")
    patience_counter = 0

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        epoch_loss /= len(train_loader)
        scheduler.step(epoch_loss)

        # Check for early stopping
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            patience_counter = 0
            torch.save(model.state_dict(), "best_cortisol_model.pth")  # Save best model
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}!")
                break

        if epoch % 10 == 0:
            print(f"Epoch {epoch}/{epochs}, Loss: {epoch_loss:.4f}")


# Load the best model
model.load_state_dict(torch.load("best_cortisol_model.pth"))
model.eval()

# Evaluate the model
def evaluate():
    model.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            predictions = model(batch_X).cpu().numpy()
            y_pred.extend(predictions)
            y_true.extend(batch_y.cpu().numpy())

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    print(f"Test MSE: {mse:.4f}")
    print(f"Test RMSE: {rmse:.4f}")
    print(f"Test MAE: {mae:.4f}")
    print(f"Test R² Score: {r2:.4f}")

# Function to predict cortisol for a single input
def predict_single(sample):
    model.eval()
    sample = torch.tensor(scaler.transform([sample]), dtype=torch.float32).to(device)
    with torch.no_grad():
        prediction = model(sample).item()
    print(f"Predicted cortisol level: {prediction:.2f}")

def train_and_eval():
    train_model()
    evaluate()
    sample_input = X.iloc[0].tolist()  # Using first row as a sample input
    predict_single(sample_input)

#train_and_eval()