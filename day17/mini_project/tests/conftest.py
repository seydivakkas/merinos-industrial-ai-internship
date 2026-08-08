"""
Pytest konfigürasyonu ve scikit-learn uyumluluk yaması.
"""
import inspect
from sklearn.linear_model import LogisticRegression

# Scikit-learn >= 1.5 multi_class uyumluluk yaması
_orig_lr_init = LogisticRegression.__init__
_sig = inspect.signature(_orig_lr_init)
if "multi_class" not in _sig.parameters:
    def _compat_lr_init(self, *args, **kwargs):
        kwargs.pop("multi_class", None)
        return _orig_lr_init(self, *args, **kwargs)
    _compat_lr_init.__signature__ = _sig
    LogisticRegression.__init__ = _compat_lr_init
