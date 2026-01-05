ID = "tensorflow_adapter"
TITLE = "TensorFlow tensor"
TAGS = ["tensorflow", "tensor"]
REQUIRES = ['tensorflow']
DISPLAY_INPUT = "tf.constant([1.0, 2.0])"
EXPECTED = "A TensorFlow tensor with shape (2,)."


def build():
    import tensorflow as tf

    return tf.constant([1.0, 2.0])
