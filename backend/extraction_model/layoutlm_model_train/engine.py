import torch
from tqdm import tqdm

def train_fn(dataloader, model, optimizer, device):
    model.train()
    total_loss = 0
    for batch in tqdm(dataloader):
        for k,v in batch.items():
            batch[k] = v.to(device)
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total_loss += loss.item()
    return total_loss / len(dataloader)

def eval_fn(dataloader, model, device):
    model.eval()
    total_loss = 0
    with torch.no_grad():
        for batch in tqdm(dataloader):
            for k,v in batch.items():
                batch[k] = v.to(device)
            outputs = model(**batch)
            total_loss += outputs.loss.item()
    return total_loss / len(dataloader)