# Astra-IDE
Упрощённый вариант python. Написан на python. Пока что только русский язык доступен ONLY RU.
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>

<div class="card">
<h1>🪐 Astra IDE — Полный Гайд</h1>
<p class="small">Документация по Astra, IDE, AstraWindow, сборке в .exe/.msi и советам. Можно читать прямо в браузере.</p>
</div>

<div class="card" id="intro">
<h2>Что такое Astra IDE</h2>
<p>Astra IDE — это интегрированная среда разработки для языка <strong>Astra</strong>. Поддерживает:</p>
<ul>
<li>Редактор кода с подсветкой синтаксиса</li>
<li>Интерпретатор языка Astra</li>
<li>GUI-библиотеку <strong>AstraWindow</strong></li>
<li>Сборку в .exe и .msi</li>
<li>Отладку с Debug Output</li>
</ul>
</div>

<a class="button-download" href="https://example.com/AstraIDE.zip" download>
    Скачать Astra IDE
</a>
</div>

<div class="card" id="structure">
<h2>Структура проекта</h2>
<pre><code>project/
├─ main.ast
├─ libs/
│   └─ AstraWindow.py
├─ icons/
├─ examples/
└─ build_settings.json</code></pre>
<p class="small">.ast — код на языке Astra, libs — дополнительные библиотеки, например AstraWindow.</p>
</div>

<div class="card" id="editor">
<h2>Интерфейс IDE</h2>
<ul>
<li>Редактор кода с подсветкой</li>
<li>Проводник проекта (папки/файлы)</li>
<li>Кнопки: Run / Stop / Save / Guide / Build</li>
<li>Debug Output — лог выполнения</li>
<li>Подсказки по командам внизу</li>
</ul>
</div>

<div class="card" id="files">
<h2>Работа с файлами .ast</h2>
<ul>
<li>Создать файл — кнопка <em>Создать файл</em></li>
<li>Открыть файл — двойной клик в проводнике</li>
<li>Сохранить — кнопка <em>Save</em> или Ctrl+S</li>
</ul>
</div>

<div class="card" id="syntax">
<h2>Язык Astra — Полный синтаксис</h2>

<h3>Переменные</h3>
<pre><code>TEXTVAR name, value       ; создание переменной
UPDATEVAR name, valueOrVar ; обновление</code></pre>

<h3>Математика</h3>
<pre><code>ADD var, number    ; прибавить
SUB var, number    ; вычесть
MOV var, numberOrVar ; присвоить значение</code></pre>

<h3>Вывод</h3>
<pre><code>PRINT expression</code></pre>

<h3>Условия</h3>
<pre><code>IF a == b THEN
  ...
}
ELIF a == c THEN
  ...
}
ELSE
  ...
}</code></pre>

<h3>Циклы</h3>
<pre><code>WHILE a != b
  ...
}
FOR item IN 1,2,3
  ...
}</code></pre>

<h3>Функции</h3>
<pre><code>FUNCTION name
  ...
}
name ; вызов функции</code></pre>

<h3>Исключения</h3>
<pre><code>TRY
  ...
EXCEPT
  ...
}</code></pre>

<h3>Библиотеки</h3>
<pre><code>USE AstraWindow</code></pre>
</div>

<div class="card" id="examples">
<h2>Примеры кода</h2>

<h3>Простой Clicker</h3>
<pre class="example"><code>USE AstraWindow
TEXTVAR score,0
FUNCTION onClick
  ADD score,1
  PRINT score
}
WINDOW main,320,200,"Clicker"
TEXT main,10,10,"Score:"
TEXT main,70,10,score
BUTTON main,10,40,"Click",onClick</code></pre>

<h3>Таймер</h3>
<pre class="example"><code>TEXTVAR timer,10
FUNCTION tick
  PRINT timer
  SUB timer,1
}
WHILE timer!=0
  tick
  WAIT 1
}</code></pre>

<h3>Скрытие/показ элементов</h3>
<pre class="example"><code>TEXT main,20,20,"Привет",16,"blue","yellow",true
BUTTON main,20,60,"Click",updateScore,14,"white","green",true
SQUARE main,100,100,50,"red",true
TEXT main,20,120,"Скрытый текст",12,"black",None,false</code></pre>

</div>

<div class="card" id="astrawindow">
<h2>AstraWindow — GUI библиотека</h2>
<p>После <code>USE AstraWindow</code> доступны команды:</p>
<ul>
<li><strong>WINDOW</strong> — создание окна</li>
<li><strong>TEXT</strong> — текст с настройкой шрифта, цвета, фона и видимости</li>
<li><strong>BUTTON</strong> — кнопка с шрифтом, цветом текста, фоном и видимостью</li>
<li><strong>SQUARE</strong> — квадрат с цветом и видимостью</li>
</ul>

<h3>Пример команды TEXT</h3>
<pre><code>TEXT main,20,20,"Привет",16,"blue","yellow",true</code></pre>

<h3>Пример команды BUTTON</h3>
<pre><code>BUTTON main,20,60,"Click Me",onClick,14,"white","green",true</code></pre>

<h3>Пример команды SQUARE</h3>
<pre><code>SQUARE main,100,100,50,"red",true</code></pre>
</div>

<div class="card" id="build">
<h2>Сборка</h2>
<h3>.exe (PyInstaller)</h3>
<pre><code>pyinstaller --onefile --windowed --add-data "icons;icons" astra_ide.py</code></pre>
<h3>.msi (pynsist / NSIS)</h3>
<p>Используйте pynsist для сборки MSI. Настройте entry_point и добавьте папку dist в конфиг.</p>
</div>

<div class="card" id="build-settings">
<h2>Настройки сборки</h2>
<p>Через окно настроек IDE можно задать:</p>
<ul>
<li>Имя проекта</li>
<li>Версию</li>
<li>Файлы и папки для включения</li>
<li>Список пакетов</li>
</ul>
<p class="small">Сохраняется в <code>build_settings.json</code></p>
</div>

<div class="card" id="tips">
<h2>Советы и трюки</h2>
<ul>
<li>Используйте <code>PRINT</code> для отладки</li>
<li>Закрывайте блоки фигурной скобкой <code>}</code></li>
<li>Имена функций и переменных чувствительны к регистру</li>
<li>GUI-команды (WINDOW/TEXT/BUTTON) выполняйте после USE AstraWindow</li>
</ul>
</div>

<nav>
<div class="card">
<h3>Навигация</h3>
<ul>
<li><a href="#intro">Intro</a></li>
<li><a href="#structure">Структура</a></li>
<li><a href="#syntax">Синтаксис</a></li>
<li><a href="#examples">Примеры</a></li>
<li><a href="#astrawindow">AstraWindow</a></li>
<li><a href="#build">Сборка</a></li>
<li><a href="#build-settings">Настройки сборки</a></li>
<li><a href="#tips">Советы</a></li>
</ul>
</div>
</nav>

</body>
</html>
