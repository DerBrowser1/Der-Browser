# Der-Browser
Hi! This browser was created by AI! (Yes, I'm lazy.) So, how do I launch it? Instructions: Check for Python:

Press the WIN +R key combination, type cmd and press OK to open the command prompt.

In the window that opens, enter the command:

python --version or py --version If you see the version number (for example, Python 3.11.5), it means Python is installed. Go to Step 2.

If the message "python" appears, it is not an internal or external command..., it means that Python is not installed or added to the PATH variable. Install Python (if necessary):

Download the latest version of Python from the official website. Attention! During installation, make sure to check the box "Add Python to PATH". This is a critical step.

Complete the installation and restart the command prompt (cmd). Run the check again with the python --version command. 2. Installing the necessary libraries The PyQt5 and PyQtWebEngine modules are required for the browser to work.

Open the command prompt (WIN + R → cmd → OK). Enter the following command and press Enter:

pip install PyQt5 PyQtWebEngine 
Note for users with multiple versions of Python: If the pip command did not work or is linked to another version, use: pip3 install PyQt5 PyQtWebEngine or explicitly specify Python: 
python -m pip install PyQt5 PyQtWebEngine 
Wait until all components are downloaded and installed. The process may take several minutes.

Launching the browser, find the FastStart.bat file in the browser folder.
Launch it with a double click. Wait a few seconds to open the main browser window.

!A reminder! Do not close the command prompt window (the black FastStart.bat window) that appears after startup! It controls the operation of the browser. Closing this window will immediately shut down the browser. To close the browser correctly, use the standard x in its main window.

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
