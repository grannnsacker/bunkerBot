def get_profile_text(user):
    return f'''
👤 {user.username}\n
<b>Кошелек</b>
💰 Крышечки: 30
🥒 Изумруды: 0\n

<b>Инвентарь</b>
♻ Смена характеристики: 0
📚 Книги: 0
'''


def get_me_text(player):
    return f'''
<b>Пол:</b> {player.sex}
<b>Возраст:</b>{player.age}
<b>Профессия:</b> {player.job}
<b>Хобби:</b> {player.hobby}
<b>Фобия:</b> {player.fear}
<b>Багаж:</b> {player.luggage}
<b>Характер:</b> {player.personality}
<b>Здоровье:</b> {player.health}
<b>Доп. информация:</b> {player.add_inf}
<b>Знание:</b> {player.knowledge}
<b>Карточка действий:</b> {player.card_1.split('!')[1]}
<b>Карточка условий:</b> {player.card_2}'''


def get_apocalypses_and_bunker_text(game):
    return f'''
<b>(АПОКАЛИПСИС)\n{game.disaster}</b>

<b>(ИНФОРМАЦИЯ О БУНКЕРЕ)
Площадь:</b> {game.size}
<b>Вместимость:</b> {len(game.players) // 2} чел.
<b>Время нахождения:</b> {game.time_spent}
<b>Общее состояние:</b> {game.condition}
<b>Предназначение:</b> {game.build_reason}
<b>Расположение:</b> {game.location}
<b>Помещения:</b>
• {game.room_1}
• {game.room_2}
• {game.room_3}
<b>Доступные ресурсы:</b>
• {game.available_resource_1}
• {game.available_resource_2}
'''


def get_bunker_text(game):
    return f'''
<b>Площадь:</b> {game.size}
<b>Вместимость:</b> {len(game.players) // 2} чел.
<b>Время нахождения:</b> {game.time_spent}
<b>Общее состояние:</b> {game.condition}
<b>Предназначение:</b> {game.build_reason}
<b>Расположение:</b> {game.location}
<b>Помещения:</b>
• {game.room_1}
• {game.room_2}
• {game.room_3}
<b>Доступные ресурсы:</b>
• {game.available_resource_1}
• {game.available_resource_2}
'''


def get_apocalypses_text(game):
    return f'''
    
    '''