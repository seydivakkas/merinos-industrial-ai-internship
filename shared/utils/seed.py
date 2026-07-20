"""
shared/utils/seed.py
Deterministik deneyler ve tekrarlanabilirlik için global rastgelelik sabitleyici.
"""

import os
import random
import numpy as np


def seed_everything(seed: int = 42) -> int:
    """
    Tüm rastgelelik üreteçlerini deterministik bir çekirdek (seed) ile sabitler.
    
    Args:
        seed: Sabitleme için kullanılacak tamsayı çekirdek değeri (varsayılan: 42)
        
    Returns:
        Kullanılan seed değeri
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)

    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

    return seed
