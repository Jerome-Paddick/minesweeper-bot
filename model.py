import tensorflow as tf

_model = None
_classnames = None

def get_model():
    global _model, _classnames

    if _model is None:
        _model = tf.keras.models.load_model('simple_classifier.h5')

    if _classnames is None:
        with open('class_names.txt', 'r') as f:
            _classnames = f.read().splitlines()

    return _model, _classnames
