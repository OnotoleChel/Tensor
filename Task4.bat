#В системе зарегистрировано и запущено несколько systemd юнитов с именем "foobar-название_сервиса". Каждый запускает определенный сервис. В каждом юните есть параметр с рабочей директорией вида: 
#WorkingDirectory=/opt/misc/название_сервиса
#и параметр ExecStart вида
#ExecStart=/opt/misc/название_сервиса/foobar-daemon произвольные_параметры
#Написать скрипт который получит список юнитов с таким именем поочередно их остановит, перенесет файлы сервиса из  /opt/misc/название_сервиса в /srv/data/название_сервиса, поправит пути в параметрах WorkingDirectory и ExecStart и запустит эти юниты


#!/bin/bash

# Проверка, запущен ли скрипт от root
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен запускаться от root"
   exit 1
fi

# Получаем список юнитов
units=$(systemctl list-units --full --no-legend 'foobar-*' | awk '{print $1}')

for unit in $units; do
    echo "Обработка юнита: $unit"
    
    # Извлекаем название сервиса
    service_name="${unit#foobar-}"
    service_name="${service_name%.service}"
    
    # Пути
    src_dir="/opt/misc/$service_name"
    dest_dir="/srv/data/$service_name"
    
    # Останавливаем юнит
    systemctl stop "$unit"
    if [ $? -ne 0 ]; then
        echo "Ошибка остановки юнита $unit"
        exit 1
    fi
    
    # Проверяем существование исходной директории
    if [ ! -d "$src_dir" ]; then
        echo "Исходная директория $src_dir не существует"
        exit 1
    fi
    
    # Создаем целевую директорию
    mkdir -p "$dest_dir"
    
    # Переносим файлы
    rsync -a --remove-source "$src_dir"/ "$dest_dir/" || { echo "Ошибка копирования файлов из $src_dir в $dest_dir"; exit 1; }
    
    # Получаем путь к конфигурационному файлу
    config_file=$(systemctl show -p FragmentPath "$unit" | cut -d= -f2)
    
    if [ ! -f "$config_file" ]; then
        echo "Файл конфигурации $config_file не найден"
        exit 1
    fi
    
    # Резервная копия конфига
    cp "$config_file" "$config_file.bak"
    
    # Замена путей в конфиге
    old_path="$src_dir"
    new_path="$dest_dir"
    
    # Замена WorkingDirectory
    sed -i "s|^WorkingDirectory=$old_path$|WorkingDirectory=$new_path|" "$config_file"
    # Замена ExecStart
    sed -i "s|^ExecStart=$old_path/foobar-daemon |ExecStart=$new_path/foobar-daemon |" "$config_file"
    
    # Перезагружаем systemd
    systemctl daemon-reload
    
    # Запускаем юнит
    systemctl start "$unit"
    if [ $? -ne 0 ]; then
        echo "Ошибка запуска юнита $unit. Восстанавливаю конфиг из резервной копии..."
        cp "$config_file.bak" "$config_file"
        systemctl daemon-reload
        exit 1
    fi
    
    # Удаляем резервную копию, если все прошло успешно
    rm -f "$config_file.bak"
    
    echo "Юнит $unit обработан успешно"
done

echo "Все юниты обработаны"