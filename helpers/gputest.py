import torch

# Проверить доступность CUDA
print(torch.cuda.is_available())

# Получить количество GPU
print(torch.cuda.device_count())

# Получить имя GPU
print(torch.cuda.get_device_name())
