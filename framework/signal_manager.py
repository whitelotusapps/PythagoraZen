import inspect
import logging

from PyQt5.QtCore import QObject, pyqtSignal

from framework.logging_handler import PythagoraZenLogger

pythagorazen_logger = PythagoraZenLogger()
pythagorazen_logger.configure_logging()


class SignalManager(QObject):
    instance_created = pyqtSignal(object, str)

    _instance = None

    def __new__(cls):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        if cls._instance is None:
            cls._instance = super(SignalManager, cls).__new__(cls)
            cls._instance.__init__()  # Explicitly call __init__ of the base class
            # cls._instance.pythagorazen_logger = PythagoraZenLogger()
            # cls._instance.pythagorazen_logger.configure_logging()
            cls._instance.instances = {}
            cls._instance.instance_created.connect(cls._instance.on_instance_created)
        return cls._instance

    def __init__(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        super(SignalManager, self).__init__()

    def on_instance_created(self, instance):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        class_name = instance.__class__.__name__
        identifier = f"{class_name}_{len(self.instances.get(class_name, []))}"
        self.register_instance(instance, identifier)

    def register_instance(self, instance, identifier):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        class_name = instance.__class__.__name__

        logging.debug("register_instance method called")
        logging.debug(f"instance  : {instance}")
        logging.debug(f"class_name: {class_name}")
        logging.debug(f"identifier: {identifier}")

        if class_name not in self.instances:
            self.instances[class_name] = {}

        if identifier in self.instances[class_name]:
            logging.warning(
                f"Warning: Instance with identifier {identifier} already exists for {class_name}. "
                f"Choosing a different identifier might be a good idea."
            )
        self.instances[class_name][identifier] = instance
        self.instance_created.emit(instance)

    def connect_instances(
        self,
        sender_instance,
        sender_name,
        signal_name,
        receiver_instance,
        receiver_name,
        slot_name,
    ):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        logging.debug(f"sender_instance   : {sender_instance}")
        logging.debug(f"sender_name       : {sender_name}")
        logging.debug(f"signal_name       : {signal_name}")
        logging.debug(f"receiver_instance : {receiver_instance}")
        logging.debug(f"receiver_name     : {receiver_name}")
        logging.debug(f"slot_name         : {slot_name}")

        sender_signal = getattr(sender_instance, signal_name)
        receiver_slot = getattr(receiver_instance, slot_name)

        logging.debug(f"sender_signal     : {sender_signal}")
        logging.debug(f"receiver_slot     : {receiver_slot}")

        if sender_signal is not None and receiver_slot is not None:
            sender_signal.connect(receiver_slot)
        else:
            logging.error("Invalid signal or slot.")
