# Der-Browser
Hi! This browser was made by AI! (Yeah, I'm lazy.) So, how to start it? Instructions:
Check for Python:

Press the WIN + R key combination, type cmd, and click OK to open the command prompt.

In the opened window, enter the command:

python --version
or
py --version
If you see a version number (for example, Python 3.11.5), then Python is installed. Proceed to Step 2.

If the message "python" is not an internal or external command appears, then Python is not installed or added to the PATH variable.
Install Python (if necessary):

Download the latest version of Python from the official website.
Attention! During the installation, be sure to check the box "Add Python to PATH" (Add Python to PATH). This is a critical step.

 Complete the installation and restart the command line (cmd). Re-run the command python --version.
2. Installing the required libraries
The browser requires the PyQt5 and PyQtWebEngine modules to work.

 Open the command line (WIN + R → cmd → OK).
Enter the following command and press Enter:

pip install PyQt5 PyQtWebEngine

For Russian people:
Привет! Этот браузер был создан компанией AI! (Да, я ленив.) Итак, как его запустить? Инструкции:
Проверьте наличие Python:

Нажмите комбинацию клавиш WIN + R, введите cmd и нажмите OK, чтобы открыть командную строку.

В открывшемся окне введите команду:

python --version
или
py --version
Если вы видите номер версии (например, Python 3.11.5), значит, Python установлен. Переходите к Шагу 2.

Если появляется сообщение "python" не является внутренней или внешней командой..., значит, Python не установлен или не добавлен в переменную PATH.
Установите Python (если необходимо):

Скачайте последнюю версию Python с официального сайта.
Внимание! Во время установки обязательно отметьте галочку "Add Python to PATH" (Добавить Python в PATH). Это критически важный шаг.

Завершите установку и перезапустите командную строку (cmd). Снова выполните проверку командой python --version.
2. Установка необходимых библиотек
Для работы браузера требуются модули PyQt5 и PyQtWebEngine.

Откройте командную строку (WIN + R → cmd → OK).
Введите следующую команду и нажмите Enter:

pip install PyQt5 PyQtWebEngine
Примечание для пользователей с несколькими версиями Python: Если команда pip не сработала или связана с другой версией, используйте:
pip3 install PyQt5 PyQtWebEngine
или явно укажите Python:
python -m pip install PyQt5 PyQtWebEngine
Дождитесь окончания загрузки и установки всех компонентов. Процесс может занять несколько минут.

3. Запуск браузера
Найдите в папке с браузером файл FastStart.bat.

Запустите его двойным кликом.
Подождите несколько секунд — откроется главное окно браузера.

!Напоминание!
Не закрывайте окно командной строки (черное окно FastStart.bat), которое появится после запуска! Оно управляет работой браузера.
Закрытие этого окна приведет к немедленному завершению работы браузера. Чтобы корректно закрыть браузер, используйте стандартный крестик в его основном окне.
