from abc import abstractmethod
from typing import Any, Optional
from base.specialized import BaseSpecializedHandler
from threading import Thread as Event


class BaseIoInterface(BaseSpecializedHandler):
    """
    Базовый класс аксессоров интерфейсов
    последовательной передачи данных

    Args:
        *args (Any): Позиционные аргументы модуля
        **kwargs (Any): Именованные аргументы модуля
    """

    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any):
        self.is_open = False  # Интерфейс пока не открыт

        self._event: Optional[Event]  # Указываем аннотацию типа для ивента

        self._timeout = None  # Таймаут пока не установлен

        BaseSpecializedHandler.__init__(self)  # Инициализируем базовый класс


    @abstractmethod
    def fileno(self) -> int:
        """
        Получение дескриптора интерфейса

        Returns:
            int: Файловый дескриптор интерфейса
        """


    @property
    def event(self) -> Optional[Event]:
        """
        Получение внутреннего ивента, через активацию которого
        можно инициировать пробуждение аксессора

        Returns:
            Optional[Event]:
                Ивент для пробуждения процесса, если допустим для класса
        """

        return self._event  # Возвращаем внутренний ивент


    @event.setter
    @abstractmethod
    def event(self, event: Event):
        """
        Установка внешнего ивента для пробуждения процесса
        из другого процесса

        Args:
            event (Event): Внешний ивент с автоматическим сбросом
        """


    @property
    def timeout(self) -> Optional[float]:
        """
        Получение текущего установленного таймаута на ожидание данных.
        По умолчанию не установлен

        Returns:
            Optional[float]:
                Таймаут в секундах (`None` - бесконечное ожидание)
        """

        return self._timeout  # Возвращаем текущий установленный таймаут на ожидание данных


    @timeout.setter
    def timeout(self, timeout: Optional[float] = None):
        """
        Установка таймаута на ожидание. По умолчанию не установлен

        Args:
            timeout (Optional[float]):
                Таймаут в секундах (`None` - бесконечное ожидание)
        """

        self._timeout = timeout  # Устанавливаем новый таймаут на ожидание


    @abstractmethod
    def run(self):
        """
        Запуск работы класса, осуществление подключения
        """

        self.is_open = True  # Устанавливаем флаг того что интерфейс открыт

        BaseSpecializedHandler.run(self)  # Устанавливаем флаг на запуск


    @property
    @abstractmethod
    def in_waiting(self) -> int:
        """
        Получение количества байт, доступного для чтения

        Returns:
            int: Количество байт, доступное для чтения
        """


    @abstractmethod
    def write(self, data: bytes):
        """
        Установка данных на отправку на интерфейс вывода

        Args:
            data (bytes): Данные для отправки
        """


    def inWaiting(self) -> int:
        """
        Возвращает количество байт, ожидающих в буфере

        Returns:
            int: Количество байт, ожидающих в буфере
        """

        return self.in_waiting


    @abstractmethod
    def _wait_for_event(self) -> bool:
        """
        Ожидание события от интерфейса или внешнего события

        Returns:
            bool:
                - `True` - если пришёл ивент на получение данных
                - `False` - если произошла активация внешнего ивента
        """


    @abstractmethod
    def _read(self, size: int) -> bytes:
        """
        Чтение указанного количества байт из буфера интерфейса

        Args:
            size (int): Количество байт для чтения
        Returns:
            bytes: Прочитанные данные в виде байтов
        """


    def read(self, size: int = 1) -> bytes:
        """
        Блокирующее чтение указанного количества байт.
        Будет ждать, пока не получит >= байт, чем указано

        Args:
            size (int):
                Количество байт, необходимых к прочтению
                (всегда должно быть > 0)
        Returns:
            bytes:
                Необходимое количество байт.
                - `>= size` - по умолчанию
                - Пустой набор байт, если активация внешнего ивента
        """

        while True:
            if self.in_waiting >= size:
                return self._read(size)
            if not self._wait_for_event():
                return b""  # Возвращаем пустые байты по завершении работы


    @abstractmethod
    def close(self):
        """
        Закрытие порта, завершение работы
        """

        self.is_open = False  # Устанавливаем флаг того, что интерфейс закрыт

        BaseSpecializedHandler.close(self)  # Устанавливаем флаг завершения работы