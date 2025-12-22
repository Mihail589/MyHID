from abc import abstractmethod
from math import ceil
from typing import TYPE_CHECKING, Dict, List, NamedTuple, Optional, Self, TypeAlias, cast
from threading import Thread as Event
from base_interface import BaseIoInterface
UInt8: TypeAlias = int
DevicesListType: TypeAlias = List[Dict[str, bytes | int | str]]
"""Список свойств обнаруженных Bluetooth Classic устройств"""

if TYPE_CHECKING:
    def hid_enumerate(
            vendor_id: Optional[int] = None,  # pylint: disable=unused-argument
            product_id: Optional[int] = None  # pylint: disable=unused-argument
        ) -> DevicesListType:  # pyright: ignore[reportReturnType]
        """
        Обнаружение всех подключённых HID устройств

        Args:
            vendor_id (Optional[int]): ID производителя
            product_id (Optional[int]): ID продукта
        Returns:
            DevicesListType:
                Список параметров обнаруженных HID устройств
        """
else:
    from hid import enumerate as hid_enumerate

HIR_REPORT_SIZE = 64  # Байтовый размер одного HID отчёта


class HIDDeviceError(Exception):
    """Пользовательское исключение для ошибок HID устройства"""


class HidAttributes(NamedTuple):
    """
    Адрес HID-устройства для подключения

    Attributes:
        vendor_id (int): ID производителя
        product_id (int): ID продукта
        serial_number (Optional[int]): Серийный номер, опционально
    """

    vendor_id: int  # ID производителя
    product_id: int  # ID продукта
    serial_number: Optional[int] = None  # Серийный номер, опционально


class BaseHid(BaseIoInterface):
    """
    Базовый класс аксессоров взаимодействия с устройствами HID
    """

    def __init__(
            self,
            device_address: HidAttributes | str,
            send_report_id: UInt8 = 0,
            use_hidd: bool = False
        ):
        """
        Инициализация аксессора передачи данных
        посредством устройства HID
        
        Args:
            device_address (HidAttributes | str):
                Идентификаторы устройства или путь до устройства
            send_report_id (UInt8):
                ID отчёта по-умолчанию при отправке отчёта
            use_hidd (bool): Использовать ли методы чтения-записи HidD
        Raises:
            RecursionError:
                Если передан объект `HidAttributes`, но не удалось найти
                соответствующее устройство по указанным атрибутам
        """

        self.set_report_id(send_report_id)  # Устанавливаем ID отчёта для отправки отчётов

        # Определяем путь до устройства через атрибуты:
        if isinstance(device_address, HidAttributes):
            device_path = self.get_device_path_by_attributes(device_address)  # Получаем путь до устройства
            if device_path is None:  # Если не удалось найти устройства по переданным атрибутам
                raise RecursionError(f"No Device for attributes {device_address} found")  # Выводим исключение
            self.device_path = device_path  # Устанавливаем путь до устройства
        else:
            self.device_path = device_address.encode()  # Устанавливаем путь до устройства

        self._use_hidd = use_hidd  # Устанавливаем флаг необходимости использования HidD
        if use_hidd:  # Если используем HidD:
            # Подменяем внутренний метод получения данных, на получение из HidD:
            self.recv_report = self.recv_hidd_report
            # Подменяем внутренний метод записи, на запись посредством HidD:
            self._write_report = self._write_hidd_report

        self._self_timeout = None  # Таймаут пока не установлен

        self.buffer = b""  # Внутренний буфер для чтения
        self.device_handle = None  # Дескриптор устройства
        self.input_report_length = HIR_REPORT_SIZE + 1  # Добавляем байт для Report ID
        self.output_report_length = HIR_REPORT_SIZE + 1  # Добавляем байт для Report ID
        self.feature_report_length = HIR_REPORT_SIZE + 1  # Добавляем байт для Report ID

        self._setup_api_functions()  # Настраиваем функции API

        BaseIoInterface.__init__(self)  # Инициализируем базовый класс


    @abstractmethod
    def _setup_api_functions(self):
        """
        Настройка прототипов функций
        """


    @staticmethod
    def get_device_path_by_attributes(hid_attributes: HidAttributes) -> Optional[bytes]:
        """
        Получение пути до устройства через его атрибуты
        
        Args:
            hid_attributes (HidAttributes): Идентификаторы устройства
        Returns:
            Optional[bytes]:
                Файловый путь до устройства, если найдено
                и `None` - если не удалось найти устройство,
                соответствующее необходимым атрибутам
        """

        # Находим устройство под атрибуты:
        hid_devices = hid_enumerate(hid_attributes.vendor_id, hid_attributes.product_id)

        if hid_devices:  # Если хотя бы одно устройство найдено
            if hid_attributes.serial_number is None:  # Если соответствие серийному номеру не требуется
                return cast(bytes, hid_devices[0]["path"])  # Возвращаем первое найденное устройство
            for device in hid_devices:
                if device["serial_number"] == hid_attributes.serial_number:  # Если серийный номер совпал
                    return cast(bytes, device["path"])

        return None  # Возвращаем None как маркер того, что не нашли подходящее устройство


    @staticmethod
    def discover() -> DevicesListType:
        """
        Вывод кортежа всех обнаруженных HID устройств и их характеристик

        Returns:
            DevicesListType:
                Список всех найденных HID устройств и их характеристик
        """

        return hid_enumerate()  # Возвращаем список всех обнаруженных HID устройств


    @classmethod
    def init_by_device_name(
            cls,
            device_name: str,
            send_report_id: UInt8 = 0,
            use_hidd: bool = False
        ) -> Self:
        """
        Инициализация класса через имя HID устройства

        Args:
            device_name (str): Имя HID устройства
            send_report_id (UInt8):
                ID отчёта по-умолчанию при отправке отчёта
            use_hidd (bool): Использовать ли методы чтения-записи HidD
        Returns:
            Self: Инициализированный через имя адаптера, класс
        Raises:
            RuntimeError:
                Если в системе не найдено ни одного HID устройства
                с указанным именем (product_string)
        """

        for device_info in cls.discover():  # Для каждого найденного HID устройства
            if device_info["product_string"] == device_name:  # Если имя устройства совпало
                return cls(
                    device_address = cast(str, device_info["path"]),  # Передаём путь до устройства
                    send_report_id = send_report_id,  # ID отчёта при отправке отчётов
                    use_hidd = use_hidd  # Передаём флаг необходимости использования HidD
                )  # Инициализируем класс и возвращаем

        raise RuntimeError(f"No HID devices with name {device_name} found")  # Вызываем исключение


    def set_report_id(self, send_report_id: UInt8 = 0):
        """
        Установка нового ID отчёта при отправке отчётов

        Args:
            send_report_id (UInt8): ID отчёта для отправки
        """

        self._send_report_id_byte = bytes(send_report_id)  # Устанавливаем новое ID отчёта для отправки


    @abstractmethod
    def _get_capabilities(self):
        """
        Получение возможностей HID устройства
        """


    @abstractmethod
    def _get_device_info(self):
        """
        Получение атрибутов и возможностей устройства
        """


    @abstractmethod
    def _open_path(self, path: bytes):
        """
        Открытие устройства по пути

        Args:
            path (bytes): Путь до устройства
        """


    def fileno(self) -> int:
        """
        Получение дескриптора устройства HID

        Returns:
            int: Файловый дескриптор устройства HID
        """

        return cast(int, self.device_handle)  # Возвращаем файловый дескриптор


    @abstractmethod
    def _init_overleaped(self):
        """
        Инициализация атрибутов для операций асинхронного чтения-записи
        """


    @abstractmethod
    def _init_hidd(self):
        """
        Инициализация атрибутов для операций асинхронного чтения-записи
        через HidD
        """


    def run(self):
        """
        Запуск работы аксессора
        """

        self._open_path(self.device_path)  # Открываем устройство через путь

        if self._use_hidd:  # Если читаем HidD
            self._init_hidd()  # Инициализируем взаимодействие через HidD
        else:
            self._init_overleaped()  # Инициализируем асинхронное чтение-запись

        BaseIoInterface.run(self)  # Устанавливаем флаг на запуск


    def _process_input_data(self, data: bytes) -> bytes:
        """
        Обработка входных данных, опциональное удаление ID отчета

        Args:
            data (bytes): Входные данные
        Returns:
            bytes: Обработанные данные
        """

        if len(data) > 0 and data[0] == 0:
            data = data[1:]

        return data


    @abstractmethod
    def recv_report(self) -> bytes:
        """
        Запуск и осуществление асинхронного чтения
        с использованием ReadFile с OVERLAPPED

        Returns:
            bytes:
                Прочитанные данные отчёта,
                если удалось прочесть синхронно, иначе пустой буфер
        """


    @abstractmethod
    def recv_hidd_report(self) -> bytes:
        """
        Получение данных с использованием HidD_GetInputReport

        Returns:
            bytes: Данные полученного HID отчёта
        """


    @abstractmethod
    def _wait_for_event(self) -> bool:
        """
        Ожидание события от порта или внешнего события

        Returns:
            bool:
                - `True` - если пришёл ивент на получение данных
                - `False` - если произошла активация внешнего ивента
        """


    def receive(self) -> bytes:
        """
        Получение всех доступных данных из буфера.
        Удаляет данные из буфера после чтения

        Returns:
            bytes: Данные в виде байт
        """

        if len(self.buffer) == 0:
            return b""

        data = bytes(self.buffer)
        self.buffer = b""  # Очистка буфера после чтения

        return data


    def _is_report(self) -> bool:
        """
        Поверка, есть ли хотя бы один отчёт в буфере для чтения

        Returns:
            bool:
                Есть ли хотя бы один отчёт в буфере для чтения
        """

        return cast(Event, self._event).is_set()  # Возвращаем флаг того, получены ли данные


    def _receive(self):
        """
        Чтение всех полученных данных во внутренний буфер
        """

        while True:  # Пока отчёты есть в буфере
            data = self.recv_report()  # Читаем данные отчётов
            if not data:  # Если отчёты в буфере закончились
                break  # Выходим из цикла
            self.buffer += data  # Добавляем данные в буфер


    @property
    def in_waiting(self) -> int:
        """
        Возвращает количество байт, ожидающих в буфере

        Returns:
            int: Количество байт, ожидающих в буфере
        """

        self._receive()  # Читаем данные в буфер с помощью HidD, если есть

        return len(self.buffer)  # Возвращаем количество байт в буфере, прочитанных с помощью HidD


    def _read(self, size: int) -> bytes:
        """
        Чтение указанного количества байт из буфера HID

        Args:
            size (int): Количество байт для чтения
        Returns:
            bytes: Прочитанные данные в виде байтов
        """

        data = self.buffer[:size]  # Чтение данных из буфера
        self.buffer = self.buffer[size:]  # Удаление прочитанных данных

        return bytes(data)  # Возвращаем прочитанные данные


    def _prepare_output_buffer(self, data: bytes) -> bytes:
        """
        Подготовка выходного буфера с правильной длиной

        Args:
            data (bytes): Исходные данные
        Returns:
            bytes: Подготовленный буфер
        """

        return self._send_report_id_byte + data + b'\x00' * (self.output_report_length - len(data))


    @abstractmethod
    def _write_report(self, data: bytes):
        """
        Запись с использованием WriteFile с OVERLAPPED

        Args:
            data (bytes):
                Данные для записи (len(data) <= размеру отчёта)
        """


    @abstractmethod
    def _write_hidd_report(self, data: bytes):
        """
        Запись с использованием HidD_SetOutputReport

        Args:
            data (bytes):
                Данные для записи (len(data) <= размеру отчёта)
        """


    def write(self, data: bytes):
        """
        Запись данных в HID устройство
        (неблокирующее через OVERLAPPED + wait)

        Args:
            data (bytes): Данные для записи
        """

        for i in range(ceil(len(data) / self.output_report_length)):  # Разбиваем на отдельный отчёты
            report_start = i * self.output_report_length  # Индекс начала нового отчёта
            self._write_report(data[report_start: report_start + self.output_report_length])  # Записываем отчёт на HID


    @abstractmethod
    def close(self):
        """
        Завершение работы аксессора
        """

        BaseIoInterface.close(self)  # Устанавливаем флаг на завершение работы